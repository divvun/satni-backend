"""Models for generator results."""
import graphene


class GeneratorAnalysis(graphene.ObjectType):
    """HFST gives a wordform and a weight."""

    wordform = graphene.String(required=True)
    weight = graphene.Float(required=True)


class GeneratorResultType(graphene.ObjectType):
    """The result of the generation of one paradigm template."""

    paradigm_template = graphene.String(required=True)
    analyses = graphene.List(GeneratorAnalysis)
