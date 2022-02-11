from mongoengine import Document
from mongoengine.fields import ListField, ObjectIdField, StringField


class Stem(Document):
    meta = {"collection": "stems"}
    stem = StringField(required=True)
    search_stem = StringField(required=True)
    srclangs = ListField(StringField(required=True))
    targetlangs = ListField(StringField(required=True))
    dicts = ListField(StringField(required=True))
