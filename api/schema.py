from typing import List, Union
import strawberry
import json


from main.database import DB

from .definitions.dict import Dict, make_dict
from .definitions.term import TermEntry, make_term_entry


def make_entry(entry) -> Union[Dict, TermEntry]:
    return (
        make_dict(entry.get("Dict"))
        if entry.get("Dict")
        else make_term_entry(entry.get("Term"))
    )


@strawberry.type
class Query:
    @strawberry.field
    def list_lemmas(self, search_term: str) -> List[str]:
        return [answer for db in DB for answer in db.list_lemmas(search_term)]

    @strawberry.field
    def entry_list(self, search_term: str) -> List[Union[Dict, TermEntry]]:
        return [
            make_entry(entry)
            for db in DB
            for entry in json.loads(db.entry_list(search_term))
        ]


schema = strawberry.Schema(Query)
