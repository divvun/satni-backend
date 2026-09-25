"""Setup a schema to get results from the lemmatiser."""

import platform
from pathlib import Path

import graphene

from .lemmatiser import lemmatiser
from .types import LemmatiserResultType

GIELLA_DIR = (
    Path("/usr/share/giella")
    if platform.system() == "Linux"
    else Path("/usr/local/share/giella")
)

LEMMATISERS = {path.name: lemmatiser(path.name) for path in GIELLA_DIR.glob("???")}


class Query(graphene.ObjectType):
    """Query class for lemmatiser."""

    lemmatised = graphene.List(
        LemmatiserResultType, lookup_string=graphene.String(required=True)
    )

    def resolve_lemmatised(self, info, lookup_string=None):
        """Lemmatise lookup_string."""
        return [
            {
                "language": lang,
                "wordforms": [
                    wordform for wordform in LEMMATISERS[lang].lemmatise(lookup_string)
                ],
                "analyses": [
                    {"analysis": analysis.analysis, "weight": analysis.weight}
                    for analysis in LEMMATISERS[lang].analyse(lookup_string)
                ],
            }
            for lang in LEMMATISERS
        ]
