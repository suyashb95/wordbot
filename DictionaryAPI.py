import requests
import sys
import json
import telebot

from config import *
from datetime import datetime
from cachetools import LFUCache
from collections import Counter
from wordnik import swagger, WordApi, WordsApi


class Dictionary(object):
    def __init__(self):
        self.word_api = WordApi.WordApi(swagger.ApiClient(wordnik_api_key, wordnik_api))
        self.wordoftheday_api = WordsApi.WordsApi(swagger.ApiClient(wordnik_api_key, wordnik_api))
        self.urbandictionary_api = urbandictionary_api
        self.dictionaryCache = LFUCache(maxsize = 1000)
        self.urbandictionaryCache = LFUCache(maxsize = 1000)
        self.wordOfTheDayCache = {}
        self.session = requests.Session()
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))

    def part_of_speech_filter(self, counter, pos):
        counter[pos] += 1
        return counter[pos] <= 2

    def get_word(self, word):
        if word in self.dictionaryCache: return self.dictionaryCache[word]
        definitions = self.word_api.getDefinitions(word, limit=20, useCanonical=True)
        if not definitions: return None
        counter = Counter()
        definitions = list(filter(lambda d: self.part_of_speech_filter(counter, d.partOfSpeech), definitions))
        examples = self.word_api.getExamples(word, limit=5, useCanonical=True)
        relatedWords = self.word_api.getRelatedWords(word, limitPerRelationshipType=5, useCanonical=True)
        if not relatedWords: relatedWords = []
        synonyms = [x for x in relatedWords if x.relationshipType == 'synonym']
        antonyms = [x for x in relatedWords if x.relationshipType == 'antonym']
        word_dict = {
            'word': word,
            'definitions': definitions,
            'example': sorted(examples.examples, key=lambda x: len(x.text))[0],
            'synonyms': synonyms[0].words if synonyms else [],
            'antonyms': antonyms[0].words if antonyms else []
        }
        self.dictionaryCache.update({word: word_dict})
        return word_dict

    def get_word_of_the_day(self):
        wordOfTheDay = self.wordOfTheDayCache.get(datetime.now().day, None)
        if wordOfTheDay and wordOfTheDay in self.dictionaryCache: return self.dictionaryCache[wordOfTheDay]
        wordOfTheDay = self.wordoftheday_api.getWordOfTheDay()
        relatedWords = self.word_api.getRelatedWords(wordOfTheDay.word, limitPerRelationshipType=5, useCanonical=True)
        synonyms = [x for x in relatedWords if x.relationshipType == 'synonym'] if relatedWords else []
        antonyms = [x for x in relatedWords if x.relationshipType == 'antonym'] if relatedWords else []
        word_dict = {
            'word': wordOfTheDay.word,
            'definitions': wordOfTheDay.definitions,
            'example': sorted(wordOfTheDay.examples, key=lambda x: len(x.text))[0],
            'synonyms': synonyms,
            'antonyms': antonyms
        }
        self.dictionaryCache.update({wordOfTheDay.word: word_dict})
        self.wordOfTheDayCache.clear()
        self.wordOfTheDayCache[datetime.now().day] = wordOfTheDay.word
        return word_dict

    def get_urbandictionary_word(self, word):
        if word in self.urbandictionaryCache: return self.urbandictionaryCache[word]
        url = '{}/define'.format(self.urbandictionary_api)
        url_params = {
            'term': word
        }
        res = self.session.get(url, params=url_params)
        json_res = json.loads(res.text)
        if not json_res['list']: return None
        word_dict = {
            'word': word,
            'definition': json_res['list'][0]['definition'],
            'example': json_res['list'][0]['example']
        }
        self.urbandictionaryCache.update({word: word_dict})
        return word_dict