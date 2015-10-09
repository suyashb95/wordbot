import requests,sys
from bs4 import BeautifulSoup
from config import base_url,bot_token,glosbe_url
import json
from tornado.httpclient import AsyncHTTPClient
import tornado.web

class WordBot(tornado.web.RequestHandler):
	
	def __init__(self):
		self.offset = ''
		self.URL = 'https://api.telegram.org/bot' + bot_token
		self.session = requests.Session()
		self.session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
		self.session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
		self.http_client = AsyncHTTPClient()
		self.startMessage = '''
							Hi! This is a multifuntional dictionary bot.
							
							Commands you can run
							=====================					
							/define [word] : Gets the word's meaning.(only this works)
							/origin [word] : Gets the word's etymology.
							/synonyms [word] : Gets similar words.
							/antonyms [word] : Gets opposites.
							/use [word] : Gets usage examples. 
							/all [word] : Gets all of the above.
							'''
							
		
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
				if query[0] == '/define':
					message = self.getWord(query[1])
					self.sendMessage(message,chat_id)
		return True
	
	def getWord(self,word):
		response = self.session.get(glosbe_url + str(word),verify=False)
		#soup = BeautifulSoup(response.text)
		#data = soup.findAll('div',{'class':'def-list'})
		data = json.loads(response.text)
		message = ''
		try:
			for meaning in data['tuc'][0]['meanings']:
				message = message + meaning['text'].encode('utf-8') + '\n'
		except KeyError:
			pass
		print "Fetched word"
		return message
		#return ('\n'.join(data[0].text.strip().split('\n\n'))).encode('utf-8')	
		
	def sendMessage(self,message,chat_id):
		response = self.session.get(self.URL + '/sendMessage?chat_id=' + str(chat_id) +'&text=' + str(message),verify=False)
		print "Sent message"
		#response = self.http_client.fetch(self.URL + '/sendMessage?chat_id=' + str(chat_id) +'&text=' + str(message))
		