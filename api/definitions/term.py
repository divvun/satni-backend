import strawberry

from .lemma import Lemma


@strawberry.type
class Term:
    status: str | None
    sanctioned: bool
    note: str | None
    source: str | None
    expression: Lemma


@strawberry.type
class Concept:
    language: str
    definition: str | None
    explanation: str | None
    terms: list[Term]


@strawberry.type
class TermEntry:
    name: str
    collections: list[str] | None
    concepts: list[Concept]


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


def make_term_entry(entry, langs):
    return TermEntry(
        name=entry.get("name"),
        collections=None,
        concepts=[
            make_concept(concept)
            for concept in entry.get("concepts")
            if concept.get("language") in langs
        ],
    )
