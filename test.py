from packages.chd import (
    Dictionary, 
    Character, 
    convert_pronunciations, 
    convert_to_pleco_syntax, 
    decode_pinyin,
    encode_pinyin,
    dump_json,
    load_json,
    Loader,
    Sentence,
    Grammar
    )
import json
from pathlib import Path 
import re
import os

from packages.chd.unicode_characters import chinese_char, not_chinese_char, pleco_char
print(chinese_char)

# --------------------------------------
# directory="/media/selina/SHARE/MyProjects/ChD/dictionaries/MCD/"
# filename="MCD.db"
# # template='/home/selina/Applications/MyApps/ChineseDictionary/appdata/templates/dictionary_template.chd'
# categories=load_json('dictionary_categories.json','/home/selina/Applications/MyApps/ChineseDictionary/appdata/defaults')
# d1=Dictionary('MCD')
# d1.read('/media/selina/SHARE/MyProjects/ChD/dictionaries/MCD/MCD.jsonl',categories=categories)

# d2=Dictionary('Test')
# d2.read('/media/selina/SHARE/MyProjects/ChD/dictionaries/Test/Test.jsonl',categories=categories)
# print(d)
# # d.to_db(directory='/media/selina/SHARE/MyProjects/ChD/',src_file='/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/MCD.jsonl')
# # print(d[0].to_pleco_entry(template=template))
# # --------------------------------------
# # print(d[0].info())
# # d1.to_db(directory="/media/selina/SHARE/MyProjects/ChD/dictionaries/",filename='ALL.db',clean=True)
# # d2.to_db(directory="/media/selina/SHARE/MyProjects/ChD/dictionaries/",filename='ALL.db',clean=False)