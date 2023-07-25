from satni_back_python import SatniDictDB
from os import getenv

DB = [
    SatniDictDB(f"{getenv('GTHOME')}/words/dicts/{pair}/src/")
    for pair in ["smenob", "nobsme", "smanob", "nobsma"]
]
