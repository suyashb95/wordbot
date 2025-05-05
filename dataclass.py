from typing import List, Optional
from dataclasses import dataclass


@dataclass
class Definition:
    part_of_speech: str
    text: str


@dataclass
class Word:
    word: str
    definitions: List[Definition]
    example: Optional[str]
    synonyms: List[str]
    antonyms: List[str]