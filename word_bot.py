import telebot
import logging

from config import bot_token, start_message
from telebot import types
from dictionary_api import Dictionary
from utils import *

wordbot = telebot.TeleBot(bot_token)
dictionary = Dictionary()


def send_reply(message, text):
    if text != "":
        try:
            wordbot.send_chat_action(message.chat.id, "typing")
            wordbot.send_message(message.chat.id, text, parse_mode="markdown")
        except Exception as e:
            logging.error(e)
            logging.error(message)


@wordbot.message_handler(commands=["start", "help"])
def send_help_message(message):
    send_reply(message, start_message)


@wordbot.message_handler(
    commands=["define", "all", "synonyms", "antonyms", "use"], content_types=["text"]
)
def default_message_handler(message):
    if message.new_chat_member or not message.text:
        return
    query = message.text.replace("@anotherwordbot", "")
    reply = make_reply(query)
    send_reply(message, reply)


@wordbot.message_handler(commands=["today"], content_types=["text"])
def send_word_of_the_day(message):
    word_data = dictionary.get_word_of_the_day()
    query = "/define " + word_data["word"]
    reply = make_reply(query)
    send_reply(message, reply)


@wordbot.inline_handler(lambda query: True)
def handle_inline_query(inline_query):
    inline_answers = []
    query_word = inline_query.query
    if query_word or query_word != "":
        reply = make_reply("/define " + query_word)
        desc = reply if reply == "Word not found." else None
        query_result = types.InlineQueryResultArticle(
            "1",
            query_word,
            types.InputTextMessageContent(reply, parse_mode="markdown"),
            description=desc,
        )
        inline_answers = [query_result]
    wordbot.answer_inline_query(inline_query.id, inline_answers)


def make_reply(query):
    reply_message = ""
    query = query.split()
    if len(query) > 1:
        if query[0] in ["/define", "/synonyms", "/antonyms", "/use", "/all"]:
            word = " ".join(query[1::])
            reply_message = "{}\n\n".format(bold(word))
            word_data = dictionary.get_word(word)
            if word_data is None:
                return "Word not found"
            if query[0] in ["/define", "/all"]:
                reply_message += format_definitions(word_data)
            if query[0] in ["/synonyms", "/all"]:
                reply_message += format_synonyms(word_data) + "\n"
            if query[0] in ["/antonyms", "/all"]:
                reply_message += format_antonyms(word_data) + "\n"
            if query[0] in ["/use"]:
                reply_message += format_example(word_data)
    return reply_message


if __name__ == "__main__":
    wordbot.polling()
