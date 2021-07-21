"""Models for generator results."""
import graphene


class GeneratorResultType(graphene.ObjectType):
    """The result of the generation of one paradigm template."""

    paradigm_template = graphene.String()
    wordforms = graphene.List(graphene.String)
