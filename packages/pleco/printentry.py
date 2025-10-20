from .convert_instructions import plecoformat
from .entry import entry

import re

PinyinToneMark = {
    0: "aoeiuv\u00fc", 
    1: "\u0101\u014d\u0113\u012b\u016b\u01d6\u01d6", # āōēīūǖǖ
    2: "\u00e1\u00f3\u00e9\u00ed\u00fa\u01d8\u01d8", # áóéíúǘǘ
    3: "\u01ce\u01d2\u011b\u01d0\u01d4\u01da\u01da", # ǎǒěǐǔǚǚ
    4: "\u00e0\u00f2\u00e8\u00ec\u00f9\u01dc\u01dc", # àòèìùǜǜ
}

def decode_pinyin(s):
    if s!=None:
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
                r += t
                t = ""
        r += t
        return r


def encode_pinyin(pinyin: str) -> str:
    if pinyin!=None:
        tone_map = {
            'ā': ('a', '1'), 'á': ('a', '2'), 'ǎ': ('a', '3'), 'à': ('a', '4'),
            'ē': ('e', '1'), 'é': ('e', '2'), 'ě': ('e', '3'), 'è': ('e', '4'),
            'ī': ('i', '1'), 'í': ('i', '2'), 'ǐ': ('i', '3'), 'ì': ('i', '4'),
            'ō': ('o', '1'), 'ó': ('o', '2'), 'ǒ': ('o', '3'), 'ò': ('o', '4'),
            'ū': ('u', '1'), 'ú': ('u', '2'), 'ǔ': ('u', '3'), 'ù': ('u', '4'),
            'ǖ': ('v', '1'), 'ǘ': ('v', '2'), 'ǚ': ('v', '3'), 'ǜ': ('v', '4'),
            'ü': ('v', '0'),  # plain ü → v0
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

def list_definitions(definitions,bullet='dot',newline=False):
    if type(definitions)==list:
        if definitions==['']: linestart=''
        else: linestart=plecoformat(bullet)
        if newline:
            liststring=f'{plecoformat("newline")}{plecoformat(bullet)} '.join(definitions)
        else:
            liststring=f' {plecoformat(bullet)} '.join(definitions)
        if bullet=='point':
            content=f'{linestart} '+liststring
        else:
            content=liststring
    elif definitions==None:
        content=''
    else:
        content=definitions
    return content

def definition(aspect: str, color: str, boldness: str, bullet='dot', elements=None, newline=False) -> str:
    
    if elements!=None and not newline:
        result=plecoformat(color,plecoformat(f'{boldness}',f'{aspect} '))+list_definitions(definitions=elements, bullet=bullet)+plecoformat('newline')
    elif elements!=None and newline:
        result=plecoformat(color,plecoformat(f'{boldness}',f'{aspect} '))+plecoformat('newline')+list_definitions(definitions=elements, bullet=bullet)+plecoformat('newline')
    else: result=''
    return result

def link_to_string(match):
    naked_string = match.group().lstrip('[').rstrip(']')
    # naked_string=decode_pinyin(naked_string)
    linked_string = plecoformat('link',naked_string)
    return f'[{linked_string}]'

def link_pronunciations(plecostring):
    return re.sub(r'\[(?:(?![\u4e00-\u9fff])[\S]+)\]',link_to_string,plecostring)

class plecoprinter():
    def __init__(self,entry=None):
        if entry==None:
            # creates entry witch no information at all
            self.__entry=entry()
        else:
            # attributes of entry depend on how dictionary defines characters
            self.__entry=entry

    def translation(self):
        categories=['english','german','measure_word','radical','opposite']
        n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
        if n_categories < 1: return ''
        return plecoformat(
            'left',
            definition('ENG','blue','narrowbold','point',self.__entry.english)+
            definition('GER','blue','narrowbold','point',self.__entry.german)+
            definition('MW ','teal','narrowbold','point',self.__entry.measure_word)+
            definition('RAD','teal','narrowbold','point',self.__entry.radical)+
            definition('OPP','green','narrowbold','point',self.__entry.opposite)
            )
    def information(self):
        categories=['strokes','classifier','variants','relatives','words','others','dict_entries']
        n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
        if n_categories < 1: return ''
        
        if self.__entry.dict_entries!=None: 
            dict_entries=[plecoformat('link',de) for de in self.__entry.dict_entries]
        else:
            dict_entries=None
        return plecoformat('grey',plecoformat('bold','INFORMATION'))+plecoformat(
            'indent',
            # definition('STROKES:','grey','bold','dot',f'({self.__entry.strokecount}) {self.__entry.strokeorder}')+
            definition('STROKES:','grey','bold','dot',self.__entry.strokes)+
            definition('CLASSIFIER:','grey','bold','dot',self.__entry.classifier)+
            definition('VARIANTS:','grey','bold','dot',self.__entry.variants)+
            definition('RELATIVES:','grey','bold','dot',self.__entry.relatives)+
            definition('WORDS:','grey','bold','dot',self.__entry.words)+
            definition('DISTINGUISH:','grey','bold','dot',self.__entry.others)+
            definition('DICTIONARY ENTRIES:','grey','bold','dot',dict_entries,newline=True)
        )
    def meaning(self):
        categories=['components','mnemonics','usage','origin']
        n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
        if n_categories < 1: return ''
        
        if self.__entry.components!=None:
            components=[c for c in self.__entry.components if len(c) <=5]
            components_explained=[c for c in self.__entry.components if len(c) >5]
            if len(components_explained)>0: comp=list_definitions(components_explained,bullet='point',newline=True)+plecoformat('newline')
            else: comp=''
        else:
            comp=''
            components=self.__entry.components
        return plecoformat('grey',plecoformat('bold','CHARACTER MEANING'))+plecoformat(
            'indent',
            definition('COMPONENTS:','grey','bold','dot',components)+comp+
            definition('MNEOMICS:','grey','bold','point',self.__entry.mnemonics)+
            definition('COMPONENT USAGE:','grey','bold','point',self.__entry.usage)+
            definition('ORIGINS:','grey','bold','point',self.__entry.origin)
        ) 

    def ancient_form(self):
        categories=['ancient']
        n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
        if n_categories < 1: return ''
        
        ancientform = ''.join(self.__entry.ancient) if isinstance(self.__entry.ancient,list) else self.__entry.ancient
        ancientform = ancientform if ancientform != None else ""
        return plecoformat('grey',plecoformat('bold','ANCIENT FORM:'))+plecoformat('textbig',f'{ancientform}')

    def links(self):
        categories=['link']
        n_categories = len([cat for cat in categories if cat in self.__entry.categories and self.__entry.__dict__[cat]!=None])
        if n_categories < 1: return ''
        
        links= self.__entry.link if self.__entry.link != None else []
        if len(links) > 0:
            zitoolslinks=[plecoformat('link',link) +plecoformat('newline') for link in links]
            return plecoformat('right',plecoformat('textsmall',''.join(zitoolslinks)))
        else:
            return ""