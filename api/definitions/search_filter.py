import strawberry


@strawberry.input
class SearchFilter:
    search_term: str
    wanted_src_langs: list[str]
    wanted_target_langs: list[str]
    wanted_dicts: list[str]
