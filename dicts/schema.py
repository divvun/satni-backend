import logging

import graphene
from graphene_mongo.fields import MongoengineConnectionField
from lemmas.models import Lemma
from mongoengine.queryset.visitor import Q

from .models import DictEntry
from .types import DictEntryType

LOGGER = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    dict_entry_list = graphene.List(
        DictEntryType,
        exact=graphene.String(),
        src_langs=graphene.List(graphene.String),
        target_langs=graphene.List(graphene.String),
        wanted_dicts=graphene.List(graphene.String))

    def resolve_dict_entry_list(self,
                                info,
                                wanted_dicts,
                                exact=None,
                                **kwargs):
        src_langs = kwargs['src_langs']
        target_langs = kwargs['target_langs']

        lookup_filter = Q(lookupLemmas__in=Lemma.objects(lemma=exact))
        translation_filter = Q(
            translationGroups__translationLemmas__in=Lemma.objects(
                lemma=exact))
        by_lemma = DictEntry.objects(lookup_filter | translation_filter)
        by_src_lang = [d for d in by_lemma if d.srcLang in src_langs]
        by_target_lang = [
            d for d in by_src_lang if d.targetLang in target_langs
        ]
        by_dicts = [d for d in by_target_lang if d.dictName in wanted_dicts]

        # if by_dicts:
        #     LOGGER.info(f'{exact} '
        #                 f'langs: {", ".join(sorted(wanted))} '
        #                 f'dicts: {", ".join(sorted(wanted_dicts))}')

        return by_dicts
