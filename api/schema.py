from typing import List
import strawberry
import json


from main.database import DB

from .definitions.dict import Dict, make_dict


@strawberry.type
class Query:
    @strawberry.field
    def list_lemmas(self, search_term: str) -> List[str]:
        return [answer for db in DB for answer in db.list_lemmas(search_term)]

    @strawberry.field
    def dict_entries(self, search_term: str) -> List[Dict]:
        return [
            make_dict(entry["Dict"])
            for db in DB
            for entry in json.loads(db.entry_list(search_term))
        ]


schema = strawberry.Schema(Query)
