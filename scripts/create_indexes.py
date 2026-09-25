"""Explicitly build the mongoengine-declared indexes for all Document models.

Run with `poetry run python manage.py runscript create_indexes`.

mongoengine can create indexes lazily on first access, but for large,
already-populated collections that first query would pay the full index
build cost. Running this script ahead of time (e.g. as part of a deploy)
avoids that surprise latency.
"""

from dicts.models import DictEntry
from lemmas.models import Lemma
from stems.models import Stem
from terms.models import Concept

MODELS = [Lemma, Stem, DictEntry, Concept]


def run():
    """Ensure indexes exist for every model listed in MODELS."""
    for model in MODELS:
        print(f"Ensuring indexes for {model.__name__}...")
        model.ensure_indexes()

    print("Done.")
