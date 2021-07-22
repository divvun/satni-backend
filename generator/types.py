"""Models for generator results."""
import graphene


class GeneratorAnalysis(graphene.ObjectType):
    """HFST gives a wordform and a weight."""

    wordform = graphene.String()
    weight = graphene.Float()


class GeneratorResultType(graphene.ObjectType):
    """The result of the generation of one paradigm template."""

    paradigm_template = graphene.String()
    analyses = graphene.List(GeneratorAnalysis)
