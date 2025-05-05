import telebot
import logging

from config import bot_token, start_message
from telebot import types
from dictionary_api import Dictionary
from utils import *

wordbot = telebot.TeleBot(bot_token)
dictionary = Dictionary()


def send_reply(message, text):
    wordbot.send_chat_action(message.chat.id, "typing")
    wordbot.send_message(message.chat.id, text, parse_mode="markdown")

def get_query_phrase(text):
    query = text.replace("@anotherwordbot", "")
    return ' '.join(query.split()[1::])


@wordbot.message_handler(commands=["start", "help"])
def send_help_message(message):
    send_reply(message, start_message)


@wordbot.message_handler(
    commands=["all"], content_types=["text"]
)
def all_handler(message):
    word = get_query_phrase(message.text)
    word_data = dictionary.get_word(word)
    reply = f"{bold(word)}\n\n{format_definitions(word_data)}" if word_data else "Definitions not found."
    reply += f"{format_synonyms(word_data) if word_data.synonyms else "Synonyms not found"}\n"
    reply += f"{format_antonyms(word_data) if word_data.antonyms else "Antonyms not found"}\n"
    reply += f"{format_example(word_data) if word_data.example else "Examples not found"}\n"
    send_reply(message, reply)


@wordbot.message_handler(
    commands=["define"], content_types=["text"]
)
def definitions_handler(message):
    word = get_query_phrase(message.text)
    word_data = dictionary.get_word(word)
    reply = f"{bold(word)}\n\n{format_definitions(word_data)}" if word_data.definitions else "Definitions not found."
    send_reply(message, reply)

@wordbot.message_handler(
    commands=["use"], content_types=["text"]
)
def examples_handler(message):
    word = get_query_phrase(message.text)
    word_data = dictionary.get_word(word)
    reply = f"{bold(word)}\n\n{format_example(word_data) if word_data.example else 'Antonyms not found.'}"
    send_reply(message, reply)

@wordbot.message_handler(
    commands=["synonyms"], content_types=["text"]
)
def synonyms_handler(message):
    word = get_query_phrase(message.text)
    word_data = dictionary.get_word(word)
    reply = f"{bold(word)}\n\n{format_synonyms(word_data) if word_data.synonyms else 'Synonyms not found.'}"
    send_reply(message, reply)


@wordbot.message_handler(
    commands=["antonyms"], content_types=["text"]
)
def antonyms_handler(message):
    word = get_query_phrase(message.text)
    word_data = dictionary.get_word(word)
    reply = f"{bold(word)}\n\n{format_antonyms(word_data) if word_data.antonyms else 'Antonyms not found.'}"
    send_reply(message, reply)


@wordbot.inline_handler(lambda query: True)
def handle_inline_query(inline_query):
    inline_answers = []
    query_word = inline_query.query
    if query_word or query_word != "":
        word_data = dictionary.get_word(query_word)
        reply = f"{bold(query_word)}\n\n{format_definitions(word_data) if word_data else 'Word not found.'}"
        desc = reply if reply == "Word not found." else None
        query_result = types.InlineQueryResultArticle(
            "1",
            query_word,
            types.InputTextMessageContent(reply, parse_mode="markdown"),
            description=desc,
        )
        inline_answers = [query_result]
    wordbot.answer_inline_query(inline_query.id, inline_answers)


if __name__ == "__main__":
    wordbot.polling()
