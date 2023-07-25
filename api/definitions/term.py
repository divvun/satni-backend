from typing import List, Optional
import strawberry

from lemma import Lemma


@strawberry
class Term:
    status: Optional[str]
    sanctioned: bool
    note: Optional[str]
    source: Optional[str]
    expression: Lemma


@strawberry
class Concept:
    language: str
    definition: Optional[str]
    explanation: Optional[str]
    terms: List[Term]


@strawberry
class TermEntry:
    name: str
    collections: Optional[List[str]]
    concepts: List[Concept]
