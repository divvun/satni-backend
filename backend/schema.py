import graphene

import dicts.schema
import stems.schema
import terms.schema


class Query(stems.schema.Query, dicts.schema.Query, terms.schema.Query,
            graphene.ObjectType):
    pass


# class Mutation(graphene.ObjectType):
#     pass
#

schema = graphene.Schema(query=Query,
                         # mutation=Mutation,
                         types=[stems.types.StemType, terms.types.ConceptType])
