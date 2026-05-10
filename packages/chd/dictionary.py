import json
import os
import sqlite3
from .character import Character
import re
from .convert_pleco_txt import encode_pinyin, decode_pinyin
from .convert_pleco_txt import Loader
from typing import Literal, TypeAlias
# from typeguard import typechecked

_EXPORT_CHOICES: TypeAlias = Literal['pleco', 'txt', 'chd', '.txt', 'jsonl', '.jsonl','db','.db']
_VALID_EXT={
    '.txt':['pleco','txt','.txt','all'],
    '.jsonl':['chd','jsonl','.jsonl','all'],
    '.db':['db','sql','base','all'],
}
_SORT_OPT: TypeAlias = Literal['simple','traditional','pronunciation']

def choose_file_ext(choice:_EXPORT_CHOICES|None,ext_map:dict=_VALID_EXT):
    file_format=[f for f,f_options in ext_map.items() if choice in f_options]
    if file_format!=[]: return file_format[0]
    else: return None


def make_subset(matching_characters, dictionary_name:str, force_dictionary:bool=False,**kwargs):
    if len(matching_characters) == 0:
        return None
    elif len(matching_characters) == 1 and not force_dictionary:
        return matching_characters[0] 
    elif len(matching_characters) > 1 or force_dictionary:
        return Dictionary(name=dictionary_name,characters=matching_characters,**kwargs)
    else:
        return None

class Dictionary():
    
    def __init__(self,
                 name:str|None=None,
                 characters:list|Character|None=None,
                 grammar:list|None=None,
                 sorting_key:_SORT_OPT='pronunciation'):
        self.name = name if isinstance(name,str) else ""
        self.__init_characters(characters=characters)
        self.__init_grammar(grammar=grammar)
        self._sorting_key=sorting_key
        self.sort()
        

                
    def copy(self):
        characters = [c.copy() for c in self.characters]
        return Dictionary(name=self.name,characters=characters,sorting_key=self.sorting_key,grammar=self.grammar)
    
    def empty(self):
        self.characters=[]
    
    # = ============================================================== = #
    # =                         GET PROPERTIES                         = #
    # = ============================================================== = #
    
    @property
    def character_index(self):
        return [c.uniq for c in self.characters]
    
    def index(self,c):
        if isinstance(c,Character) and c in self.characters:
            return self.characters.index(c)
        elif isinstance(c,tuple) and c in self.character_index:
            return self.character_index.index(c)

    @property
    def sorting_key(self):
        return self._sorting_key
    
    # = ============================================================== = #
    # =                         SET PROPERTIES                         = #
    # = ============================================================== = #

    def __init_characters(self,characters):
        if isinstance(characters,list): 
            self.characters=[c for c in set(characters) if isinstance(c,Character) and not c.is_empty()]
        elif isinstance(characters,Dictionary):
            self.characters=characters.characters.copy()
        elif isinstance(characters,Character) and not characters.is_empty():  
            self.characters=[characters]
        else:
            self.characters=[]
            
    def __init_grammar(self,grammar):
        from .grammar import Grammar
        if isinstance(grammar,list):
            self.grammar = [g for g in set(grammar)]
        elif isinstance(grammar,Grammar):
            self.grammar = [grammar]
        else:
            self.grammar = []
            
    def set_categories(self,categories):
        # defines default categories and dtypes for characters
        self.__category_dictionary=categories 
        
    def set_grammar(self,grammar):
        self.__init_grammar(grammar=grammar)

    def rename(self,name):
        self.name = name
        
    @sorting_key.setter
    def sorting_key(self, key):
        acceptable = ['simple','traditional','pronunciation']
        if key.lower() in ['simple','traditional','pronunciation']:
            self._sorting_key = key.lower()
            self.sort()
        else:
            print(f'\nWARNING: Sorting key is not valid. Choose from: {acceptable}')

    # = ============================================================== = #
    # =                          MAGIC METHODS                         = #
    # = ============================================================== = #
    
    def __repr__(self):
        header = f'<{self.name}> dictionary: {len(self.characters)} character entries'
        lines=[]
        for i,c in enumerate(self.characters):
            i='{:4}'.format(i)
            lines+=[f'{i}: {str(c)}\n']
        if len(lines) > 0:
            return header + '\n' + ''.join(lines)
        else:
            return header
    def __str__(self):
        return self.__repr__()
    
    def __len__(self):
        return len(self.characters)
    def __eq__(self,other):
        if type(self) == type(other):
            sorting_key = 'pronunciation'
            test = sorted(self.characters,key=lambda x: encode_pinyin(x[sorting_key]) if x[sorting_key]!=None else "")
            comp = sorted(other.characters,key=lambda x: encode_pinyin(x[sorting_key]) if x[sorting_key]!=None else "")
            return test == comp
        else: return False
        
    def __iter__(self):
        return iter(self.characters)
    def __add__(self,other):
        characters = self.characters.copy()
        do_warning = False
        if isinstance(other,Character):
            name = self.name
            if other.uniq not in self.character_index:
                characters.append(other)
            elif do_warning:
                print(f'character {(other)} was not added to dictionary, it already exists')
        if isinstance(other,Dictionary):
            name = self.name if self.name != "" else other.name
            for c in other:
                if c not in characters:
                    characters.append(c)
                elif do_warning:
                    print(f'character {c} was not added to dictionary, it already exists')

        return Dictionary(name=name, characters=characters, sorting_key=self.sorting_key,grammar=self.grammar)
    
    def __sub__(self,c:Character):
        if c.uniq in self.character_index:
            self.characters.remove(c)
        else:
            print('character is not in dictionary')
        self.sort()
        return self
    
    def __getitem__(self,index):
        kwargs={
            'sorting_key':self.sorting_key,
            'grammar':self.grammar
        }
        if isinstance(index,int):
            if index < len(self.characters): return self.characters[index]
        elif isinstance(index,tuple) and index in self.character_index:
            matching_c = [c for c in self.characters if c.uniq == index]
            return make_subset(matching_characters=matching_c,dictionary_name=self.name,force_dictionary=False,**kwargs)
        elif isinstance(index,str):
            matching_c = [c for c in self.characters if index in c.uniq]
            return make_subset(matching_characters=matching_c,dictionary_name=self.name,force_dictionary=False,**kwargs)
        elif isinstance(index,slice):
            matching_c = [c for c in self.characters[index.start:index.stop]]
            return make_subset(matching_characters=matching_c,dictionary_name=self.name,force_dictionary=True,**kwargs)
        elif isinstance(index,Character):
            index=index.uniq
            matching_c = [c for c in self.characters if c.uniq == index]
            return make_subset(matching_characters=matching_c,dictionary_name=self.name,force_dictionary=False,**kwargs)
        elif isinstance(index,list) and isinstance(index[0],tuple):
            overlap = set(index) & set(self.character_index)
            matching_c = [c for c in self.characters if c.uniq in overlap]
            return make_subset(matching_characters=matching_c,dictionary_name=self.name,force_dictionary=True,**kwargs)
        else:
            print(f'WARNING: dictionary cannot work with index {type(index)}',isinstance(index,Character))
        
    def __contains__(self, c):
        if c in self.characters or c in self.character_index:
            return True
        else:
            return False
    
    # = ============================================================== = #
    # =                          SORT & SEARCH                         = #
    # = ============================================================== = #
    
    # def _get_sorted_characters(self,sorting_key=None):
        # sorting_key = self.sorting_key if sorting_key == None else sorting_key
    
    def sort(self,sorting_key=None,sorting_function=None):
        sorting_key = self.sorting_key if sorting_key == None else sorting_key
        def get_next_key(char,sorting_key):
            # determine priorities (what happens when property is None/"")
            if sorting_key == "simple":
                other_keys = ['simple','traditional','pronunciation']
            elif sorting_key == "traditional":
                other_keys = ['traditional','pronunciation','simple']
                # other_keys = ['traditional','simple','pronunciation']
            elif sorting_key == "pronunciation":
                other_keys = ['pronunciation','simple','traditional']
            values = [char[key] for key in other_keys if char[key] not in [None,'']]
            value = values[0] if len(values)>=1 else ""
            return value
        if self.sorting_key in ['simple','traditional','pronunciation']:
            self.characters.sort(key=lambda x: encode_pinyin(get_next_key(char=x,sorting_key=sorting_key)))
        return self
    
    def search(self,text:str="",exact:bool=False,search_prompt:bool=False):
        exact=True
        
        def prepare_text(text:str):
            text = text.lower().replace(' ','')
            pinyin = decode_pinyin(text)
            pinyin_numeric = encode_pinyin(pinyin)
            pinyin_toneless = re.sub(r'\d+', '', pinyin_numeric)
            if not exact: return [pinyin_toneless]
            else: return [pinyin_numeric,pinyin]
        
        def compare(text:str|list,character:Character,use_variants:bool=True):
            if isinstance(text,str): text=[text]
            if not exact: search_for = list(character.uniq)[:2]+[character.pinyin_toneless]
            else: search_for = list(character.uniq)[:2]+[character.pinyin_numeric,character.pinyin]
            if use_variants: search_for += character.clean_variants
            search_for = [s.replace(' ','') for s in search_for]
            found=any([any([t in s for t in text]) for s in search_for])
            return found
        
        search_text = prepare_text(text)
        if search_prompt: print('Look for:',text,'or',search_text)
        fits = [char for char in self.characters if compare(text=search_text,character=char)]
        return Dictionary(name=self.name, characters=fits, sorting_key=self.sorting_key, grammar=self.grammar)
    
    # = –––––––––––––––––––––––––––– links ––––––––––––––––––––––––––– = #
        
    def get_linked_grammar(self,character,key='dict_entries'):
        # get grammar entries that correspond to dict_entries of character
        
        def match_gram_to_dict_entry(entry,grammar):
            if hasattr(grammar,'references'):
                references = [re.sub(r'[.|。|,|，|!|！|?|？]','',ref) for ref in grammar.references]
                references = [ref.strip('＿') for ref in references]
                entry = re.sub(r'[.|。|,|，|!|！|?|？]','',entry)
                entry = entry.strip('＿')
                return entry in references
            return False
        
        links={}
        if isinstance(character[key],list):
            for n,entry in enumerate(character[key]):
                match_gram = [g for g in self.grammar if match_gram_to_dict_entry(entry,g)]
                if match_gram != []: links[entry]=match_gram[0]
                else: links[entry]=None
        return links
    
    def get_linked_character(self,grammar_link,key='dict_entries'):
        # get characters that have grammar linked in dict_entries
        
        if isinstance(grammar_link,Character):
            grammar_link=grammar_link['simple'].replace('…','＿')
        elif isinstance(grammar_link,str):
            grammar_link=grammar_link.replace('…','＿')
        else:
            grammar_link=""
            
        def match_to_dict_entries(gram_char,character):
            if isinstance(character[key],list):
                entries=character[key]
                entries = [re.sub(r'[.|。|,|，|!|！|?|？]','',entry) for entry in entries]
                entries = [entry.strip('＿') for entry in entries]
                gram_char = re.sub(r'[.|。|,|，|!|！|?|？]','',gram_char)
                gram_char = gram_char.strip('＿')
                return gram_char in entries
            else:
                return False
        
        grammar_link.strip('＿')
        match_char = [char for char in self.characters if match_to_dict_entries(grammar_link,char)]
        return match_char
    
    # = ============================================================== = #
    # =                              READ                              = #
    # = ============================================================== = #
    
    def read(self,filename,file_format:_EXPORT_CHOICES|None=None,add=True,categories=None,template=None):
        filename,ext = os.path.splitext(filename)
        if ext!="": file_format=ext
        file_format=choose_file_ext(file_format)
        if file_format!=None:
            filename=filename+file_format
            if file_format == '.txt':
                return self.read_pleco(filename,template=template,add=add,categories=categories)
            elif file_format == '.jsonl':
                return self.read_jsonl(filename,add=add,categories=categories)
            else: return False
        else: return False
            
    def read_jsonl(self,filename,add=True,categories=None):
        try:
            with open(filename,'r') as file:
                json_list = list(file)
            if not add:
                self.characters=[]
            for json_str in json_list:
                entry=json.loads(json_str)
                c = Character(needed_categories=categories, **entry)
                if c.uniq not in self.character_index:
                    self.characters.append(c)
                elif c.uniq in self.character_index:
                    matching_c = [char for char in self.characters if char.uniq == c.uniq][0]
                    if c.default_dtypes != matching_c.default_dtypes:
                        self.characters.remove(matching_c)
                        self.characters.append(c)
                        
            self.sort()
            return True
        except:
            return False
        
    def read_pleco(self,filename,template,add=True,categories=None):
        if template!=None and os.path.isfile(template):
            l=Loader(template=template)
            with open(filename) as f:
                character_lines=f.readlines()
            if character_lines!=None:
                if not add: self.characters=[]  
                for char_line in character_lines:
                    char_content = l.character(content=char_line)
                    c=Character(needed_categories=categories,**char_content)
                    if c.uniq not in self.character_index:
                        self.characters.append(c)
                    elif c.uniq in self.character_index:
                        matching_c = [char for char in self.characters if char.uniq == c.uniq][0]
                        if c.default_dtypes != matching_c.default_dtypes:
                            self.characters.remove(matching_c)
                            self.characters.append(c)
                self.sort()
                return True
            else: return False
        else: return False
    
    # = ============================================================== = #
    # =                              WRITE                             = #
    # = ============================================================== = #
    
    def write(self,directory:str='./',filename:str|None=None,file_format:_EXPORT_CHOICES|None=None,**kwargs):
        filename = self.name if filename == None else filename
        file_format=choose_file_ext(file_format)
        if file_format!=None:
            filename = filename+file_format if filename == self.name else filename
            if file_format == '.txt':
                template = kwargs.pop('template')
                self.to_txt(directory=directory,filename=filename,template=template)
            elif file_format == '.jsonl':
                self.to_jsonl(directory=directory,filename=filename)
            elif file_format == '.db':
                self.to_db(directory=directory,filename=filename)
                

    def to_jsonl(self,directory:str,filename=None):
        filename = filename+'.jsonl' if filename == self.name else filename
        with open(directory+filename,'w') as outfile:
            for c in self.characters:
                json.dump(c.to_dict(), outfile, indent=None, ensure_ascii=False)
                outfile.write('\n')
    
    def to_txt(self,directory:str,template:str,filename=None):
        filename = filename+'.txt' if filename == self.name else filename
        with open(directory+filename,'w') as file:
            pleco_text=[
                c.to_pleco_entry(template=template)
                for c in self.characters]
            file.write('\n'.join(pleco_text))
        

    def to_db(self,directory:str,filename=None):
        filename = filename+'.db' if filename == self.name else filename
        db_file = os.path.join(directory,filename)

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        def get_col(dtype):
            dtype_map = {
                str:'TEXT',
                int:'INTEGER',
                float:'NUMERIC',
                list:'TEXT',
                dict:'TEXT',
            }
            if dtype not in dtype_map.keys(): return 'TEXT'
            else: return [t for d,t in dtype_map.items() if dtype==d][0]
        
        c_links = []
        for i,c in enumerate(self.characters):
            c_data = c.to_dict()
            
            for entry,result in self.get_linked_grammar(c).items():
                if result!=None:
                    c_links.append((c.unicode_unique_string,result.unique_string,entry))
                else:
                    c_links.append((c.unicode_unique_string,result,entry))
                        
            if i == 0:
                cols = [f'"{k}" {get_col(v)}' for k,v in c.default_dtypes.items()]
                cols = '"uniq" TEXT UNIQUE, '+", ".join(cols)
                cursor.execute(f"DROP TABLE IF EXISTS {self.name}")
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.name} ({cols})")
                placeholders = '?, '+", ".join(["?" for _ in c_data.keys()])
                insert_query = f"INSERT INTO {self.name} VALUES ({placeholders})"
            values = [c.unicode_unique_string]+[json.dumps(v) if isinstance(v, (list, dict)) else v for v in c_data.values()]
            cursor.execute(insert_query, values)
                        
        from packages.chd import Grammar
        for i,g in enumerate(self.grammar):
            if isinstance(g,Grammar) and not g.is_empty():
                g_data = g.to_dict()
                if  i == 0:
                    cols = [f'"{k}" TEXT' for k in g_data.keys()]
                    cols = '"index" TEXT UNIQUE, '+", ".join(cols)
                    cursor.execute(f"DROP TABLE IF EXISTS Grammar")
                    cursor.execute(f"CREATE TABLE IF NOT EXISTS Grammar ({cols})")
                    placeholders = '?, '+", ".join(["?" for _ in g_data.keys()])
                    insert_query = f"INSERT INTO Grammar VALUES ({placeholders})"
                values = [g.unique_string]+[json.dumps(v) if isinstance(v, (list, dict)) else v for v in g_data.values()]
                cursor.execute(insert_query, values)
                
        for i,links in enumerate(c_links):
            if  i == 0:
                cols = f'"character" TEXT, "grammar" TEXT, "entry" TEXT'
                cursor.execute(f"DROP TABLE IF EXISTS Links")
                cursor.execute(f"CREATE TABLE IF NOT EXISTS Links ({cols})")
                placeholders = '?, ?, ?'
                insert_query = f"INSERT INTO Links VALUES ({placeholders})"
            cursor.execute(insert_query, links)
            
        conn.commit()
        conn.close()
        
