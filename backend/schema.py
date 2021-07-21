import graphene

import dicts.schema
import generator.schema
import lemmatiser.schema
import stems.schema
import terms.schema


class Query(
    stems.schema.Query,
    dicts.schema.Query,
    lemmatiser.schema.Query,
    terms.schema.Query,
    generator.schema.Query,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(
    query=Query, types=[stems.types.StemType, terms.types.ConceptType]
)
