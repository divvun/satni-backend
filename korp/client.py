"""Client for checking whether a lemma exists in the Korp corpus.

This wraps the direct HTTP calls to https://gtweb.uit.no/korp that used to be
made from the frontend. Results are cached in-process so that repeated
lookups for the same language/lemma pair do not hit the remote Korp backend
again.
"""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from functools import lru_cache

LOGGER = logging.getLogger(__name__)

REQUEST_TIMEOUT = 10

# Corpora searched per language, mirroring the setup that used to live in the
# frontend (src/api/index.ts).
KORP_INFO = {
    "sma": {
        "start_query": "https://gtweb.uit.no/korp/backend-sma/query?corpus=",
        "corpora": "SMA_ADMIN_20211118,SMA_BIBLE_20211118,SMA_FACTA_20211118,"
        "SMA_FICTI_20211118,SMA_LAWS_20211118,SMA_NEWS_20211118,"
        "SMA_SCIENCE_20211118",
    },
    "sme": {
        "start_query": "https://gtweb.uit.no/korp/backend-sme/query?corpus=",
        "corpora": "SME_ADMIN_20181106,SME_ASSU_20181106,SME_AVVIR_20181106,"
        "SME_BIBLE_20181106,SME_BLOGS_20181106,SME_FACTA_20181106,"
        "SME_FICTI_20181106,SME_LAWS_20181106,SME_MINAIGI_20181106,"
        "SME_MUITALUS_20170319,SME_NRK_20181106,SME_SCIENCE_20181106",
    },
    "smj": {
        "start_query": "https://gtweb.uit.no/korp/backend-smj/query?corpus=",
        "corpora": "SMJ_BIBLE_20211118,SMJ_FICTI_20211118,SMJ_NEWS_20211118,"
        "SMJ_LAWS_20211118,SMJ_ADMIN_20211118,SMJ_SCIENCE_20211118,"
        "SMJ_FACTA_20211118",
    },
    "smn": {
        "start_query": "https://gtweb.uit.no/korp/backend-smn/query?corpus=",
        "corpora": "SMN_ADMIN_20211118,SMN_BIBLE_20211118,SMN_BLOGS_20211118,"
        "SMN_FACTA_20211118,SMN_FICTI_20211118,SMN_NEWS_20211118,"
        "SMN_SCIENCE_20211118,SMN_WIKIPEDIA_20211118",
    },
    "sms": {
        "start_query": "https://gtweb.uit.no/korp/backend-sms/query?corpus=",
        "corpora": "SMS_ADMIN_20211118,SMS_BLOGS_20211118,SMS_FACTA_20211118,"
        "SMS_LAWS_20211118,SMS_LITERATURE_20211118,SMS_NEWS_20211118,"
        "SMS_SCIENCE_20211118",
    },
}


def _build_url(language: str, lemma: str) -> str:
    """Build the Korp query URL for the given language and lemma."""
    info = KORP_INFO[language]
    cqp = urllib.parse.quote_plus(f'[lemma = "{lemma}"]')

    return f"{info['start_query']}{info['corpora']}&cqp={cqp}&start=0&end=0"


@lru_cache(maxsize=4096)
def lemma_exists(language: str, lemma: str) -> bool:
    """Check whether a lemma has hits in the Korp corpus.

    Results are cached (per process) so that the same language/lemma pair
    is only ever looked up once against the remote Korp backend.
    """
    if language not in KORP_INFO:
        raise ValueError(f"Language '{language}' is not supported")

    url = _build_url(language, lemma)
    LOGGER.debug("Cache miss - querying Korp for: %s (%s)", lemma, language)

    try:
        with urllib.request.urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        LOGGER.warning("Failed to query Korp for %s (%s): %s", lemma, language, error)
        return False

    return bool(payload.get("hits", 0) > 0)


def cache_info():
    """Get cache statistics for the Korp lemma cache."""
    return lemma_exists.cache_info()
