"""Models for lemmas."""

from typing import Annotated

from mongoengine import Document
from mongoengine.fields import StringField


class Lemma(Document):
    """A representation of lemmas."""

    meta = {"collection": "lemmas", "indexes": ["lemma"]}
    lemma: Annotated[str, StringField(required=True)] = StringField(required=True)
    presentation_lemma: Annotated[str, StringField(required=True)] = StringField(required=True)
    pos: Annotated[str | None, StringField()] = StringField()
    language: Annotated[str, StringField(required=True)] = StringField(required=True)
    dialect: Annotated[str | None, StringField()] = StringField()
    country: Annotated[str | None, StringField()] = StringField()  # two chars, iso something

    def __str__(self):
        return "%s %s %s" % (self.lemma, self.pos, self.language)
