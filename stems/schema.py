"""Queries for stem models."""

import logging
from functools import lru_cache

import graphene
from graphene import relay
from mongoengine.queryset.visitor import Q

from .models import Stem
from .types import StemType

LOGGER = logging.getLogger(__name__)


def get_search_filter(mode, search):
    """
    Build the search filter for the given mode.

    `search_stem` is always stored lowercased, so the incoming `search` is
    expected to already be lowercased (see `resolve_stem_list`). Using
    case-sensitive regex operators (as opposed to the case-insensitive
    `istartswith`/`icontains`/`iendswith` variants) lets MongoDB use the
    `search_stem` index to do an actual range-seek for the (most common)
    "start" mode, instead of scanning every document in the collection.
    """
    if mode == "middle":
        return Q(search_stem__contains=search)

    if mode == "end":
        return Q(search_stem__endswith=search)

    return Q(search_stem__startswith=search)


@lru_cache(maxsize=128)
def _cached_stem_query(
    search, mode, src_langs_tuple, target_langs_tuple, wanted_dicts_tuple
):
    """
    Cached stem query function with LRU cache.

    This caches the database query results for significant performance improvement
    on repeated searches. Returns a list of stems for the given parameters.
    """
    LOGGER.debug(f"Cache miss - executing database query for: {search} ({mode})")

    # Build compound filter combining all conditions at database level
    search_filter = get_search_filter(mode, search)
    src_lang_filter = Q(srclangs__in=list(src_langs_tuple))
    target_lang_filter = Q(targetlangs__in=list(target_langs_tuple))
    dict_filter = Q(dicts__in=list(wanted_dicts_tuple))

    # Combine all filters for single efficient database query
    combined_filter = search_filter & src_lang_filter & target_lang_filter & dict_filter

    # Execute optimized query with database-level sorting
    stems = list(Stem.objects(combined_filter).order_by("search_stem"))

    LOGGER.debug(f"Database query returned {len(stems)} stems")
    return stems


class StemConnection(relay.Connection):
    class Meta:
        node = StemType

    total_count = graphene.Int()

    def resolve_total_count(self, info):
        return len(self.iterable)


class Query(graphene.ObjectType):
    stem_list = graphene.ConnectionField(
        StemConnection,
        search=graphene.String(required=True),
        mode=graphene.String(required=True),
        src_langs=graphene.List(graphene.String, required=True),
        target_langs=graphene.List(graphene.String, required=True),
        wanted_dicts=graphene.List(graphene.String, required=True),
    )
    has_stem = graphene.List(
        StemType,
        exact=graphene.String(required=True),
        src_langs=graphene.List(graphene.String, required=True),
        target_langs=graphene.List(graphene.String, required=True),
        wanted_dicts=graphene.List(graphene.String, required=True),
    )

    def resolve_has_stem(self, info, exact, **kwargs):
        combined_filter = (
            Q(stem=exact)
            & Q(srclangs__in=kwargs["src_langs"])
            & Q(targetlangs__in=kwargs["target_langs"])
            & Q(dicts__in=kwargs["wanted_dicts"])
        )

        return Stem.objects(combined_filter)

    def resolve_stem_list(self, info, search, **kwargs):
        """
        Optimized resolver with LRU caching.

        This resolver uses LRU caching to dramatically improve performance
        on repeated queries while maintaining full GraphQL connection support.
        """
        if not search:
            return Stem.objects.none()

        # Lowercase up front: search_stem is always stored lowercased, so this
        # keeps matching correct for case-sensitive filters (see
        # get_search_filter) and improves the LRU cache hit rate for
        # differently-cased repeats of the same search.
        search = search.lower()

        # Convert lists to sorted tuples for cache key consistency
        cached_results = _cached_stem_query(
            search,
            mode=kwargs.get("mode", "start"),
            src_langs_tuple=tuple(sorted(kwargs["src_langs"])),
            target_langs_tuple=tuple(sorted(kwargs["target_langs"])),
            wanted_dicts_tuple=tuple(sorted(kwargs["wanted_dicts"])),
        )

        # Log cache stats for monitoring
        cache_info = _cached_stem_query.cache_info()
        LOGGER.debug(f"Cache stats: hits={cache_info.hits}, misses={cache_info.misses}")

        # Return the cached results directly
        return cached_results


def get_cache_info():
    """Get cache statistics for the stem query cache."""
    return {"stem_query_cache": _cached_stem_query.cache_info()}
