import requests, sys, json
import httplib, urllib2, telebot
from config import bot_token, start_message, wordnik_url, wordnik_api_key
from datetime import datetime
from cachetools import LFUCache
from collections import Counter

def patch_http_response_read(func):
    def inner(*args):
        try:
            return func(*args)
        except httplib.IncompleteRead, e:
            return e.partial

    return inner

httplib.HTTPResponse.read = patch_http_response_read(httplib.HTTPResponse.read)

class Dictionary(object):
    def __init__(self):
        self.dictionaryCache = LFUCache(maxsize = 1000)
        self.urbandictionaryCache = LFUCache(maxsize = 1000)
        self.wordOfTheDayCache = {}
        self.session = requests.Session()
        self.session.mount('http://', requests.adapters.HTTPAdapter(max_retries=5))
        self.session.mount('https://', requests.adapters.HTTPAdapter(max_retries=5))

    def updateCache(self, word, wordData):
        dataDict = {}
        definitionText = '*Definitions*' +'\n'
        synonymsText = '*Synonyms*' + '\n'
        antonymsText = '*Antonyms*' + '\n'
        examplesText = '*Examples*' + '\n'
        definitions = self.getDefinitions(wordData)
        synonyms = self.getSynonyms(wordData)
        antonyms = self.getAntonyms(wordData)
        examples = self.getExamples(wordData)
        if not definitions:
            definitionText += 'No definitions found.\n'
        if not synonyms:
            synonymsText += 'No synonyms found.\n'
        if not antonyms:
            antonymsText += 'No antonyms found.\n'
        if not examples:
            examplesText += 'No examples found.\n'      
        for definition in definitions:
            if definition[0]:
                definitionText += definition[0] + ': '
            definitionText += definition[1] + '\n\n'    
        definitionText = definitionText[:-1]    
        for synonym in synonyms[:3]:
            synonymsText += synonym + '\n'
        for antonym in antonyms[:3]:
            antonymsText += antonym + '\n'
        for index, example in enumerate(examples[:3]):
            examplesText += str(index+1) + '. ' + example + '\n\n'
        examplesText = examplesText[:-1]
        dataDict['word'] = word
        dataDict['definitions'] = definitionText
        dataDict['synonyms'] = synonymsText
        dataDict['antonyms'] = antonymsText
        dataDict['examples'] = examplesText
        self.dictionaryCache.update({word:dataDict})
        return dataDict
            
    def getDefinitions(self, wordData):
        partCounter = Counter()
        definitions = []
        for definition in wordData:
            if 'partOfSpeech' in definition.keys() and partCounter[definition['partOfSpeech']] < 2:
                definitions.append( 
                    ('_' + definition['partOfSpeech'] + '_ ', 
                    definition['text'])
                )
                partCounter[definition['partOfSpeech']] += 1
            else:
                definitions.append(('',definition['text']))
        return definitions

    def getSynonyms(self, wordData):
        synonyms = []
        for relatedWords in wordData[0]['relatedWords']:
            if relatedWords['relationshipType'] == 'synonym':
                for synonym in relatedWords['words']:
                    synonyms.append(synonym)
        
        for relatedWords in wordData[0]['relatedWords']:
            if relatedWords['relationshipType']  == 'cross-reference':
                for synonym in relatedWords['words']:
                    synonyms.append(synonym)    
        return synonyms

    def getAntonyms(self, wordData):
        antonyms = []
        for relatedWords in wordData[0]['relatedWords']:
            if relatedWords['relationshipType']  == 'antonym':
                for antonym in relatedWords['words']:
                    antonyms.append(antonym)
        return antonyms

    def getExamples(self, wordData):
        examples = []
        for index,example in enumerate(wordData[0]['examples']):
            examples.append(example['text'].replace('\n',''))
        return examples
        
    def getEtymology(self, wordData):
        etymologies = []
        for etymology in wordData[0]['etymologies']:
            etymologies.append(etymology)
        return etymology

    def getWord(self, word):
        if '#' in word:
            return None
        def_url = wordnik_url + word + '/definitions?limit=15&api_key=' + wordnik_api_key
        example_url = wordnik_url + word + '/examples?api_key=' + wordnik_api_key
        related_url = wordnik_url + word + '/relatedWords?api_key=' + wordnik_api_key
        urls = [def_url, example_url, related_url]
        data = []
        for url in urls:
            try:
                response = self.session.get(url, verify=False)
                if response.status_code != 200:
                    return None
                data.append(json.loads(response.text.encode('utf-8')))
            except ValueError:
                return None
        if not data[0]:
            return None
        wordData = data[0]
        try:
            wordData[0]['examples'] = data[1]['examples']
        except KeyError:
            wordData[0]['examples'] = []
        try:
            wordData[0]['relatedWords'] = data[2]
        except KeyError:
            wordData[0]['relatedWords'] = []
        return self.updateCache(word,wordData)

    def getUrbandictionaryWord(self, word):
        api_url = 'http://api.urbandictionary.com/v0/define?term='
        #response = requests.get(api_url+word, verify=False)
        response = urllib2.urlopen(api_url + word)
        data = json.loads(response.read().decode('utf-8'))
        if data.get('result_type', None) == 'no_results' or not data['list']:
            return None
        wordData = {}
        wordData['definition'] = '*Definition*' + '\n'
        wordData['example'] = '*Example*'  + '\n'
        try:
            if data['list'][0]['definition']:
                wordData['definition'] += data['list'][0]['definition'].strip() + '\n'
            else:
                return None
        except KeyError:
            return None
        try:
            if data['list'][0]['example']:
                wordData['example'] += data['list'][0]['example'].strip() + '\n'
            else:
                wordData['example'] += 'No example found.'
        except KeyError:
            wordData['example'] += 'No example found.'          
        self.urbandictionaryCache.update({word:wordData})
        return wordData

    def getWordOfTheDay(self):
        wordOfTheDay = self.wordOfTheDayCache.get(datetime.now().day, None)
        if wordOfTheDay is None:
            today = datetime.strftime(datetime.now(), '%Y-%m-%d')
            url = wordnik_url[:-10] + 'words.json/wordOfTheDay?api_key=' + wordnik_api_key + '&date=' + today
            data = []
            response = self.session.get(url, verify=False)
            try:
                data.append(json.loads(response.text.encode('utf-8')))
            except ValueError:
                return None
            wordOfTheDay = data[0]['word']
            self.wordOfTheDayCache.clear()
            self.wordOfTheDayCache[datetime.now().day] = wordOfTheDay
        else:
            pass
        wordData = self.dictionaryCache.get(wordOfTheDay)
        if not wordData:
            url = wordnik_url + wordOfTheDay + '/relatedWords?api_key=' + wordnik_api_key
            wordData = [definition for definition in data[0]['definitions']]
            for definition in wordData:
                definition['attributionText'] = ''
            wordData[0]['examples'] = data[0]['examples']
            response = self.session.get(url, verify = False)
            relatedWords = json.loads(response.text)
            wordData[0]['relatedWords'] = relatedWords
            wordData[0]['word'] = wordOfTheDay
            return self.updateCache(wordOfTheDay, wordData) 
        else:
            return wordData 