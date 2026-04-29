from .dictionary import Dictionary, _VALID_EXT, choose_file_ext
from .character import Character
from .entry import Entry
from .grammar import Grammar, Sentence
from .convert_pleco_txt import (
    convert_pronunciations, convert_to_pleco_syntax, create_container,
    Writer, Loader)
from .unicode_characters import encode_pinyin, decode_pinyin
import ast
import json

def convert_to_dtype(value: str):
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

import os
from pathlib import Path
APP_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent

def load_json(path, default_dir=APP_DIR):
    path=path if default_dir==None else Path(default_dir)/path
    with open(path, "r") as f:
        settings = json.load(f)
    return settings

def dump_json(data,path, default_dir=APP_DIR):
    path=path if default_dir==None else Path(default_dir)/path
    with open(path, "w") as f:
        json.dump(data, f, indent=4,ensure_ascii=False)
    return True
