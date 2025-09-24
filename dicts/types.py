import graphene
from graphene import relay
from graphene_mongo import MongoengineObjectType
from graphene_mongo.fields import MongoengineConnectionField
from lemmas.types import LemmaType

from .models import DictEntry, ExampleGroup, Restriction, TranslationGroup


class LemmaConnection(relay.Connection):
    class Meta:
        node = LemmaType


class ExampleGroupType(MongoengineObjectType):
    class Meta:
        model = ExampleGroup


class RestrictionType(MongoengineObjectType):
    class Meta:
        model = Restriction


class TranslationGroupType(MongoengineObjectType):
    class Meta:
        model = TranslationGroup
    
    translationLemmas = graphene.ConnectionField(LemmaConnection)
    
    def resolve_translationLemmas(self, info):
        return self.translationLemmas


class DictEntryType(MongoengineObjectType):
    class Meta:
        model = DictEntry
    
    lookupLemmas = graphene.ConnectionField(LemmaConnection)
    
    def resolve_lookupLemmas(self, info):
        return self.lookupLemmas
