from typing import List
import strawberry


@strawberry.type
class GeneratorAnalysis:
    """HFST gives a wordform and a weight."""

    wordform: str
    weight: str


@strawberry.type
class GeneratorResult:
    """The result of the generation of one paradigm template."""

    paradigm_template: str
    analyses: List[GeneratorAnalysis]
