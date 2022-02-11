from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    BooleanField,
    EmbeddedDocumentField,
    ListField,
    ObjectIdField,
    ReferenceField,
    StringField,
)

from lemmas.models import Lemma


class Term(EmbeddedDocument):
    status = StringField(blank=True, null=True)
    sanctioned = BooleanField(default=False)
    note = StringField(blank=True, null=True)
    source = StringField(blank=True, null=True)
    expression = ReferenceField(Lemma, required=True)


class Concept(Document):
    meta = {"collection": "terms"}
    name = StringField(required=True)
    language = StringField(required=True)
    definition = StringField(blank=True, null=True)
    explanation = StringField(blank=True, null=True)
    terms = ListField(EmbeddedDocumentField(Term), required=True)
    collections = ListField(StringField())

    def __str__(self):
        return "%s: %s" % (self.name, self.language)
