from typing import List
import strawberry
import json


from main.database import DictDB, TermDB

from .definitions.dict import Dict, make_dict
from .definitions.term import TermEntry, make_term_entry


@strawberry.type
class Query:
    @strawberry.field
    def list_lemmas(self, search_term: str) -> List[str]:
        return [answer for db in DictDB for answer in db.list_lemmas(search_term)]

    @strawberry.field
    def dict_entries(self, search_term: str) -> List[Dict]:
        return [
            make_dict(entry["Dict"])
            for db in DictDB
            for entry in json.loads(db.entry_list(search_term))
        ]

    @strawberry.field
    def term_entries(self, search_term: str) -> List[TermEntry]:
        arg = [
            entry for db in TermDB for entry in json.loads(db.entry_list(search_term))
        ]
        print(arg)
        urg = [make_term_entry(entry["Term"]) for entry in arg]
        print(urg)
        return urg


schema = strawberry.Schema(Query)
