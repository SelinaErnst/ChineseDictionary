import re
from .character import Character
from .convert_pleco_txt import convert_to_pleco_syntax
from .unicode_characters import chinese_char, decode_pinyin


class Sentence():
    def __init__(self,text:str='',pronunciation:str='',translation:str='',content:tuple=None):
        self.__text=text
        self.clean_text()
        self.__pronunciation=pronunciation
        self.translation=translation

        if content!=None: self.__text, self.__pronunciation, self.translation = content
        self.marked_text=self.text

    @property
    def pronunciation(self):
        return decode_pinyin(self.__pronunciation)
    
    @property
    def text(self):
        self.clean_text()
        return self.__text

    def clean_text(self):
        a=convert_to_pleco_syntax('link')[0]
        b=convert_to_pleco_syntax('link')[1]
        self.__text = self.__text.replace(a,'').replace(b,'')
        self.__text = self.__text.replace('.','。').replace(',','，').replace('!',"！").replace('?','？')
        self.__text = self.__text.replace(' ',"")
    
    def __repr__(self):
        return f'Sentence: {self.text}'

    def __str__(self):
        # result=[t for t in [self.marked_text,self.pronunciation,self.translation] if t!=""]
        result=[t for t in [self.text,self.pronunciation,self.translation] if t!=""]
        return f"\n".join(result)
    
    def to_txt(self):
        pronunciation=convert_to_pleco_syntax(command='color',text=self.pronunciation,color_name='grey')
        result=[t.strip(' ') for t in [self.marked_text,pronunciation,self.translation] if t!=""]
        return f"{convert_to_pleco_syntax('newline')}".join(result)
    
    def to_dict(self):
        return {'text':self.text,'pronunciation':self.pronunciation,'translation':self.translation}
    
    def mark_char(self,char:Character):
        finder=self.__find_ch_char(char,'simple')
        not_pattern='|'.join(finder)
        pattern=rf'(?:(?![{not_pattern}]).)*'.join(finder)
        found_patterns=[p for p in re.findall(pattern,self.text) if p!='']
        
        def is_inside_link(string):
            not_pattern=rf'(?:(?![{a}|{b}]).)*'
            # return re.findall(rf'[{a}|{b}].*?{string}.*?[{a}|{b}]',self.marked_text)!=[]
            # return re.findall(rf'{a}.*?{string}.*?{b}',self.marked_text)!=[]
            return re.findall(rf'{a}{not_pattern}{string}{not_pattern}{b}',self.marked_text)!=[]
        def replace_match(match):
            match = match.group()
            for f in set(finder):
                if not is_inside_link(f):
                    match=re.sub(f,convert_to_pleco_syntax('link',f),match)
                    # print(f,'IS NOT IN LINK',self.marked_text)
                # else:
                    # print(f,'is in link')
            return match
        def undo_replace(match):
            match = match.group()
            match = match[1:-1]
            return match
        
        if len(found_patterns)!=0:
            a=convert_to_pleco_syntax('link')[0]
            b=convert_to_pleco_syntax('link')[1]
            # a=convert_to_pleco_syntax('color',color_name='blue')[0]
            # a=convert_to_pleco_syntax('color',color_name='blue')[1]
            # in case of overlap 
            marked_found_patterns = re.findall(pattern,self.marked_text)
            if found_patterns != marked_found_patterns:
                for f in finder:
                    # ab -> ab or ab -> ab
                    new_pattern = rf'[{a}|{b}]*'.join(list(f))
                    new_finder = re.findall(new_pattern,self.marked_text)
                    # contains all found patterns with/without borders: bbaa, bbaa, bbaa, bbaa 
                    for f_with_border in set(new_finder):
                        borders = re.findall(rf'[{a}|{b}]',f_with_border)
                        # has overlap if border!=[]
                        if borders!=[]: 
                            if len(borders)==1 and borders[0]==a: f=f'{a}{f}'
                            elif len(borders)==1 and borders[0]==b: f=f'{f}{b}'
                            else: pass # bbaa -> bbaa
                            self.marked_text=re.sub(new_pattern,f,self.marked_text)
                        # else: 
                            # print(re.findall(rf'[{a}|{b}]',f_with_border))
                    
            # replace found patterns with linked version
            self.marked_text=re.sub(pattern,replace_match,self.marked_text)
            # in case of multiple links
            another_finder=[f'{a*2}{f}{b*2}' for f in finder]
            another_pattern='|'.join(another_finder)
            another_pattern=rf'({another_pattern})'
            self.marked_text=re.sub(another_pattern,undo_replace,self.marked_text)
            
    def mark_all_char(self,characters):
        from .dictionary import Dictionary
        self.marked_text=self.text
        for c in characters:
            self.mark_char(c)
        return self.marked_text
    
    def __find_ch_char(self,char,key):
        finder = re.findall(rf'(?:(?!…)[{chinese_char}|\w]+)',char[key])
        return finder