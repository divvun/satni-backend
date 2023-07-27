import json
from base64 import b64decode, b64encode
from typing import Generic, TypeVar, cast

import strawberry
from satni_back_python import SatniDictDB, SatniTermDB

from main.setup import DB, GENERATORS, LEMMATISERS

from .definitions.dict import Dict, make_dict
from .definitions.generator import GeneratorAnalysis, GeneratorResult
from .definitions.lemmatiser import LemmatiserAnalysis, LemmatiserResult
from .definitions.search_filter import SearchFilter
from .definitions.term import TermEntry, make_term_entry


def encode_lemma_cursor(position: int) -> str:
    """
    Encodes the given lemma position into a cursor.

    :param position: The lemma position to encode.

    :return: The encoded cursor.
    """
    return b64encode(f"user:{position}".encode("ascii")).decode("ascii")


def decode_lemma_cursor(cursor: str) -> int:
    """
    Decodes the lemma position from the given cursor.

    :param cursor: The cursor to decode.

    :return: The decoded lemma position.
    """
    cursor_data = b64decode(cursor.encode("ascii")).decode("ascii")
    return int(cursor_data.split(":")[1])


GenericType = TypeVar("GenericType")


@strawberry.type
class Edge(Generic[GenericType]):
    node: GenericType = strawberry.field(description="The item at the end of the edge.")
    cursor: str = strawberry.field(description="A cursor for use in pagination.")


@strawberry.type
class Connection(Generic[GenericType]):
    page_info: "PageInfo" = strawberry.field(
        description="Information to aid in pagination."
    )
    edges: list["Edge[GenericType]"] = strawberry.field(
        description="A list of edges in this connection."
    )
    total_count: int = strawberry.field(description="Total found items")


@strawberry.type
class PageInfo:
    has_next_page: bool = strawberry.field(
        description="When paginating forwards, are there more items?"
    )
    has_previous_page: bool = strawberry.field(
        description="When paginating backwards, are there more items?"
    )
    start_cursor: str | None = strawberry.field(
        description="When paginating backwards, the cursor to continue."
    )
    end_cursor: str | None = strawberry.field(
        description="When paginating forwards, the cursor to continue."
    )


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
    @strawberry.field(
        description="Paginated list of lemmas containing the search string"
    )
    def list_lemmas(
        self, search_filter: SearchFilter, first: int = 50, after: str | None = None
    ) -> Connection[str]:
        all_lemmas = [
            answer
            for db in DB
            if is_wanted_db(search_filter=search_filter, db=db)
            for answer in db.list_lemmas(search_filter.search_term)
        ]

        first_position = (
            decode_lemma_cursor(cursor=after) + 1 if after is not None else 0
        )
        current_last = first_position + first
        sliced_lemmas = all_lemmas[first_position:current_last]

        has_next_page = len(sliced_lemmas) >= first
        has_previous_page = first_position > 0

        edges = [
            Edge(
                node=cast(str, lemma),
                cursor=encode_lemma_cursor(position=first_position + index),
            )
            for (index, lemma) in enumerate(sliced_lemmas)
        ]

        if edges:
            start_cursor = edges[0].cursor
        else:
            start_cursor = None

        if len(edges) > 1:
            end_cursor = edges[-1].cursor

        return Connection(
            total_count=len(all_lemmas),
            edges=edges,
            page_info=PageInfo(
                has_next_page=has_next_page,
                has_previous_page=has_previous_page,
                start_cursor=start_cursor,
                end_cursor=end_cursor,
            ),
        )

    @strawberry.field(
        description="Term and dictionary articles containing the search term"
    )
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

    @strawberry.field(
        description="Generate inflected wordforms for a given lemma and language"
    )
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

    @strawberry.field(description="Lemmatise the given wordform")
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
