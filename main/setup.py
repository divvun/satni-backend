from satni_back_python import SatniDictDB, SatniTermDB
from os import getenv
from .generator.generator import ParadigmGenerator
from .lemmatiser.lemmatiser import lemmatiser
from pathlib import Path

DB = [
    SatniDictDB(f"{getenv('GTHOME')}/words/dicts/{pair}/src/")
    for pair in ["smenob", "nobsme", "smanob", "nobsma"]
]

DB.append(SatniTermDB("files/"))

GENERATORS = {
    language: ParadigmGenerator(language)
    for language in ["fin", "sma", "sme", "smj", "smn", "sms", "nob"]
}

LEMMATISERS = {
    path.name: lemmatiser(path.name)
    for path in Path("/usr/local/share/giella/").glob("???")
}
