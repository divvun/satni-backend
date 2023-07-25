from typing import List, Optional
import strawberry

from .lemma import Lemma


@strawberry.type
class Term:
    status: Optional[str]
    sanctioned: bool
    note: Optional[str]
    source: Optional[str]
    expression: Lemma


@strawberry.type
class Concept:
    language: str
    definition: Optional[str]
    explanation: Optional[str]
    terms: List[Term]


@strawberry.type
class TermEntry:
    name: str
    collections: Optional[List[str]]
    concepts: List[Concept]


def make_term(term):
    return Term(
        status=term.get("status"),
        sanctioned=term.get("sanctioned"),
        note=term.get("note"),
        source=term.get("source"),
        expression=Lemma(
            pos=term.get("expression").get("pos"),
            text=term.get("expression").get("text"),
        ),
    )


def make_concept(concept):
    return Concept(
        language=concept.get("language"),
        definition=concept.get("definition"),
        explanation=concept.get("explanation"),
        terms=[make_term(term) for term in concept.get("terms")],
    )


def make_term_entry(entry):
    return TermEntry(
        name=entry.get("name"),
        collections=None,
        concepts=[make_concept(concept) for concept in entry.get("concepts")],
    )
