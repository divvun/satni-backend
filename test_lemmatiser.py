import unittest

from nose2.tools import params

import lemmatiser


class TestLemmatiser(unittest.TestCase):
    def setUp(self):
        self.lemmatiser = lemmatiser.Lemmatiser()

    @params(('sme', 'vuolgin', ['vuolgit', 'vuolgi', 'vuolgin']),
            ('sme', 'vuolgimat', ['vuolgit', 'vuolgi', 'vuolgin']),
            ('sme', 'biillat', ['biila']))
    def test_lemmatiser(self, language, word, exptected_results):
        assert self.lemmatiser.lemmatise(language,
                                         word) == sorted(exptected_results)
