# CJK Radicals Supplement
cjk_rad_supl = "\u2E80-\u2EFF"
# KangXi Radicals
kangxi_rad = "\u2F00-\u2FDF" 
# CJK Strokes
cjk_strokes = "\u31C0-\u31EF"
# CJK Unified Ideographs Extension A
cjk_ext_a = "\u3400-\u4DBF"
# CJK Unified Ideographs
cjk_uni_ideogr = "\u4E00-\u9FFF"


# Extensions B-F
# ext_b_f = "\U00020000-\U0002EBEF"
ext_b_f = "\U00020000-\U0002EBEF"
# Extensions G-J
ext_g_h = "\U00030000-\U0003347F"
ext_i = "\U0002EBF0-\U0002EE5F"

all_ext = f"{ext_b_f}|{ext_g_h}|{ext_i}"

pleco_char = "\ueaaa-\uefff"

chinese_char = f'{cjk_rad_supl}|{kangxi_rad}|{cjk_strokes}|{cjk_ext_a}|{cjk_uni_ideogr}|{all_ext}'
not_chinese_char = f'^{cjk_rad_supl}{kangxi_rad}{cjk_strokes}{cjk_ext_a}{cjk_uni_ideogr}{all_ext}'

PinyinToneMark = {
    0: "aoeiuv\u00fc", 
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6", # āōēīūǖǖ
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8", # áóéíúǘǘ
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da", # ǎǒěǐǔǚǚ
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc", # àòèìùǜǜ
}

import re

def decode_pinyin(s):
    # ba1 -> bā, nv3 -> nǚ
    s = "" if s==None else s
    s = s.replace('ü','v')
    words = str(s).split(' ')
    result = []
    for s  in words:
        if s!=None and re.search(r'\d', s):
            s = s.lower()
            r = ""
            t = ""
            for c in s:
                if c >= 'a' and c <= 'z':
                    t += c
                elif c == ':':
                    assert t[-1] == 'u'
                    t = t[:-1] + "\u00fc"
                else:
                    if c >= '0' and c <= '5':
                        tone = int(c) % 5 # tone 5 -> 0
                        if tone != 0:
                            m = re.search("[aoeiuv\u00fc]+", t)
                            if m is None:
                                t += c
                            elif len(m.group(0)) == 1:
                                t = t[:m.start(0)] + PinyinToneMark[tone][PinyinToneMark[0].index(m.group(0))] + t[m.end(0):]
                            else:
                                if 'a' in t:
                                    t = t.replace("a", PinyinToneMark[tone][0])
                                elif 'o' in t:
                                    t = t.replace("o", PinyinToneMark[tone][1])
                                elif 'e' in t:
                                    t = t.replace("e", PinyinToneMark[tone][2])
                                elif t.endswith("ui"):
                                    t = t.replace("i", PinyinToneMark[tone][3])
                                elif t.endswith("iu"):
                                    t = t.replace("u", PinyinToneMark[tone][4])
                                else:
                                    t += "!"
                        else:
                            t = t.replace('v','ü')
                    r += t
                    t = ""
            r += t
            result+=[r]
        else:
            s=s.replace('v','ü')
            result+=[s]
    return ' '.join(result)

# def encode_pinyin(pinyin: str) -> str:

#     if not pinyin:
#         return ""

#     tone_map = {
#         'ā': ('a', '1'), 'á': ('a', '2'), 'ǎ': ('a', '3'), 'à': ('a', '4'),
#         'ē': ('e', '1'), 'é': ('e', '2'), 'ě': ('e', '3'), 'è': ('e', '4'),
#         'ī': ('i', '1'), 'í': ('i', '2'), 'ǐ': ('i', '3'), 'ì': ('i', '4'),
#         'ō': ('o', '1'), 'ó': ('o', '2'), 'ǒ': ('o', '3'), 'ò': ('o', '4'),
#         'ū': ('u', '1'), 'ú': ('u', '2'), 'ǔ': ('u', '3'), 'ù': ('u', '4'),
#         'ǖ': ('v', '1'), 'ǘ': ('v', '2'), 'ǚ': ('v', '3'), 'ǜ': ('v', '4'),
#         'ü': ('v', '0'),
#     }

#     result = ""
#     current_tone = ""

#     for char in pinyin:
#         if char in tone_map:
#             # If we already have a tone stored from a previous syllable,
#             # append it before starting the next one.
#             if current_tone:
#                 result += current_tone
            
#             base, tone = tone_map[char]
#             result += base
#             current_tone = tone
#         else:
#             result += char
#             # If we hit a space, append the tone to the word that just ended
#             if char == ' ' and current_tone:
#                 result = result[:-1] + current_tone + ' '
#                 current_tone = ""

#     # Append the final tone digit
#     if current_tone:
#         result += current_tone

#     return result

def encode_pinyin(pinyin: str) -> str:
    # bā -> ba1
    if pinyin!=None:
        tone_map = {
            'ā': ('a', '1'), 'á': ('a', '2'), 'ǎ': ('a', '3'), 'à': ('a', '4'),
            'ē': ('e', '1'), 'é': ('e', '2'), 'ě': ('e', '3'), 'è': ('e', '4'),
            'ī': ('i', '1'), 'í': ('i', '2'), 'ǐ': ('i', '3'), 'ì': ('i', '4'),
            'ō': ('o', '1'), 'ó': ('o', '2'), 'ǒ': ('o', '3'), 'ò': ('o', '4'),
            'ū': ('u', '1'), 'ú': ('u', '2'), 'ǔ': ('u', '3'), 'ù': ('u', '4'),
            'ǖ': ('v', '1'), 'ǘ': ('v', '2'), 'ǚ': ('v', '3'), 'ǜ': ('v', '4'),
            'ü': ('v', ''),  # plain ü → v0
        }
        result = ""
        tone_digit = ""
        for c in pinyin:
            if c in tone_map:
                base, tone = tone_map[c]
                result += base
                tone_digit = tone
            else:
                # words can be seperated by space
                if (c == ' ') and tone_digit:
                    result += tone_digit
                    tone_digit = ""
                result += c
        if tone_digit:
            result += tone_digit
        return result
