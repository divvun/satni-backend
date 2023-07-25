from satni_back_python import SatniDictDB, SatniTermDB
from os import getenv

DictDB = [
    SatniDictDB(f"{getenv('GTHOME')}/words/dicts/{pair}/src/")
    for pair in ["smenob", "nobsme", "smanob", "nobsma"]
]

TermDB = [SatniTermDB("files/")]
