from typing import Annotated

from mongoengine import Document, EmbeddedDocument
from mongoengine.fields import (
    EmbeddedDocumentField,
    ListField,
    ReferenceField,
    StringField,
)

from lemmas.models import Lemma


class ExampleGroup(EmbeddedDocument):
    example: Annotated[str, StringField(required=True)] = StringField(required=True)
    translation: Annotated[str, StringField(required=True)] = StringField(required=True)


class Restriction(EmbeddedDocument):
    restriction: Annotated[str | None, StringField()] = StringField()
    attributes: Annotated[str | None, StringField()] = StringField()


class TranslationGroup(EmbeddedDocument):
    translationLemmas: Annotated[list[Lemma], ListField(ReferenceField(Lemma))] = ListField(ReferenceField(Lemma))
    restriction: Annotated[Restriction | None, EmbeddedDocumentField(Restriction)] = EmbeddedDocumentField(Restriction)
    exampleGroups: Annotated[list[ExampleGroup], ListField(EmbeddedDocumentField(ExampleGroup))] = ListField(EmbeddedDocumentField(ExampleGroup))


class DictEntry(Document):
    meta = {
        "collection": "dicts",
        "indexes": ["lookupLemmas", "translationGroups.translationLemmas"],
    }
    dictName: Annotated[str, StringField(required=True)] = StringField(required=True)
    srcLang: Annotated[str, StringField(required=True)] = StringField(required=True)
    targetLang: Annotated[str, StringField(required=True)] = StringField(required=True)
    lookupLemmas: Annotated[list[Lemma], ListField(ReferenceField(Lemma), required=True)] = ListField(ReferenceField(Lemma), required=True)
    translationGroups: Annotated[list[TranslationGroup], ListField(EmbeddedDocumentField(TranslationGroup), required=True)] = ListField(
        EmbeddedDocumentField(TranslationGroup), required=True
    )
