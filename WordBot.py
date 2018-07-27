import requests, sys, json
import httplib, urllib2, telebot
from config import bot_token, start_message, wordnik_url, wordnik_api_key
from datetime import datetime
from collections import Counter
from telebot import types
from time import sleep
from DictionaryAPI import Dictionary

wordbot = telebot.TeleBot(bot_token)
dictionary = Dictionary()

@wordbot.message_handler(commands = ['start', 'help'])
def send_help_message(message):
    wordbot.send_chat_action(message.chat.id, 'typing')
    wordbot.send_message(message.chat.id, start_message, parse_mode='markdown')

@wordbot.message_handler(commands = ['define', 'all', 'synonyms', 'antonyms', 'ud', 'use'], content_types=['text'])
def default_message_handler(message):
    if message.new_chat_member or not message.text:
        return
    query = message.text.replace('@LexicoBot', '')
    reply = make_reply(query)
    if reply != '':
        wordbot.send_chat_action(message.chat.id, 'typing')
        wordbot.send_message(message.chat.id, reply, parse_mode='markdown')

@wordbot.message_handler(commands = ['today'], content_types = ['text'])
def send_word_of_the_day(message):
    wordData = dictionary.getWordOfTheDay()
    if wordData is None:
        return
    query = '/define ' + wordData['word']
    reply = make_reply(query)
    if reply != '':
        wordbot.send_chat_action(message.chat.id, 'typing')
        wordbot.send_message(message.chat.id, reply, parse_mode='markdown')

@wordbot.inline_handler(lambda query: True)
def handle_inline_query(inline_query):
    default_word = dictionary.getWordOfTheDay()
    inline_answers = []
    if default_word:
        default_result = types.InlineQueryResultArticle(
            '1', 
            'Word of the day', 
            types.InputTextMessageContent(
                '*' + default_word['word'] + '*\n' + default_word['definitions'],
                parse_mode='markdown'
            ),
            description=default_word['word']
        )
        inline_answers = [default_result]
    query_word = inline_query.query
    if query_word or query_word != '':
        reply = make_reply('/define ' + query_word)
        desc = reply if reply == 'Word not found.' else None
        query_result = types.InlineQueryResultArticle('2', 
            query_word, 
            types.InputTextMessageContent(
                reply,
                parse_mode='markdown'
            ),
            description=desc
        )
        inline_answers = [query_result]
    wordbot.answer_inline_query(inline_query.id, inline_answers)   
       
def make_reply(query):
    reply_message = ''
    query = query.split()
    if len(query) > 1:
        if query[0] in ['/define', '/synonyms', '/antonyms', '/use', '/all', '/ud']:
            word = ' '.join(query[1::])
            reply_message = '*' +  word + '*\n\n'
            if query[0] != '/ud':
                wordData = dictionary.dictionaryCache.get(word)
                if wordData is None:
                    wordData = dictionary.getWord(word)
                if wordData is None:
                    return 'Word not found.'
                if query[0] in ['/define','/all']:
                    reply_message += wordData['definitions'] + '\n'
                if query[0] in ['/synonyms','/all']:
                    reply_message += wordData['synonyms'] + '\n'
                if query[0] in ['/antonyms','/all']:
                    reply_message += wordData['antonyms'] + '\n'
                if query[0] in ['/use']:
                    reply_message += wordData['examples'] + '\n'
            else:
                wordData = dictionary.urbandictionaryCache.get(word)
                if wordData is None:
                    wordData = dictionary.getUrbandictionaryWord(word)
                if wordData is None:
                    return 'Word not found'
                reply_message += wordData['definition'] + '\n'
                reply_message += wordData['example']    
    return reply_message

def runner(self):
    updates = wordbot.get_updates()
    latest_update = min([update.update_id for update in updates])
    while True:
        try:
            for update in updates:
                if update.message.text:
                    wordbot.handle_message(update.message)
                if update.update_id > latest_update:
                    latest_update = update.update_id
            sleep(.20)
            updates = wordbot.get_updates(offset=latest_update+1)
        except:
            sys.exit(0)

if __name__ == '__main__':
    wordbot.polling()