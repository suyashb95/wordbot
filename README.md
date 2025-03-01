Telegram English Dictionary Bot
===============================

This is a Telegram bot which fetches word definitions, synonyms, antonyms, usage examples and the word of the day from the Internet.
It uses Wordnik's API to fetch data. 

Cloning/Deploying a version of this bit
=====

* use @BotFather to create a new bot and get a token
* get an API key from wordnik
* create `config.py` from the example file with the API and bot token 
* deploy the lambda function using AWS CLI
* set the telegram message webhool using `set_webhook.sh`

### Allowed commands
* /define [word] : Gets the word's meaning.
* /synonyms [word] : Gets similar words.
* /antonyms [word] : Gets opposites.
* /use [word] : Gets usage examples. 
* /all [word] : Gets all of the above.
* /help : Send this message again.
* /today: Gets the word of the day.


Usage
=====

* Visit this URL : https://telegram.me/anotherwordbot 

* Or send a message to this username: @anotherwordbot

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
