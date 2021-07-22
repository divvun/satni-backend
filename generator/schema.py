"""Setup a schema to get results from the lemmatiser."""
import graphene

from .generator import ParadigmGenerator
from .types import GeneratorResultType

GENERATORS = {
    language: ParadigmGenerator(language)
    for language in ["fin", "sma", "sme", "smj", "smn", "sms"]
}


class Query(graphene.ObjectType):
    """Query class for generator."""

    generated = graphene.List(
        GeneratorResultType,
        origform=graphene.String(),
        language=graphene.String(),
        partOfSpeech=graphene.String(),
    )

    def resolve_generated(self, info, origform, language, partOfSpeech):
        """Generate wordforms."""
        return [
            {
                "paradigm_template": paradigm_template,
                "analyses": [
                    {"wordform": analysis.wordform, "weight": analysis.weight}
                    for analysis in analyses
                ],
            }
            for paradigm_template, analyses in GENERATORS[language].generate_wordforms(
                origform, partOfSpeech
            )
        ]
