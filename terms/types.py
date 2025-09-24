import graphene
from graphene_mongo import MongoengineObjectType
from lemmas.types import LemmaType

from .models import Concept, Term


class TermType(MongoengineObjectType):
    class Meta:
        model = Term
    
    expression = graphene.Field(LemmaType)
    
    def resolve_expression(self, info):
        return self.expression


class ConceptType(MongoengineObjectType):
    class Meta:
        model = Concept
