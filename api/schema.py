from typing import List, Union
import strawberry
import json


from main.setup import DB, GENERATORS

from .definitions.dict import Dict, make_dict
from .definitions.term import TermEntry, make_term_entry
from .definitions.generator import GeneratorResult, GeneratorAnalysis


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


schema = strawberry.Schema(Query)
