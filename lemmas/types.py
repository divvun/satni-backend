"""Types for the lemma representation."""

import graphene
from graphene import relay
from graphene_mongo import MongoengineObjectType
from stems.has_stem_cache import has_stem

from .models import Lemma


class LemmaType(MongoengineObjectType):
    class Meta:
        model = Lemma
        interfaces = (relay.Node,)

    has_stem = graphene.Boolean(
        src_langs=graphene.List(graphene.String, required=True),
        target_langs=graphene.List(graphene.String, required=True),
        wanted_dicts=graphene.List(graphene.String, required=True),
    )

    def resolve_has_stem(self, info, src_langs, target_langs, wanted_dicts):
        return has_stem(info, self.lemma, src_langs, target_langs, wanted_dicts)
