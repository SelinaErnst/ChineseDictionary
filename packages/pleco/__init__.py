# from .convert_instructions import plecoformat
# from .possible_instructions #import possible_instructions, adjustables
# from .loader import read_plecotxt
from .dictionary import dictionary
from .character import character
from .entry import entry
from .convert_instructions import plecoformat
from .printentry import encode_pinyin, decode_pinyin
import ast

def detect_type(value: str):
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