import requests

from config import *
from datetime import datetime
from cachetools import LFUCache
from collections import Counter
from wordnik import swagger, WordApi, WordsApi
from dataclass import Word, Definition

class Dictionary(object):
    def __init__(self):
        self.word_api = WordApi.WordApi(swagger.ApiClient(wordnik_api_key, wordnik_api))
        self.dictionary_cache = LFUCache(maxsize=1000)
        self.session = requests.Session()
        self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=5))
        self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=5))

    def part_of_speech_filter(self, counter, pos):
        counter[pos] += 1
        return counter[pos] <= 2

    def is_valid_definition(self, definition):
        return definition.partOfSpeech and definition.text

    def get_word(self, word):
        if word in self.dictionary_cache:
            return self.dictionary_cache[word]
        definitions = self.word_api.getDefinitions(word, limit=20, useCanonical=True)
        if not definitions:
            return None
        counter = Counter()
        definitions = list(
            filter(
                lambda d: self.part_of_speech_filter(counter, d.partOfSpeech)
                and self.is_valid_definition(d),
                definitions,
            )
        )
        examples = self.word_api.getExamples(word, limit=5, useCanonical=True)
        relatedWords = self.word_api.getRelatedWords(
            word, limitPerRelationshipType=5, useCanonical=True
        )
        if not relatedWords:
            relatedWords = []
        synonyms = [x.words for x in relatedWords if x.relationshipType == "synonym"]
        antonyms = [x.words for x in relatedWords if x.relationshipType == "antonym"]
        word_dict = Word(
            word=word,
            definitions=[Definition(part_of_speech=d.partOfSpeech, text=d.text) for d in definitions],
            example=sorted(examples.examples, key=lambda x: len(x.text))[0].text,
            synonyms=synonyms,
            antonyms=antonyms,
        )
        self.dictionary_cache.update({word: word_dict})
        return word_dict
