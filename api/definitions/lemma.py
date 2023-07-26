
import strawberry


@strawberry.type
class Lemma:
    pos: str | None
    text: str
