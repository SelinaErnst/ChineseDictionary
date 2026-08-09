import json
import re
from .sentence import Sentence
from .character import Character
from .convert_pleco_txt import Writer, convert_to_pleco_syntax
from .unicode_characters import chinese_char, decode_pinyin

def sort_f(x,item_list):
    if hasattr(x,'uniq') and x.uniq in item_list: return item_list.index(x.uniq)
    else: return 0
    
def grammar_to_jsonl(grammar:list,path):
    with open(path,'w') as outfile:
        for g in grammar:
            if not g.is_empty():
                json.dump(g.to_dict(), outfile, indent=None, ensure_ascii=False)
                outfile.write('\n')
            
def grammar_to_txt(grammar,path,template):
    with open(path,'w') as file:
        text=[]
        for g in grammar:
            if not g.is_empty():
                text.append(g.to_text(template=template))
        file.write('\n'.join(text))
                
class Grammar():
    def __init__(self,
                 level:str=None,title:str='',subtitle:str='',tags:list=[],
                 structures:list=[],opposite_structures:list=[],
                 explanation:str='',sentences:list=[],
                 characters:list=[],opposite_characters:list=[]):

        if  level == "": self.__level = ""
        else: self.level = level
        self.title = title
        self.subtitle = subtitle
        self.tags = tags
        
        self.explanation = explanation
        self.sentences,self.structures,self.opposite_structures=[],[],[]
        self.characters,self.opposite_characters=[],[]
        
        categories={
            'level':str,
            'title':str,
            'subtitle':str,
            'structures':list,
            'opposite_structures':list,
            'explanation':str,
            'sentences':list,
            'all_other_char':list}
        
        self.__character = Character(needed_categories=categories).copy()
        
        self.add_sentence(sentences)
        self.add_opp_structure(opposite_structures)
        self.add_structure(structures)

        from .dictionary import Dictionary
        self.characters = Dictionary(name='grammar_characters',sorting_key='simple')
        self.opposite_characters = Dictionary(name='grammar_opp_characters',sorting_key='')
        self.add_character(characters)
        self.add_opp_character(opposite_characters)
        
    def clear(self):
        self.level = ""
        self.title = ""
        self.subtitle = ""
        self.explanation = ""
        self.__tags = []
        self.sentences = []
        self.structures = []
        self.opposite_structures = []
        self.characters = []
        self.opposite_characters = []
        
    def is_empty(self):
        return all([v in [[],"",None] for v in self.to_dict().values()])
        
    def opp(self,level="",title="",subtitle="",explanation=""):
        opp_grammar = Grammar(level=level,title=title,subtitle=subtitle,
                              structures=self.opposite_structures,opposite_structures=self.structures,
                              explanation=explanation,sentences=self.sentences)
        opp_grammar.add_character(self.opposite_characters)
        opp_grammar.add_opp_character(self.characters)
        return opp_grammar
    # = ============================================================== = #
    # =                          MAGIC METHODS                         = #
    # = ============================================================== = #
             
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        characters = ''.join([str(c) for c in self.characters.characters])
        return f'\nLevel {self.level}: {self.title} \t{characters}'
    
    def __hash__(self):
        return hash((self.level,self.title,self.subtitle))
    
    def __eq__(self,other):
        if isinstance(other,Grammar):
            this = (self.level,self.title,self.subtitle)
            that = (other.level,other.title,other.subtitle)
            this = [text.lower().strip(' ') for text in this]
            that = [text.lower().strip(' ') for text in that]
            return this == that
        else: return False 
        
    def __getitem__(self, key):
        if key == 'level': return self.level
        if key == 'tags': return self.tags
        elif key == 'all_other_characters': return self.all_other_characters
        elif key not in ['simple','traditional','pronunciation']:
            return self.__dict__[key]
        elif key == 'all_characters': return self.__all_characters
    
    # = ============================================================== = #
    # =                           PROPERTIES                           = #
    # = ============================================================== = #
        
    @property
    def categories(self):
        return ['level','title','subtitle','tags',
                'structures','opposite_structures',
                'explanation',
                'sentences',
                'characters','opposite_characters']
        
    @property
    def references(self):
        return [c['simple'].replace('…','＿').replace('_','＿').replace(' ','') for c in self.characters.characters]
    
    @property
    def __all_characters(self):
        sorter = self.characters.character_index
        sorter += self.opposite_characters.character_index
        all_characters = self.characters+self.opposite_characters
        all_characters.characters.sort(key=lambda x: sort_f(x,sorter))
        return all_characters
    
    @property
    def level(self):
        return self.__level
            
    @property
    def tags(self):
        return self.__tags
    
    @property
    def valid_tags(self):
        valid_tags=[
            'common-mistake','word-order','s-v-o','question','measure-word',
            'Conjunctions','Numbers','Adverbs','Particles','Verbs','Auxiliary Verbs',
            'Verb Phrases','Questions','Adjectives','Nouns','Measure Words','Preposition',
            'Complements','Noun Phrases','Sentence Patterns','Grammatical Structures','Comparison','Time',
            'Past','Future','Present','Negative','Positive','Modal'
        ]
        return valid_tags

    @property
    def unique_string(self):
        title = ''.join([w[0] for w in self.title.split(' ') if w != ""])
        subtitle = ''.join([w[0] for w in self.subtitle.split(' ') if w != ""])
        return f'{self.level}_{title}_{subtitle}'
    
    # = ============================================================== = #
    # =                         SET AND UPDATE                         = #
    # = ============================================================== = #
        
    @level.setter
    def level(self,level:str):
        if level in ['A1','A2','A1','B1','B2','C1','C2']:
            self.__level = level
        else:
            if level in [None,""]: self.__level=''
            else: print(f"WARNING: grammar level '{level}' is not accepted")
    
    @tags.setter
    def tags(self,tags:list):
        # valid_tags = [tag.lower() for tag in self.valid_tags]
        # tags = [t.lower() for t in tags if t.lower() in valid_tags]
        self.__tags = [t.lower() for t in tags]
        
    def add_tag(self,tag):
        # valid_tags = [tag.lower() for tag in self.valid_tags]
        # if tag.lower() in valid_tags and tag not in self.__tags:
        tag = tag.lower()
        if tag not in self.__tags:
            self.__tags.append(tag)  
        # else:
            # print(f'[WARNING] tags have to be part of these options:\n{self.valid_tags}')       
    
    def __reference_other_characters(self,char):
        chars =[c['simple'].replace('…','＿') for c in self.__all_characters.characters if c!=char]
        return chars
    
    def update(self,**kwargs):
        if 'level' in kwargs: self.level=kwargs.pop('level')
        if 'structures' in kwargs: self.add_structure(kwargs.pop('structures'))
        if 'opposite_structures' in kwargs: self.add_opp_structure(kwargs.pop('opposite_structures'))
        if 'sentences' in kwargs: self.add_sentence(kwargs.pop('sentences'))
        for k,v in kwargs.items():
            if k in self.__dict__: self.__dict__[k]=v
            
    # = ––––––––––––––––––––––––– characters ––––––––––––––––––––––––– = #

    def add_character(self,char):
        from .dictionary import Dictionary
        
        old_uniq_list=[]
        new_uniq_list=[]
        if len(self.characters)!=0: old_uniq_list=self.characters.character_index
        if isinstance(char,Character): new_uniq_list=[char.uniq]
        elif isinstance(char,tuple): new_uniq_list=[char]
        elif isinstance(char,list) or isinstance(char,Dictionary):
            if len(char) == 0: new_uniq_list=[]
            elif isinstance(char[0],Character): new_uniq_list=[c.uniq for c in char]
            elif len(char[0])==3: new_uniq_list=char
        for uniq in new_uniq_list:
            uniq = [u if u!=None else "" for u in uniq]
            new_char = self.__character.copy().update(
                simple=re.sub(r'[_|＿]','…',uniq[0]),
                traditional=re.sub(r'[_|＿]','…',uniq[1]),
                pronunciation=uniq[2])
            self.characters+=new_char
        uniq_list = old_uniq_list+[tuple(e) for e in new_uniq_list]
        self.characters.characters.sort(key=lambda x: sort_f(x,uniq_list))
    
    def add_opp_character(self,char):
        from .dictionary import Dictionary
        
        old_uniq_list=[]
        new_uniq_list=[]
        if len(self.opposite_characters)!=0: old_uniq_list=self.opposite_characters.character_index
        
        if isinstance(char,Character): new_uniq_list=[char.uniq]
        elif isinstance(char,tuple): new_uniq_list=[char]
        elif isinstance(char,list) or isinstance(char,Dictionary): 
            if len(char) == 0: new_uniq_list=[]
            elif isinstance(char[0],Character): new_uniq_list=[c.uniq for c in char]
            elif len(char[0])==3: new_uniq_list=char
        for uniq in new_uniq_list:
            new_char = self.__character.copy().update(simple=uniq[0],traditional=uniq[1],pronunciation=uniq[2])
            self.opposite_characters+=new_char
        
        uniq_list = old_uniq_list+[tuple(e) for e in new_uniq_list]
        self.opposite_characters.characters.sort(key=lambda x: sort_f(x,uniq_list))
        
    # = ––––––––––––––––––––––––– structures ––––––––––––––––––––––––– = #
        
    def add_structure(self,element):
        if not isinstance(element,list): element=[element]
        for e in element: self.structures.append(e) # e is str
            
    def add_opp_structure(self,element):
        if not isinstance(element,list): element=[element]
        for e in element: self.opposite_structures.append(e) # e is str
        
    def remove_structure(self,element):
        if isinstance(element,list): element=[element]
        for e in element:
            if e in self.structures:
                self.structures.remove(e)
            elif e in self.opposite_structures:
                self.opposite_structures.remove(e)
                
    # = –––––––––––––––––––––––––– sentences ––––––––––––––––––––––––– = #
        
    def add_sentence(self,element=None,**kwargs):
        if element==None:
            sentence=Sentence(**kwargs)
            self.sentences.append(sentence)
        elif not isinstance(element,list): 
            element=[element]
            
        for ele in element: 
            if not isinstance(ele,Sentence):
                if type(ele) in [tuple,list] and len(ele)==3:
                    sentence=Sentence(content=ele)
                    self.sentences.append(sentence)
                elif isinstance(ele,dict):
                    sentence=Sentence(**ele)
                    self.sentences.append(sentence)
            else:
                self.sentences.append(ele)
        
    def remove_sentence(self,element:Sentence|list):
        if isinstance(element,Sentence): element=[element]
        for e in element:
            if e in self.sentences:
                self.sentences.remove(e)
                
    # = ============================================================== = #
    # =                              WRITE                             = #
    # = ============================================================== = #
    
    def __txt_updater(self,char=None):
        from .convert_pleco_txt import link_pronunciations
        for s in self.sentences:
            s.mark_all_char(self.__all_characters)
        # print(self.__all_characters)
        kwargs={
            'level':self.level,
            'title':self.title,
            'subtitle':self.subtitle,
            'structures':self.structures.copy(),
            'opposite_structures':self.opposite_structures.copy(),
            'explanation':link_pronunciations(self.explanation),
            'sentences':[s.to_txt()+convert_to_pleco_syntax('newline') for s in self.sentences],
            'all_other_char': self.__reference_other_characters(char=char)
        }
        return kwargs
                    
    def to_text(self,template):
        complete_text=[]
        if len(self.characters)==0: print('WARNING: No characters listed, cannot write grammar to txt')
        for c in self.characters:
            if isinstance(c,Character):
                char=c.copy().update(self.__txt_updater(c))
                w=Writer(template=template,character=char)
                w.add_uniq()
                newline=convert_to_pleco_syntax('newline')
                text = w.text.replace('\n\n',f'{newline} {newline}')
                text = text.replace('\n',newline)
                text = re.sub(r'[■|□|●|○]','◼',text)
                complete_text.append(text)
        return f'\n'.join(complete_text)

    def to_dict(self):
        
        grammar_dict={
            'level':self.level,
            'title':self.title,
            'subtitle':self.subtitle,
            'tags':self.tags.copy(),
            'structures':self.structures.copy(),
            'opposite_structures':self.opposite_structures.copy(),
            'explanation':self.explanation,
            'sentences':[sentence.to_dict() for sentence in self.sentences],
            'characters': [character.uniq for character in self.characters],
            'opposite_characters': [character.uniq for character in self.opposite_characters],
        }
        return grammar_dict