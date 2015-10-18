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
			query = '/define ' + wordData['word']
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
			if query[0] in ['/define','/all']:
				message += wordData['definitions'] + '\n'
			if query[0] in ['/synonyms','/all']:
				message += wordData['synonyms'] + '\n'
			if query[0] in ['/antonyms','/all']:
				message += wordData['antonyms'] + '\n'
			if query[0] in ['/use','/all']:
				message += wordData['examples'] + '\n'	
		return message
	
	def updateCache(self,word,wordData):
		dataDict = {}
		definitionText = 'Definitions :-' + '\n'
		definitionText += '-' * 20 + '\n'
		synonymsText = 'Synonyms :-' + '\n'
		synonymsText += '-' * 20 + '\n'
		antonymsText = 'Antonyms :-' + '\n'
		antonymsText += '-' * 20 + '\n'
		examplesText = 'Exmaples :-' + '\n'
		examplesText += '-' * 20 + '\n'
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
			
		for definition in self.getDefinitions(wordData):
			definitionText += definition[0] + '\n' + definition[1] + ': ' +  definition[2] + '\n\n'
		for synonym in synonyms[:5]:
			synonymsText += synonym + '\n'
		for antonym in antonyms[:5]:
			antonymsText += antonym + '\n'
		for index,example in enumerate(examples[:5]):
			examplesText += str(index+1) + ". " + example + '\n\n'
		
		dataDict['word'] = word
		dataDict['definitions'] = definitionText
		dataDict['synonyms'] = synonymsText
		dataDict['antonyms'] = antonymsText
		dataDict['examples'] = examplesText
		self.cache.update({word:dataDict})
		return dataDict 
			
	def getDefinitions(self,wordData):
		partCounter = Counter()
		definitions = []
		for definition in wordData:
			if partCounter[definition['partOfSpeech']] < 2:
				definitions.append((definition['attributionText'],definition['partOfSpeech'],definition['text']))
				partCounter[definition['partOfSpeech']] += 1
		return definitions


	def getSynonyms(self,wordData):
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
		try:
			wordData[0]['examples'] = data[1]['examples']
		except KeyError:
			wordData[0]['examples'] = []
		try:
			wordData[0]['relatedWords'] = data[2]
		except KeyError:
			wordData[0]['relatedWords'] = []
		return self.updateCache(word,wordData)
	
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
		for definition in wordData:
			definition['attributionText'] = ''
		wordData[0]['examples'] = data[0]['examples']
		response = self.session.get(url,verify = False)
		relatedWords = json.loads(response.text)
		wordData[0]['relatedWords'] = relatedWords
		wordData[0]['word'] = word
		return self.updateCache(word,wordData)		
			
	def sendMessage(self,message,chat_id):
		dataDict = {'chat_id':str(chat_id),
				'text':message.encode('utf-8'),
				'reply_markup':self.keyboard}
		response = self.session.post(self.URL + '/sendMessage',data = dataDict)
		if response.status_code == 200:
			return True
		else:
			return False
