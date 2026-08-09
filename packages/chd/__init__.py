from .dictionary import Dictionary, _VALID_EXT, choose_file_ext
from .character import Character
from .entry import Entry
from .grammar import Grammar, grammar_to_jsonl, grammar_to_txt
from .sentence import Sentence
from .convert_pleco_txt import (
    dump_json, 
    load_json,
    convert_pronunciations,
    convert_to_pleco_syntax,
    create_container,
    Writer, Loader
    )
from .unicode_characters import encode_pinyin, decode_pinyin
from .sql_methods import *

def convert_to_dtype(value: str):
    import ast
    # 1️⃣ Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # 2️⃣ Try float
    try:
        return float(value)
    except ValueError:
        pass

    # 3️⃣ Try dictionary, list, tuple, boolean, None, etc.
    try:
        parsed = ast.literal_eval(value)
        return parsed
    except (ValueError, SyntaxError):
        pass

    # 4️⃣ Otherwise, it’s just a plain string
    return value

