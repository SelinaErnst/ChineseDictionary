from packages.chd import (
    Dictionary, 
    Character, 
    convert_pronunciations, 
    convert_to_pleco_syntax, 
    Loader,
    Sentence,
    Grammar
    )
import json
from pathlib import Path 
import re
import os

# def load_json(path, default_dir):
#     path=path if default_dir==None else Path(default_dir)/path
#     with open(path, "r") as f:
#         settings = json.load(f)
#     return settings
from packages.chd import decode_pinyin, encode_pinyin
from packages.chd import dump_json, load_json
from packages.chd.unicode_characters import chinese_char, not_chinese_char, pleco_char

# --------------------------------------
# template='/home/selina/Applications/MyApps/ChineseDictionary/appdata/templates/dictionary_template.chd'
# categories=load_json('dictionary_categories.json','/home/selina/Applications/MyApps/ChineseDictionary/appdata/defaults')
# d=Dictionary('DBTest')
# d.read('/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/MCD.jsonl',file_format='jsonl',categories=categories)
# # print(d)
# d.to_db(directory='/media/selina/SHARE/MyProjects/ChD/',src_file='/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/MCD.jsonl')
# print(d[0].to_pleco_entry(template=template))
# --------------------------------------

# gr_path='/media/selina/SHARE/MyProjects/ChD/grammar/grammar.jsonl'
# template='/home/selina/Applications/MyApps/ChineseDictionary/appdata/templates/grammar_template.chd'
# grammar_list=[]

# def read_grammar_jsonl(path):
#     with open(path,'r') as file:
#         json_list = list(file)
#     for json_str in json_list:
#         entry=json.loads(json_str)
#         grammar_entry = Grammar(**entry)
#         grammar_list.append(grammar_entry)
#     return grammar_list

# def grammar_to_jsonl(grammar:list,path):
#     with open(path,'w') as outfile:
#         for g in grammar:
#             json.dump(g.to_dict(), outfile, indent=None, ensure_ascii=False)
#             outfile.write('\n')
            
# def grammar_to_txt(grammar,path,template):
#     with open(path,'w') as file:
#         text=[]
#         for g in grammar:
#             text.append(g.to_text(template=template))
#         file.write('\n'.join(text))
        
# grammar_list = read_grammar_jsonl(path=gr_path)
# print(grammar_list)
# gr={
#     'level':'',
#     'title':'',
#     'subtitle':'',
#     'structures':[''],
#     'opposite_structures':[''],
#     'explanation':"",
# }


# characters = [
#     ('…又可以…','','you4ke3yi3'),
#     ('…又得…','','you4dei3'),
#     ('…又能…','','you4neng2'),
#     ('…又是…','','you4shi4'),
#     ('…又要…','','you4yao4'),
# ]
# opposite_characters = [
#     ("…又…了。", "", "you4le5"),
#     ("…再…", "", "zai4"),
# ]

# explanation = """
# 又 [yòu] is sometimes used to express that something that has happened before is going to happen in the immediate future and has not happened yet. 
# It usually appears with 要 [yào], 可以 [kěyǐ], 能 [néng], 是 [shì], or 得 [děi]. 
# This usage often expresses exasperation or impatience with something happening yet again, but sometimes it's more neutral, or even happy.

# For general repetition of an action in the future, 再 is usually used. 
# """
# explanation = explanation.strip('\n')

# gr={
#     'level':'B1',
#     'title':'Repetition of Past Action with 又',
#     'subtitle':'Expresses repetition of a previous action in the immediate future',
#     'structures':[
#         'Subj. + 又 + (Aux. +) Verb + Obj. (+ 了) (repetition will happen immediately)'
#         ],
#     'opposite_structures':[
#         "Subj. + 再 + Verb (repetition will happen)"
#         "(Subj. +) 又 + Verb + 了 (repetition has happened)"
#         ],
#     'explanation':explanation
# }


# sentences = [
#     Sentence('老板请客，又可以吃大餐了.','lao3ban3 qing3ke4, you4 ke3yi3 chi1 da4can1 le5.',"The boss is going to treat us. We can have a big meal again!"),
#     Sentence('夏天快到了，又可以吃冰淇淋了.','lao3ban3 qing3ke4, you4 ke3yi3 chi1 da4can1 le5.',"It's almost summer, and we can eat ice cream again!"),
#     Sentence('昨天银行关门，事情没办成，今天又得请假去银行了。.','xia4tian1 kuai4 dao4 le5, you4 ke3yi3 chi1 bing1qi2lin2 le5."',"Yesterday the bank was closed and things were not done. Today, I have to ask for leave to go to the bank again."),
#     Sentence('快过年了，我们又能拿红包了.','kuai4 guo4nian2 le5, wo3men5 you4 neng2 na2 hong2bao1 le5.',"It's almost Chinese New Year. We can get our red packets [of money] again!"),
#     Sentence('明天又是星期一！','ming2tian1 you4shi4 xing1qi1yi1!',"Tomorrow is Monday again."),
#     Sentence('今年备不住又是个丰收年。','jin1nian2 bei4bu2zhu4 you4shi4ge5 feng1shou1nian2.',"This year may be another good year."),
#     {"text": "又下雨了。", "pronunciation": "tā nánpěngyou yòugāoyòushuài.", "translation": "It rained again."}, 
#     {"text": "你又迟到了。", "pronunciation": "nǐ yòu chídào le.", "translation": "You're late again."}, 
#     {"text": "宝宝又哭了。", "pronunciation": "bǎobao yòukūle.", "translation": "The baby is crying again."}, 
#     {"text": "我又忘了。", "pronunciation": "wǒ yòu wàng le.", "translation": "I forgot again."}, 
#     {"text": "这个人又来了。", "pronunciation": "zhègerén yòuláile.", "translation": "This guy is here again."}, 
#     {"text": "我昨天又吃火锅了。", "pronunciation": "wǒ zuótiān yòu chī huǒguō le.", "translation": "I ate hot pot again yesterday."}
# ]
# done=True

# g=Grammar(**gr)
# g.add_character(characters)
# g.add_opp_character(opposite_characters)
# g.add_sentence(sentences)

# if not done: print(g.to_text(template=template))
# # if not done: print(g.to_dict())
# if done and g not in grammar_list: grammar_list.append(g)

# grammar_to_jsonl(grammar=grammar_list,path=gr_path)
# grammar_to_txt(grammar=grammar_list,path='/media/selina/SHARE/MyProjects/ChD/grammar/grammar.txt',template=template)

# test="◼ jabjbdj \n◼ jkankjsnan"
# print(re.sub(r'[◼]','●',test))
# test="□ jabjbdj \n○ jkankjsnan"
# print(re.sub(r'[■|□|●|○]','◼',test))
# print(test)
# ■ □ ● ○

# print(os.path.dirname(os.path.abspath(__file__)))
# print(os.path.join('/home/','selina','test/'))
# print(Path('/home/')/'test/'/'best')
# from kivy.utils import hex_colormap
# print([palette.capitalize() for palette in hex_colormap.keys()])

test="Repetition of Past Action with 又"