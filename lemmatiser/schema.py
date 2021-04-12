from pathlib import Path

import graphene

from .lemmatiser import Lemmatiser

LEMMATISERS = {
    path.name: Lemmatiser(path / 'analyser-gt-desc.hfstol')
    for path in Path('/usr/share/giella/').glob('???')
}


class Query(graphene.ObjectType):
    lemmas = graphene.List(graphene.String, lookup_string=graphene.String())

    def resolve_lemmas(self, info, lookup_string=None, **kwargs):
        return sorted(
            set([
                lemma for lang, lemmatiser in LEMMATISERS.items()
                for lemma in lemmatiser.lemmatise(lookup_string)
            ]))
