"""Models for lemmatiser results."""
import graphene


class LemmatiserAnalysis(graphene.ObjectType):
    """HFST gives a wordform and a weight."""

    analysis = graphene.String(required=True)
    weight = graphene.Float(required=True)


class LemmatiserResultType(graphene.ObjectType):
    """Results for all languages."""

    language = graphene.String(required=True)
    wordforms = graphene.List(graphene.String, required=True)
    analyses = graphene.List(LemmatiserAnalysis, required=True)
