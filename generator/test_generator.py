"""Test the generator engine."""

import unittest

from nose2.tools import params

from generator.generator import ParadigmGenerator


class TestParadigmGenerator(unittest.TestCase):
    """Test the ParadigmGenerator class."""

    def setUp(self):
        self.generator = ParadigmGenerator("sme")

    @params(("guolli", "N+Sg+Nom"), ("vuolgit", "V+IV+Inf"), ("vielgat", "A+Sg+Nom"))
    def test_generate(self, word, paradigm_template):
        """Test that the engine itself works as expected."""
        assert list(self.generator.generate(word, paradigm_template)) != []
