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
        combined_filter = (
            get_search_filter(kwargs.get("mode"), search) & 
            Q(srclangs__in=kwargs["src_langs"]) & 
            Q(targetlangs__in=kwargs["target_langs"]) & 
            Q(dicts__in=kwargs["wanted_dicts"])
        )
        
        return Stem.objects(combined_filter)
