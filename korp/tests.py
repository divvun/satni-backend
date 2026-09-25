"""Tests for the Korp client and its lemma-existence caching."""

import json
import unittest
from unittest import mock

from korp import client


class TestBuildUrl(unittest.TestCase):
    """Test the Korp query URL construction."""

    def test_build_url_encodes_cqp_query(self):
        url = client._build_url("sme", "muorra")

        self.assertIn("https://gtweb.uit.no/korp/backend-sme/query?corpus=", url)
        self.assertIn("cqp=%5Blemma+%3D+%22muorra%22%5D", url)
        self.assertIn("&start=0&end=0", url)


class TestLemmaExists(unittest.TestCase):
    """Test the cached lemma_exists lookup."""

    def setUp(self):
        client.lemma_exists.cache_clear()

    def tearDown(self):
        client.lemma_exists.cache_clear()

    def _mock_response(self, payload):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps(payload).encode("utf-8")
        return response

    @mock.patch("korp.client.urllib.request.urlopen")
    def test_lemma_exists_true(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            {"hits": 3}
        ).encode("utf-8")

        self.assertTrue(client.lemma_exists("sme", "muorra"))
        mock_urlopen.assert_called_once()

    @mock.patch("korp.client.urllib.request.urlopen")
    def test_lemma_exists_false_when_no_hits(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            {"hits": 0}
        ).encode("utf-8")

        self.assertFalse(client.lemma_exists("sme", "asdfasdf"))

    @mock.patch("korp.client.urllib.request.urlopen")
    def test_lemma_exists_is_cached(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value.read.return_value = json.dumps(
            {"hits": 1}
        ).encode("utf-8")

        client.lemma_exists("sme", "muorra")
        client.lemma_exists("sme", "muorra")

        mock_urlopen.assert_called_once()

    @mock.patch("korp.client.urllib.request.urlopen")
    def test_lemma_exists_handles_errors_gracefully(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("timed out")

        self.assertFalse(client.lemma_exists("sme", "muorra"))

    def test_lemma_exists_raises_for_unsupported_language(self):
        with self.assertRaises(ValueError):
            client.lemma_exists("eng", "tree")
