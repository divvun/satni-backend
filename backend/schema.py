import graphene

import dicts.schema
import lemmas.schema
import stems.schema
import terms.schema


class Query(stems.schema.Query, dicts.schema.Query, terms.schema.Query,
            graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query,
                         types=[stems.types.StemType, terms.types.ConceptType])
