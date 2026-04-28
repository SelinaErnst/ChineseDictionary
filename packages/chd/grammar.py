from .dictionary import Dictionary
from .character import Character
from .convert_pleco_txt import Writer, convert_to_pleco_syntax
import re
from .unicode_characters import chinese_char

class Sentence():
    def __init__(self,text:str='',pronunciation:str='',translation:str='',content:tuple=None):
        self.text=text
        self.pronunciation=pronunciation
        self.translation=translation

        if content!=None: self.text, self.pronunciation, self.translation = content
        self.marked_text=self.text

    def __repr__(self):
        return f'Sentence:{self.text}'

    def __str__(self):
        result=[t for t in [self.marked_text,self.pronunciation,self.translation] if t!=""]
        return f"{convert_to_pleco_syntax('newline')}".join(result)
    
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
            
    def mark_all_char(self,characters:Dictionary):
        self.marked_text=self.text
        for c in characters:
            self.mark_char(c)
        return self.marked_text
    
    def __find_ch_char(self,char,key):
        finder = re.findall(rf'(?:(?!…)[{chinese_char}|\w]+)',char[key])
        return finder
            
class Grammar():
    def __init__(self,
                 level:str=None,title:str='',subtitle:str='',
                 structures:list=[],opposite_structures:list=[],
                 explanation:str='',sentences:list=[]):
        self.level = level
        self.title = title
        self.subtitle = subtitle
        
        self.explanation = explanation
        self.sentences,self.structures,self.opposite_structures=[],[],[]
        self.add_sentence(sentences)
        self.add_opp_structure(opposite_structures)
        self.add_structure(structures)
        
        self.characters = Dictionary(name='grammar_characters',sorting_key='simple')
        self.opposite_characters = Dictionary(name='grammar_opp_characters',sorting_key='simple')
        
        categories={
            'level':str,
            'title':str,
            'subtitle':str,
            'structures':list,
            'opposite_structures':list,
            'explanation':str,
            'sentences':list,
            'all_other_char':list}
        
        self.__character = Character(needed_categories=categories)
    
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return f'Level {self.level}: {self.title}'
    
    def __getitem__(self, key):
        if key == 'level': return self.level
        elif key == 'all_other_characters': return self.all_other_characters
        elif key not in ['simple','traditional','pronunciation']:
            return self.__dict__[key]
        else:
            return [c[key] for c in self.characters if isinstance(c,Character)]
    
    def get_all_other_characters(self,char):
        chars = self.characters.characters + self.opposite_characters.characters
        chars =[c['simple'].replace('…','＿') for c in chars if c!=char]
        return chars
        
    @property
    def level(self):
        return self.__level
    
    @level.setter
    def level(self,level):
        if level in ['A','A1','A2','A1','B','B1','B2','C','C1','C2']:
            self.__level = level
        else:
            if level==None: self.__level=''
            else: print(f"WARNING: grammar level '{level}' is not accepted")
    
    def __updater(self,char=None):
        all_characters = self.characters+self.opposite_characters
        # [s.mark_all_char(all_characters) for s in self.sentences]
        for s in self.sentences:
            s.mark_all_char(all_characters)
            # print(s)
        # print(self.sentences)
        kwargs={
            'level':self.level,
            'title':self.title,
            'subtitle':self.subtitle,
            'structures':self.structures.copy(),
            'opposite_structures':self.opposite_structures.copy(),
            'explanation':self.explanation,
            'sentences':[str(s)+convert_to_pleco_syntax('newline') for s in self.sentences],
            'all_other_char': self.get_all_other_characters(char=char)
        }
        return kwargs
                    
    def update(self,**kwargs):
        if 'level' in kwargs: self.level=kwargs.pop('level')
        if 'structures' in kwargs: self.add_structure(kwargs.pop('structures'))
        if 'opposite_structures' in kwargs: self.add_opp_structure(kwargs.pop('opposite_structures'))
        if 'sentences' in kwargs: self.add_sentence(kwargs.pop('sentences'))
        for k,v in kwargs.items():
            if k in self.__dict__: self.__dict__[k]=v
        
    def add_character(self,char):
        uniq_list=[]
        if isinstance(char,Character): uniq_list=[char.uniq]
        elif isinstance(char,tuple): uniq_list=[char]
        elif isinstance(char,list) or isinstance(char,Dictionary): 
            if not isinstance(char[0],Character): uniq_list=[char]
            else: uniq_list=[c.uniq for c in char]
        for uniq in uniq_list:
            new_char = self.__character.copy().update(simple=uniq[0],traditional=uniq[1],pronunciation=uniq[2])
            self.characters+=new_char
    
    def add_opp_character(self,char):
        uniq_list=[]
        if isinstance(char,Character): uniq_list=[char.uniq]
        elif isinstance(char,tuple): uniq_list=[char]
        elif isinstance(char,list) or isinstance(char,Dictionary): 
            if not isinstance(char[0],Character): uniq_list=[char]
            else: uniq_list=[c.uniq for c in char]
        for uniq in uniq_list:
            new_char = self.__character.copy().update(simple=uniq[0],traditional=uniq[1],pronunciation=uniq[2])
            self.opposite_characters+=new_char
    
    def opp(self):
        opp_grammar = Grammar(level=self.level,title=self.title,subtitle=self.subtitle,
                              structures=self.opposite_structures,opposite_structures=self.structures,
                              explanation=self.explanation,sentences=self.sentences)
        opp_grammar.add_character(self.opposite_characters)
        opp_grammar.add_opp_character(self.characters)
        return opp_grammar
            
    def add_structure(self,element):
        if not isinstance(element,list): element=[element]
        for e in element: self.structures.append(e)
            
    def add_opp_structure(self,element):
        if not isinstance(element,list): element=[element]
        for e in element: self.opposite_structures.append(e)
        
    def add_sentence(self,element=None,**kwargs):
        if not isinstance(element,list): 
            element=[element]
        for e in element: 
            if not isinstance(e,Sentence): 
                try:
                    if e==None: e=Sentence(**kwargs)
                    else: e=Sentence(content=e)
                except:
                    print(f"WARNING: '{e}' not accepted as sentence")
                    return
            self.sentences.append(e)
            
        
    def remove_sentence(self,element:Sentence):
        if isinstance(element,list): element=[element]
        for e in element:
            if e in self.sentences:
                self.sentences.remove(e)
                
    def remove_structure(self,element):
        if isinstance(element,list): element=[element]
        for e in element:
            if e in self.structures:
                self.structures.remove(e)
            elif e in self.opposite_structures:
                self.opposite_structures.remove(e)
        
    def to_text(self,template):
        complete_text=[]
        if len(self.characters)==0: print('WARNING: No characters listed, cannot write grammar to txt')
        for c in self.characters:
            if isinstance(c,Character):
                char=c.copy().update(self.__updater(c))
                w=Writer(template=template,character=char)
                w.add_uniq()
                w.link_pronunciations()
                # print(char.info(),w.text)
                complete_text.append(w.text)
        return f'\n'.join(complete_text)