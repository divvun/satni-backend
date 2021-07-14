"""Models for lemmatiser results."""
import graphene


class LemmatiserResultType(graphene.ObjectType):
    """Results for all languages."""
    language = graphene.String()
    wordforms = graphene.List(graphene.String)
    analyses = graphene.List(graphene.String)
