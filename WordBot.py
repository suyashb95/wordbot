import requests,sys
from bs4 import BeautifulSoup
from config import bot_token,start_message,wordnik_url,wordnik_api_key
import json
from tornado.httpclient import AsyncHTTPClient
import tornado.web
from cachetools import LFUCache
from collections import Counter

class WordBot(tornado.web.RequestHandler):
	
	def __init__(self):
		self.offset = ''
		self.URL = 'https://api.telegram.org/bot' + bot_token
		self.session = requests.Session()
		self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
		self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
		self.http_client = AsyncHTTPClient()
		self.cache = LFUCache(maxsize = 100)
		self.startMessage = start_message
		
	def getUpdates(self):
		response = self.session.get(self.URL + '/getUpdates?offset=' + str(self.offset),verify=False)
		print "Got update"
		updates = json.loads(response.text)
		if updates['result']:
			self.offset = updates['result'][0]['update_id'] + 1
			query = updates['result'][0]['message']['text'].split()
			chat_id = updates['result'][0]['message']['chat']['id']
			self.session.get(self.URL + '/sendChatAction?chat_id=' + str(chat_id) +'&action=typing',verify=False)
			if query[0] == '/start':
				self.sendMessage(self.startMessage,chat_id)
			if len(query) > 1:
				word = ' '.join(query[1::]).lower()
				message = 'Word: ' +  word + '\n'
				message += '=' * (len(word) + 7) + '\n'
				if self.cache.get(word):
					wordData = self.cache.get(word)
				else:
					wordData = self.getWordData(word)
					self.cache.update({word:wordData})
				if query[0] in ['/define','/all']:
					message += "Definitions :-" + '\n'
					message += '-' * 17 + '\n'
					definitions = self.getDefinitions(wordData)
					if not definitions:
						message += 'No definitions found.\n'
					for definition in definitions:
						message += definition[0] + ': ' +  definition[1] + '\n\n'
				if query[0] in ['/synonyms','/all']:
					message += "Synonyms :-" + '\n'
					message += '-' * 17 + '\n'
					synonyms = self.getSynonyms(wordData)
					if not synonyms:
						message += 'No synonyms found.\n'
					for synonym in synonyms[:5]:
						message += synonym + '\n'
					message += '\n'
				if query[0] in ['/antonyms','/all']:
					message += "Antonyms :-" + '\n'
					message += '-' * 17 + '\n'
					antonyms = self.getAntonyms(wordData)
					if not antonyms:
						message += 'No antonyms found.\n\n'
					for antonym in antonyms[:5]:
						message += antonym + '\n'
				if query[0] in ['/use','/all']:
					message += "Examples :-" + '\n'
					message += '-' * 17 + '\n'
					examples = self.getExamples(wordData)
					if not examples:
						message += 'No examples found.'
					for index,example in enumerate(examples[:5]):
						message += str(index+1) + ") " + example + '\n\n'			
				self.sendMessage(message,chat_id)
		return True
	
	def getDefinitions(self,wordData):
		partCounter = Counter()
		definitions = []
		for definition in wordData:
			if partCounter[definition['partOfSpeech']] < 2:
				definitions.append((definition['partOfSpeech'],definition['text']))
				partCounter[definition['partOfSpeech']] += 1
		return definitions

	
	def getSynonyms(self,wordData):
		synonyms = []
		for relatedWords in wordData[0]['relatedWords']:
			if relatedWords['relationshipType'] == 'synonym':
				for synonym in relatedWords['words']:
					synonyms.append(synonym)
		for relatedWords in wordData[0]['relatedWords']:
			if relatedWords['relationshipType']  == 'same-context':
				for synonym in relatedWords['words']:
					synonyms.append(synonym)
		return synonyms
	
	def getAntonyms(self,wordData):
		antonyms = []
		for relatedWords in wordData[0]['relatedWords']:
			if relatedWords['relationshipType']  == 'antonym':
				for antonym in relatedWords['words']:
					antonyms.append(antonym)
		return antonyms
		
	def getExamples(self,wordData):
		examples = []
		for index,example in enumerate(wordData[0]['exampleUses']):
			examples.append(example['text'].replace('\n',''))
		return examples
		
	def getWordData(self,word):
		url1 = wordnik_url + word + '/definitions?api_key=' + wordnik_api_key
		url2 = wordnik_url + word + '/examples?api_key=' + wordnik_api_key
		url3 = wordnik_url + word + '/relatedWords?api_key=' + wordnik_api_key
		url4 = wordnik_url + word + '/etymologies?api_key=' + wordnik_api_key
		urls = [url1,url2,url3,url4]
		data = []
		for url in urls:
			response = self.session.get(url,verify=False)
			data.append(json.loads(response.text.encode('utf-8')))
		wordData = data[0]
		wordData[0]['exampleUses'] = data[1]['examples']
		wordData[0]['relatedWords'] = data[2]
		wordData[0]['etymologies'] = data[3]
		return wordData
		
	def sendMessage(self,message,chat_id):
		response = self.session.get(self.URL + '/sendMessage?chat_id=' + str(chat_id) +'&text=' + message.encode('utf-8'),verify=False)
		print "Sent message"
		