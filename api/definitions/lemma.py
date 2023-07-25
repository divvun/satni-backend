from typing import Optional
import strawberry


@strawberry.type
class Lemma:
    pos: Optional[str]
    text: str
