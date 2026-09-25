"""Request-scoped caching for "does this lemma have a matching stem" checks.

The frontend used to answer this question per-lemma with a dedicated
`hasStem` GraphQL query, causing one HTTP round trip per stem shown in a
dict article. This module lets a resolver that already knows which lemmas
it is about to return (e.g. `dicts.schema.resolve_dict_entry_list`) look up
all of them in a single indexed Stem query and cache the result on the
GraphQL request, so that `LemmaType.resolve_has_stem` can answer instantly
without any additional queries, network round trips.
"""

from mongoengine.queryset.visitor import Q

from .models import Stem


def _cache_key(src_langs, target_langs, wanted_dicts):
    return (
        tuple(sorted(src_langs)),
        tuple(sorted(target_langs)),
        tuple(sorted(wanted_dicts)),
    )


def _get_cache(info):
    cache = getattr(info.context, "_has_stem_cache", None)
    if cache is None:
        cache = {}
        info.context._has_stem_cache = cache
    return cache


def preload_has_stem(info, lemmas, src_langs, target_langs, wanted_dicts):
    """Look up which of `lemmas` have a matching Stem in a single query.

    The result is cached on `info.context`, keyed by the (sorted) language
    and dict filters, so later `has_stem` calls for the same filters and
    request reuse it instead of issuing another query.
    """
    if not lemmas:
        return

    key = _cache_key(src_langs, target_langs, wanted_dicts)
    cache = _get_cache(info)

    combined_filter = (
        Q(stem__in=list(set(lemmas)))
        & Q(srclangs__in=src_langs)
        & Q(targetlangs__in=target_langs)
        & Q(dicts__in=wanted_dicts)
    )
    existing = cache.setdefault(key, set())
    existing.update(Stem.objects(combined_filter).distinct("stem"))


def has_stem(info, lemma, src_langs, target_langs, wanted_dicts):
    """Return whether `lemma` has a matching Stem for the given filters.

    Uses the cache populated by `preload_has_stem` when available, falling
    back to a direct (still indexed) query otherwise.
    """
    key = _cache_key(src_langs, target_langs, wanted_dicts)
    cache = _get_cache(info)

    if key not in cache:
        preload_has_stem(info, [lemma], src_langs, target_langs, wanted_dicts)

    return lemma in cache[key]
