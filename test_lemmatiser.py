import unittest

from nose2.tools import params

import lemmatiser


class TestRegexes(unittest.TestCase):
    @params('+A+Sg+Nom', '+A+Pl+Nom', '+A+Attr', '+A+Ess')
    def test_adjective(self, adjective_value):
        assert lemmatiser.ADJECTIVE.match(adjective_value) is not None

    @params('+N+Sg+Nom', '+N+Pl+Nom', '+N+Attr', '+N+Ess', '+N+G3', '+N+G7',
            '+N+Ess', '+N+Nomag')
    def test_adjective(self, adjective_value):
        assert lemmatiser.NOUN.match(adjective_value) is not None

    @params('+V+Ind', '+V+Imprt', '+V+Cond', '+V+Pot', '+V+PrfPrc', '+V+Inf',
            '+V+PrsPrc')
    def test_verb(self, verb_value):
        assert lemmatiser.VERB.match(verb_value) is not None


class TestLemmatiser(unittest.TestCase):
    def setUp(self):
        self.lemmatisers = {}
        self.lemmatisers['sme'] = lemmatiser.Lemmatiser('sme')

    @params(('sme', 'vuolgin', ['vuolgi', 'vuolgin']),
            ('sme', 'vuolgimat', ['vuolgit', 'vuolgi', 'vuolgin']),
            ('sme', 'biillat', ['biila']))
    def test_lemmatiser(self, language, word, exptected_results):
        assert self.lemmatisers[language].lemmatise(word) == sorted(
            exptected_results)
