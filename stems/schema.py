"""Queries for stem models."""
import logging

import graphene
from graphene import relay
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
            Q(stem=exact) & 
            Q(srclangs__in=kwargs["src_langs"]) & 
            Q(targetlangs__in=kwargs["target_langs"]) & 
            Q(dicts__in=kwargs["wanted_dicts"])
        )
        
        return Stem.objects(combined_filter)

    def resolve_stem_list(self, info, search, **kwargs):
        combined_filter = (
            get_search_filter(kwargs.get("mode"), search) & 
            Q(srclangs__in=kwargs["src_langs"]) & 
            Q(targetlangs__in=kwargs["target_langs"]) & 
            Q(dicts__in=kwargs["wanted_dicts"])
        )
        
        queryset = Stem.objects(combined_filter)
        return queryset
