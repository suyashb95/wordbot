from typing import Optional 
from dataclass import Word, Definition

def italics(string: str) -> str:
    return f"_{string}_"


def bold(string: str) -> str:
    return f"*{string}*"


def format_definitions(word: Optional[Word] = None) -> Optional[str]:
    if not word or not word.definitions: return None
    message = f"{bold("Definitions")}\n"
    for definition in word.definitions:
        def_string = f"{definition.part_of_speech} : {definition.text}"
        message += f"{def_string}\n\n"
    return message


def format_example(word: Optional[Word] = None) -> Optional[str]:
    if not word or not word.example:
        return None
    message = f"{bold("Examples")}\n"
    message += f"{word.example}\n\n"
    return message


def format_synonyms(word: Optional[Word] = None) -> Optional[str]:
    if not word or not word.synonyms:
        return None
    message = f"{bold("Synonyms")}\n"
    for synonym in word.synonyms:
        message += f"{synonym}\n"
    return message


def format_antonyms(word: Optional[Word] = None) -> Optional[str]:
    if not word or not word.antonyms:
        return None
    message = f"{bold("Antonyms")}\n"
    for antonym in word.antonyms:
        message += f"{antonym}\n"
    return message
