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


class ExampleGroup(EmbeddedDocument):
    example = StringField()
    translation = StringField()


class Restriction(EmbeddedDocument):
    restriction = StringField()
    attributes = StringField()


class TranslationGroup(EmbeddedDocument):
    translationLemmas = ListField(ReferenceField(Lemma))
    restriction = EmbeddedDocumentField(Restriction)
    exampleGroups = ListField(EmbeddedDocumentField(ExampleGroup))


class DictEntry(Document):
    meta = {"collection": "dicts"}
    dictName = StringField(required=True)
    srcLang = StringField(required=True)
    targetLang = StringField(required=True)
    lookupLemmas = ListField(ReferenceField(Lemma), required=True)
    translationGroups = ListField(
        EmbeddedDocumentField(TranslationGroup), required=True
    )
