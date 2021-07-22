"""Models for lemmatiser results."""
import graphene


class LemmatiserAnalysis(graphene.ObjectType):
    """HFST gives a wordform and a weight."""

    analysis = graphene.String()
    weight = graphene.Float()


class LemmatiserResultType(graphene.ObjectType):
    """Results for all languages."""

    language = graphene.String()
    wordforms = graphene.List(graphene.String)
    analyses = graphene.List(LemmatiserAnalysis)
