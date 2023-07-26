import json
from typing import List, Union

import strawberry

from main.setup import DB, GENERATORS, LEMMATISERS

from .definitions.dict import Dict, make_dict
from .definitions.generator import GeneratorAnalysis, GeneratorResult
from .definitions.lemmatiser import LemmatiserAnalysis, LemmatiserResult
from .definitions.term import TermEntry, make_term_entry


def make_entry(entry) -> Union[Dict, TermEntry]:
    return (
        make_dict(entry.get("Dict"))
        if entry.get("Dict")
        else make_term_entry(entry.get("Term"))
    )


@strawberry.type
class Query:
    @strawberry.field
    def list_lemmas(self, search_term: str) -> List[str]:
        return [answer for db in DB for answer in db.list_lemmas(search_term)]

    @strawberry.field
    def entry_list(self, search_term: str) -> List[Union[Dict, TermEntry]]:
        return [
            make_entry(entry)
            for db in DB
            for entry in json.loads(db.entry_list(search_term))
        ]

    @strawberry.field
    def generated(
        self, origform: str, language: str, paradigmTemplates: List[str]
    ) -> List[GeneratorResult]:
        return [
            GeneratorResult(
                paradigm_template=paradigm_template,
                analyses=[
                    GeneratorAnalysis(
                        wordform=analysis.wordform, weight=analysis.weight
                    )
                    for analysis in analyses
                ],
            )
            for paradigm_template, analyses in GENERATORS[language].generate_wordforms(
                origform, paradigmTemplates
            )
        ]

    @strawberry.field
    def lemmatised(self, lookup_string: str) -> List[LemmatiserResult]:
        """Lemmatise lookup_string."""
        return [
            LemmatiserResult(
                language=lang,
                wordforms=[
                    wordform for wordform in LEMMATISERS[lang].lemmatise(lookup_string)
                ],
                analyses=[
                    LemmatiserAnalysis(
                        analysis=analysis.analysis, weight=analysis.weight
                    )
                    for analysis in LEMMATISERS[lang].analyse(lookup_string)
                ],
            )
            for lang in LEMMATISERS
        ]


schema = strawberry.Schema(Query)
