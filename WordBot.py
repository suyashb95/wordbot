import requests,sys
from config import bot_token,start_message,wordnik_url,wordnik_api_key
import json,datetime
from cachetools import LFUCache
from collections import Counter

class WordBot():

	def __init__(self):
		self.offset = ''
		self.URL = 'https://api.telegram.org/bot' + bot_token
		self.session = requests.Session()
		self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
		self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
		self.cache = LFUCache(maxsize = 200)
		self.startMessage = start_message
		self.keyboard = {"keyboard":[["/define"],["/synonyms"],["/antonyms"],["/examples"],["/all"]]}

	def processUpdates(self):
		response = self.session.get(self.URL + '/getUpdates?offset=' + str(self.offset),verify=False)
		print "Got update"
		status = False
		updates = json.loads(response.text)
		if updates['result']:
			self.offset = updates['result'][0]['update_id'] + 1
			query = updates['result'][0]['message']['text']
			chat_id = updates['result'][0]['message']['chat']['id']
			self.session.get(self.URL + '/sendChatAction?chat_id=' + str(chat_id) +'&action=typing',verify=False)
			message = self.makeMessage(query)			
			status = self.sendMessage(message,chat_id)
		return status
	
	def makeMessage(self,query):
		message = self.startMessage
		if query == '/stop':
			message = 'Bot disabled.'
		elif query == '/today':
			wordData = self.getWordOfTheDay()
			query = '/define ' + wordData[0]['word']
		query = query.split()
		if len(query) > 1:
			if query[0] not in ['/define','/synonyms','/antonyms','/use','/all']:
				return self.startMessage
			word = ' '.join(query[1::]).lower()
			message = 'Word: ' +  word + '\n'
			message += '=' * (len(word) + 7) + '\n'
			if self.cache.get(word):
				print "Fetching from cache"
				wordData = self.cache.get(word)
			else:
				wordData = self.getWord(word)
				if wordData is None:
					return 'Word not found.'
				self.cache.update({word:wordData})
			if query[0] in ['/define','/all']:
				message += 'Definitions :-' + '\n'
				message += '-' * 20 + '\n'
				definitions = self.getDefinitions(wordData)
				if not definitions:
					message += 'No definitions found.\n'
				for definition in definitions:
					message += definition[0] + ': ' +  definition[1] + '\n\n'
			if query[0] in ['/synonyms','/all']:
				message += 'Synonyms :-' + '\n'
				message += '-' * 20 + '\n'
				synonyms = self.getSynonyms(wordData)
				if not synonyms:
					message += 'No synonyms found.\n'
				for synonym in synonyms[:5]:
					message += synonym + '\n'
				message += '\n'
			if query[0] in ['/antonyms','/all']:
				message += 'Antonyms :-' + '\n'
				message += '-' * 20 + '\n'
				antonyms = self.getAntonyms(wordData)
				if not antonyms:
					message += 'No antonyms found.\n'
				for antonym in antonyms[:5]:
					message += antonym + '\n'
				message += '\n'
			if query[0] in ['/use','/all']:
				message += 'Examples :-' + '\n'
				message += '-' * 18 + '\n'
				examples = self.getExamples(wordData)
				if not examples:
					message += 'No examples found.\n'
				for index,example in enumerate(examples[:5]):
					message += str(index+1) + ". " + example + '\n\n'
				message += '\n'		
		return message
		
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
		for index,example in enumerate(wordData[0]['examples']):
			examples.append(example['text'].replace('\n',''))
		return examples
		
	def getEtymology(self,wordData):
		etymologies = []
		for etymology in wordData[0]['etymologies']:
			etymologies.append(etymology)
		return etymology

	def getWord(self,word):
		url1 = wordnik_url + word + '/definitions?api_key=' + wordnik_api_key
		url2 = wordnik_url + word + '/examples?api_key=' + wordnik_api_key
		url3 = wordnik_url + word + '/relatedWords?api_key=' + wordnik_api_key
		urls = [url1,url2,url3]
		data = []
		for url in urls:
			try:
				response = self.session.get(url,verify=False)
				data.append(json.loads(response.text.encode('utf-8')))
			except ValueError:
				return None
		if not data[0]:
			return None
		wordData = data[0]
		wordData[0]['examples'] = data[1]['examples']
		wordData[0]['relatedWords'] = data[2]
		return wordData
	
	def getWordOfTheDay(self):
		today = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
		url = wordnik_url[:-10] + 'words.json/wordOfTheDay?api_key=' + wordnik_api_key + '&date=' + today
		wordData = []
		data = []
		response = self.session.get(url,verify = False)
		data.append(json.loads(response.text.encode('utf-8')))
		word = data[0]['word']
		if self.cache.get(word):
			wordData = self.cache.get(word)
			return wordData
		url = wordnik_url + word + '/relatedWords?api_key=' + wordnik_api_key
		wordData = [definition for definition in data[0]['definitions']]
		wordData[0]['examples'] = data[0]['examples']
		response = self.session.get(url,verify = False)
		relatedWords = json.loads(response.text)
		wordData[0]['relatedWords'] = relatedWords
		wordData[0]['word'] = word
		self.cache.update({word:wordData})
		return wordData			
			
	def sendMessage(self,message,chat_id):
		dataDict = {'chat_id':str(chat_id),
				'text':message.encode('utf-8'),
				'reply_markup':self.keyboard}
		response = self.session.post(self.URL + '/sendMessage',data = dataDict)
		if response.status_code == 200:
			return True
		else:
			return False
