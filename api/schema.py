import json

import strawberry
from satni_back_python import SatniDictDB, SatniTermDB

from main.setup import DB, GENERATORS, LEMMATISERS

from .definitions.dict import Dict, make_dict
from .definitions.generator import GeneratorAnalysis, GeneratorResult
from .definitions.lemmatiser import LemmatiserAnalysis, LemmatiserResult
from .definitions.search_filter import SearchFilter
from .definitions.term import TermEntry, make_term_entry


def make_entry(entry, langs) -> Dict | TermEntry:
    return (
        make_dict(entry.get("Dict"))
        if entry.get("Dict")
        else make_term_entry(entry.get("Term"), langs)
    )


def is_wanted_db(search_filter: SearchFilter, db: SatniDictDB | SatniTermDB) -> bool:
    return (
        isinstance(db, SatniDictDB)
        and f"{db.src_lang}{db.target_lang}" in search_filter.wanted_dicts
        and db.src_lang in search_filter.wanted_src_langs
        and db.target_lang in search_filter.wanted_target_langs
    ) or (isinstance(db, SatniTermDB) and "termwiki" in search_filter.wanted_dicts)


@strawberry.type
class Query:
    @strawberry.field
    def list_lemmas(self, search_filter: SearchFilter) -> list[str]:
        return [
            answer
            for db in DB
            if is_wanted_db(search_filter=search_filter, db=db)
            for answer in db.list_lemmas(search_filter.search_term)
        ]

    @strawberry.field
    def entry_list(self, search_filter: SearchFilter) -> list[Dict | TermEntry]:
        def is_valid_entry(entry):
            return isinstance(entry, Dict) or (
                isinstance(entry, TermEntry) and len(entry.concepts) > 1
            )

        return [
            final_entry
            for final_entry in [
                make_entry(
                    entry,
                    {
                        lang
                        for langs in [
                            search_filter.wanted_src_langs,
                            search_filter.wanted_target_langs,
                        ]
                        for lang in langs
                    },
                )
                for db in DB
                if is_wanted_db(search_filter=search_filter, db=db)
                for entry in json.loads(db.entry_list(search_filter.search_term))
            ]
            if is_valid_entry(final_entry)
        ]

    @strawberry.field
    def generated(
        self, origform: str, language: str, paradigmTemplates: list[str]
    ) -> list[GeneratorResult]:
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
    def lemmatised(self, lookup_string: str) -> list[LemmatiserResult]:
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
