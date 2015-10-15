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
		self.partCounter = Counter()
		
	def getUpdates(self):
		response = self.session.get(self.URL + '/getUpdates?offset=' + str(self.offset),verify=False)
		print "Got update"
		updates = json.loads(response.text)
		if updates['result']:
			self.offset = updates['result'][0]['update_id'] + 1
			query = updates['result'][0]['message']['text'].split()
			chat_id = updates['result'][0]['message']['chat']['id']
			if query[0] == '/start':
				self.sendMessage(self.startMessage,chat_id)
			if len(query) > 1:
				word = ' '.join(query[1::]).lower()
				if self.cache.get(word):
					wordData = self.cache.get(word)
				else:
					wordData = self.getWord(word)
					self.cache.update({word:wordData})
				if query[0] == '/define':
					message = 'Word: ' +  word + '\n'
					message += '=' * (len(word) + 7) + '\n'
					for definition in wordData:
						if self.partCounter[definition['partOfSpeech']] < 2:
							message += definition['partOfSpeech'] + ': ' +  definition['text'] + '\n\n'
						self.partCounter[definition['partOfSpeech']] += 1
					self.sendMessage(message,chat_id)
					self.partCounter.clear()
				elif query[0] == '/synonyms':
					message = 'Word: ' +  word + '\n'
					message += '=' * (len(word) + 7) + '\n'
					message += "Synonyms :-" + '\n'
					message += '-' * 17 + '\n'
					for relatedWords in wordData[0]['relatedWords']:
						if relatedWords['relationshipType'] in ['synonym','same-context']:
							for synonym in relatedWords['words']:
								message += synonym + '\n'
					self.sendMessage(message,chat_id)
				elif query[0] == '/antonyms':
					message = 'Word: ' +  word + '\n'
					message += '=' * (len(word) + 7) + '\n'
					message += "Antonyms :-" + '\n'
					message += '-' * 17 + '\n'
					for relatedWords in wordData[0]['relatedWords']:
						if relatedWords['relationshipType'] in ['antonym']:
							for synonym in relatedWords['words']:
								message += synonym + '\n'
					self.sendMessage(message,chat_id)
				elif query[0] == '/use':
					message = 'Word: ' +  word + '\n'
					message += '=' * (len(word) + 7) + '\n'
					message += "Examples :-" + '\n'
					message += '-' * 17 + '\n'
					for index,example in enumerate(wordData[0]['exampleUses']):
						message += str(index+1) + ") " + example['text'].replace('\n','') + '\n\n'
					self.sendMessage(message,chat_id)
		return True
	
	def getWord(self,word):
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
		