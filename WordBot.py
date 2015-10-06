import requests,sys
from bs4 import BeautifulSoup
from config import base_url,bot_token,glosbe_url
import json

class WordBot():
	
	def __init__(self):
		self.offset = ''
		self.URL = 'https://api.telegram.org/bot' + bot_token
		self.session = requests.Session()
		self.startMessage = '''
							Hi! This is a multifuntional dictionary bot.
							
							Commands you can run(Sans the square braces)
							============================================
							
							/define [word] : Gets the word's meaning.(Only this one works for now.)
							/origin [word] : Gets the word's etymology.(/define etymology maybe? haha)
							/synonyms [word] : Gets similar words.
							/antonyms [word] : Gets opposites.
							/use [word] : Gets usage examples. 
							/all [word] : Gets all of the above.
							'''
							
		
	def getUpdates(self):
		response = self.session.get(self.URL + '/getUpdates?offset=' + str(self.offset))
		updates = json.loads(response.text)
		if updates['result']:
			self.offset = updates['result'][0]['update_id'] + 1
			query = updates['result'][0]['message']['text'].split()
			if len(query) > 1:
				if query[0] == '/define':
					message = self.getWord(query[1])
					chat_id = updates['result'][0]['message']['chat']['id']
					self.sendMessage(message,chat_id)
	
	def getWord(self,word):
		response = self.session.get(glosbe_url + str(word).replace('/',''))
		#soup = BeautifulSoup(response.text)
		#data = soup.findAll('div',{'class':'def-list'})
		print response.text.encode('utf-8')
		data = json.loads(response.text)
		message = ''
		try:
			for meaning in data['tuc'][0]['meanings']:
				message = message + meaning['text'].encode('utf-8') + '\n'
		except KeyError:
			pass
		return message
		#return ('\n'.join(data[0].text.strip().split('\n\n'))).encode('utf-8')	
		
	def sendMessage(self,message,chat_id):
		response = self.session.get(self.URL + '/sendMessage?chat_id=' + str(chat_id) +'&text=' + str(message))
		print response.status_code
		