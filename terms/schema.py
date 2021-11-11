import logging

import graphene
from graphene_mongo.fields import MongoengineConnectionField
from lemmas.models import Lemma
from mongoengine.queryset.visitor import Q

from .models import Concept
from .types import ConceptType

LOGGER = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    concept_list = graphene.List(
        ConceptType,
        exact=graphene.String(),
        src_langs=graphene.List(graphene.String),
        target_langs=graphene.List(graphene.String),
    )

    def resolve_concept_list(self, info, exact, **kwargs):
        src_langs = kwargs["src_langs"]
        target_langs = kwargs["target_langs"]
        langs = set(src_langs + target_langs)
        names = [
            concept.name
            for concept in Concept.objects(
                terms__expression__in=Lemma.objects(lemma=exact)
            )
        ]

        if not names:
            return []

        name_queries = [Q(name=name) for name in names]
        name_filter = name_queries.pop()
        for item in name_queries:
            name_filter |= item

        named = Concept.objects(name_filter)
        wanted_by_langs = [
            name for name in named if name.terms[0].expression.language in langs
        ]

        if wanted_by_langs:
            LOGGER.info(f"term: {exact} " f'langs: {", ".join(sorted(langs))}')

        return wanted_by_langs
