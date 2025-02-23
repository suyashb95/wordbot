Telegram English Dictionary Bot
===============================

This is a Telegram bot which fetches word definitions, synonyms, antonyms, usage examples and the word of the day from the Internet.
It uses Wordnik's API to fetch data. 

![alt tag](http://i.imgur.com/Jhvxues.png)

Usage
=====

* Visit this URL : https://telegram.me/LexicoBot 

* Or send a message to this username: @LexicoBot

* Inline mode is supported. 

### Allowed commands
* /define [word] : Gets the word's meaning.
* /synonyms [word] : Gets similar words.
* /antonyms [word] : Gets opposites.
* /use [word] : Gets usage examples. 
* /all [word] : Gets all of the above.
* /help : Send this message again.
* /today: Gets the word of the day.

Screenshots
===============

![alt tag](http://i.imgur.com/5bJNzkC.gif)

Requirements
------------

* tornado==6.3.3
* requests==2.31.0
* pyTelegramBotAPI==4.23.0
* cachetools==5.5.2
* aws_lambda_powertools==3.6.0
