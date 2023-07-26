from typing import List

import strawberry


@strawberry.type
class LemmatiserAnalysis:
    """HFST gives a wordform and a weight."""

    analysis: str
    weight: str


@strawberry.type
class LemmatiserResult:
    """Results for all languages."""

    language: str
    wordforms: List[str]
    analyses: List[LemmatiserAnalysis]
