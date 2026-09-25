"""Queries for stem models."""

import logging
import re
from functools import lru_cache

import graphene
from bson import Regex
from graphene import relay
from mongoengine.queryset.visitor import Q

from .models import Stem
from .types import StemType

LOGGER = logging.getLogger(__name__)


def get_search_filter(mode, search):
    """
    Build the search filter for the given mode.

    `search_stem` is always stored lowercased, so the incoming `search` is
    expected to already be lowercased (see `resolve_stem_list`).

    This builds the regex filter as an unflagged `bson.Regex` instead of
    using mongoengine's `__startswith`/`__contains`/`__endswith` operators.
    Those operators build the regex via Python's `re.compile`, which always
    attaches the `re.UNICODE` flag to `str` patterns (even when `flags=0` is
    passed explicitly) - and MongoDB's query planner refuses to use an
    anchored index range-seek for *any* regex that carries option flags,
    falling back to a full index scan instead. A `bson.Regex` built with no
    flags avoids that pitfall and lets MongoDB range-seek on the
    `search_stem` index for the (most common) "start" mode.
    """
    escaped = re.escape(search)

    if mode == "middle":
        return Q(search_stem=Regex(escaped))

    if mode == "end":
        return Q(search_stem=Regex(f"{escaped}$"))

    return Q(search_stem=Regex(f"^{escaped}"))


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
