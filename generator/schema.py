"""Setup a schema to get results from the lemmatiser."""
import graphene

from .generator import ParadigmGenerator
from .types import GeneratorResultType

GENERATOR_LANGS = ["fin", "sma", "sme", "smj", "smn", "sms"]
GENERATORS = {
    language: ParadigmGenerator(language)
    for language in GENERATOR_LANGS
}


class Query(graphene.ObjectType):
    """Query class for generator."""

    generated = graphene.List(
        GeneratorResultType,
        origform=graphene.String(required=True),
        language=graphene.String(required=True),
        paradigmTemplates=graphene.List(graphene.String, required=True),
    )

    def resolve_generated(self, info, origform, language, paradigmTemplates):
        """Generate wordforms."""
        print("generator schema", origform, language, paradigmTemplates)

        if language not in GENERATOR_LANGS:
            return []
        
        return [
            {
                "paradigm_template": paradigm_template,
                "analyses": [
                    {"wordform": analysis.wordform, "weight": analysis.weight}
                    for analysis in analyses
                ],
            }
            for paradigm_template, analyses in GENERATORS[language].generate_wordforms(
                origform, paradigmTemplates
            )
        ]
