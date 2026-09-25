import logging

import graphene
from lemmas.models import Lemma
from mongoengine.queryset.visitor import Q

from .models import DictEntry
from .types import DictEntryType

LOGGER = logging.getLogger(__name__)


class Query(graphene.ObjectType):
    dict_entry_list = graphene.List(
        DictEntryType,
        exact=graphene.String(required=True),
        src_langs=graphene.List(graphene.String, required=True),
        target_langs=graphene.List(graphene.String, required=True),
        wanted_dicts=graphene.List(graphene.String, required=True),
    )

    def resolve_dict_entry_list(self, info, wanted_dicts, exact=None, **kwargs):
        src_langs = kwargs["src_langs"]
        target_langs = kwargs["target_langs"]

        matching_lemmas = Lemma.objects(lemma=exact)

        dict_entries = []

        if (
            "fin" in src_langs
            and "sme" in target_langs
            and "sammallahtismefin" in wanted_dicts
        ):
            translation_filter = Q(
                translationGroups__translationLemmas__in=matching_lemmas
            ) & Q(dictName="sammallahtismefin")
            dict_entries.extend(DictEntry.objects(translation_filter))

        lookup_filter = (
            Q(lookupLemmas__in=matching_lemmas)
            & Q(srcLang__in=src_langs)
            & Q(targetLang__in=target_langs)
            & Q(dictName__in=wanted_dicts)
        )
        dict_entries.extend(DictEntry.objects(lookup_filter))

        if dict_entries:
            LOGGER.info(
                f"{exact} "
                f"src: {', '.join(sorted(src_langs))} "
                f"target: {', '.join(sorted(target_langs))} "
                f"dicts: {', '.join(sorted(wanted_dicts))}"
            )

        return dict_entries
