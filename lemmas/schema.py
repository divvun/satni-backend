"""GraphQL schemas for Lemmas."""

import graphene
from graphene_mongo.fields import MongoengineConnectionField



# class Query(graphene.ObjectType):
#     lemma_list = MongoengineConnectionField(LemmaType,
#                                             search=graphene.String())
#
#     def resolve_lemma_list(self, info, search=None, **kwargs):
#         if search:
#             return Lemma.objects.filter(lemma__istartswith=search)
#
#         return Lemma.objects.all()

# class Mutations(graphene.ObjectType):
#     create_lemma = CreateLemmaMutation.Field()
#     update_lemma = UpdateLemmaMutation.Field()
#     delete_lemma = DeleteLemmaMutation.Field()
