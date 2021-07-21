"""Queries for stem models."""
import logging

import graphene
from graphene_mongo.fields import MongoengineConnectionField
from mongoengine.queryset.visitor import Q

from .models import Stem
from .types import StemType

LOGGER = logging.getLogger(__name__)


def get_search_filter(mode, search):
    if mode == "middle":
        return Q(search_stem__icontains=search)

    if mode == "end":
        return Q(search_stem__iendswith=search)

    return Q(search_stem__istartswith=search)


class Query(graphene.ObjectType):
    stem_list = MongoengineConnectionField(
        StemType,
        search=graphene.String(),
        mode=graphene.String(),
        src_langs=graphene.List(graphene.String),
        target_langs=graphene.List(graphene.String),
        wanted_dicts=graphene.List(graphene.String),
    )
    has_stem = graphene.List(
        StemType,
        exact=graphene.String(),
        src_langs=graphene.List(graphene.String),
        target_langs=graphene.List(graphene.String),
        wanted_dicts=graphene.List(graphene.String),
    )

    def resolve_has_stem(self, info, exact, **kwargs):
        by_exact_stem = Stem.objects(stem=exact)
        target_langs = kwargs["target_langs"]
        wanted_dicts = kwargs["wanted_dicts"]

        by_target_langs = [
            s
            for s in by_exact_stem
            if any([targetlang in target_langs for targetlang in s.targetlangs])
        ]
        by_wanted_dicts = [
            s
            for s in by_target_langs
            if any([dict in wanted_dicts for dict in s.dicts])
        ]

        return by_wanted_dicts

    def resolve_stem_list(self, info, search, **kwargs):
        src_langs = kwargs["src_langs"]
        target_langs = kwargs["target_langs"]
        wanted_dicts = kwargs["wanted_dicts"]

        log_info = [search]
        for key, value in kwargs.items():
            log_info.append(f"{key}:")
            if isinstance(value, list):
                log_info.append(", ".join(sorted(value)))
            else:
                log_info.append(str(value))
        LOGGER.info(" ".join(log_info))

        search_filter = get_search_filter(kwargs.get("mode"), search)

        by_search_stem = Stem.objects(search_filter).order_by("search_stem")
        by_src_langs = [
            s
            for s in by_search_stem
            if any([srclang in src_langs for srclang in s.srclangs])
        ]
        by_target_langs = [
            s
            for s in by_src_langs
            if any([targetlang in target_langs for targetlang in s.targetlangs])
        ]
        by_wanted_dicts = [
            s
            for s in by_target_langs
            if any([dict in wanted_dicts for dict in s.dicts])
        ]

        return by_wanted_dicts
