### Telegram English Dictionary Bot

This is a Telegram bot which fetches word definitions, synonyms, antonyms, usage examples and the word of the day from the Internet.
It uses Wordnik's API to fetch data. 

#### Cloning/Deploying a version of this bot

* use [@BotFather](https://telegram.me/BotFather) to create a new bot and get a token
* get an API key from [wordnik](https://www.wordnik.com/)
* create `config.py` from the example file with the API and bot token 
* deploy the lambda function using GCloud console
* set the telegram message webhool using `set_webhook.sh` or by calling the `{google_cloud_app_url}/setWebhook` API


#### Usage

* Visit [the bot](https://telegram.me/anotherwordbot) or send a message to @anotherwordbot
* Inline mode is supported. 

#### Allowed commands

* /define [word] : Gets the word's meaning.
* /synonyms [word] : Gets similar words.
* /antonyms [word] : Gets opposites.
* /use [word] : Gets usage examples. 
* /all [word] : Gets all of the above.
* /help : Send this message again.

![alt tag](http://i.imgur.com/5bJNzkC.gif)

#### Requirements

* tornado==6.3.3
* requests==2.31.0
* pyTelegramBotAPI==4.23.0
* cachetools==5.5.2
