"""Setup a schema to get results from the lemmatiser."""
from pathlib import Path

import graphene

from .lemmatiser import lemmatiser
from .types import LemmatiserResultType

LEMMATISERS = {
    path.name: lemmatiser(path.name)
    for path in Path('/usr/share/giella/').glob('???')
}


class Query(graphene.ObjectType):
    """Query class for lemmatiser."""
    lemmatised = graphene.List(LemmatiserResultType,
                               lookup_string=graphene.String())

    def resolve_lemmatised(self, info, lookup_string=None, **kwargs):
        """Lemmatise lookup_string."""
        return [{
            'language':
            lang,
            'wordforms': [
                wordform
                for wordform in LEMMATISERS[lang].lemmatise(lookup_string)
            ],
            'analyses': [
                analysis
                for analysis in LEMMATISERS[lang].analyse(lookup_string)
            ]
        } for lang in LEMMATISERS]
