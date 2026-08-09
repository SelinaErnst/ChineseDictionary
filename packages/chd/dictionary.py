import json
import os
import sqlite3
from .character import Character
from .grammar import Grammar
import re
from .convert_pleco_txt import encode_pinyin, decode_pinyin
from .convert_pleco_txt import Loader
from .sql_methods import (
    table_exists, 
    create_table, 
    remove_table,
    open_db, close_db, 
    get_table_columns,
    get_table_names,
    create_column_list,
    add_columns,
    get_unique_values,
    )
from typing import Literal, TypeAlias
from pathlib import Path
# from typeguard import typechecked

_EXPORT_CHOICES: TypeAlias = Literal['pleco', 'txt', 'chd', '.txt', 'jsonl', '.jsonl','db','.db']
_VALID_EXT={
    '.txt':['pleco','txt','.txt','all'],
    '.jsonl':['chd','jsonl','.jsonl','all'],
    '.db':['db','.db','sql','base','all'],
}
_SORT_KEY: TypeAlias = Literal['simple','traditional','pronunciation']
_SORT_ORD: TypeAlias = Literal['ascending','descending']

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
                 grammar:list|Grammar|None=None,
                 sorting_key:_SORT_KEY='pronunciation',
                 sorting_order:_SORT_ORD='ascending'):
        
        self.name = name if isinstance(name,str) else ""
        self.__init_characters(characters=characters)
        self.__init_grammar(grammar=grammar)
        self.__sorting_key=sorting_key
        self.__sorting_order=sorting_order
        
        
        self.sort()
        

                
    def copy(self):
        characters = [c.copy() for c in self.characters]
        return Dictionary(name=self.name,characters=characters,sorting_key=self.__sorting_key,grammar=self.grammar)
    
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
        return self.__sorting_key
    
    @property
    def sorting_order(self):
        return self.__sorting_order
    
    # = ============================================================== = #
    # =                         SET PROPERTIES                         = #
    # = ============================================================== = #

    @sorting_key.setter
    def sorting_key(self, key):
        acceptable = list(_SORT_KEY.__args__)
        if key.lower() in acceptable:
            self.__sorting_key = key.lower()
            self.sort()
    
    @sorting_order.setter
    def sorting_order(self, order):
        acceptable = list(_SORT_ORD.__args__)
        if order.lower() in acceptable:
            self.__sorting_order = order.lower()
            self.sort()
    
    def reorder(self,key,order):
        key,order = key.lower(),order.lower()
        acceptable = list(_SORT_KEY.__args__)
        if key not in acceptable:
            return None
        
        acceptable = list(_SORT_ORD.__args__)
        if order not in acceptable:
            return None
        
        if key != self.__sorting_key or order != self.__sorting_order:
            self.__sorting_key = key
            self.__sorting_order = order
            self.sort()
        
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
        self.__categories=categories 
        
    def set_grammar(self,grammar):
        self.__init_grammar(grammar=grammar)

    def rename(self,name):
        self.name = name

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

        return Dictionary(name=name, characters=characters, sorting_key=self.__sorting_key,grammar=self.grammar)
    
    def __sub__(self,c:Character):
        if c.uniq in self.character_index:
            self.characters.remove(c)
        else:
            print('character is not in dictionary')
        self.sort()
        return self
    
    def __getitem__(self,index):
        kwargs={
            'sorting_key':self.__sorting_key,
            'grammar':self.grammar
        }
        if isinstance(index,int):
            if index < len(self.characters): return self.characters[index]
        elif isinstance(index,tuple):
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
        if c in self.character_index:
            return True
        elif c in self.characters:
            return True
        else:
            return False
    
    # = ============================================================== = #
    # =                          SORT & SEARCH                         = #
    # = ============================================================== = #
    
    def sort(self,sorting_key=None,sorting_order=None,sorting_function=None):
        sorting_key = self.__sorting_key if sorting_key == None else sorting_key
        sorting_order = self.__sorting_order if sorting_order == None else sorting_key
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
            
        if sorting_key in list(_SORT_KEY.__args__):
            reverse = False if sorting_order=="ascending" else True
            self.characters.sort(key=lambda x: encode_pinyin(get_next_key(char=x,sorting_key=sorting_key)), reverse=reverse)
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
        return Dictionary(name=self.name, characters=fits, sorting_key=self.__sorting_key, grammar=self.grammar)
    
    def search_category(self,category:str,text:str="",exact:bool=False,search_prompt:bool=False):

        def look_for(text,string:str):
            if exact:
                for c in '().[]",:':
                    string = string.replace(c,"")
                string = string.split(' ')
                return text.lower() in [s.strip().lower() for s in string if s!=""]
            else:
                return text.lower() in string.lower()

        def compare(text:str,character:Character,category:str):
            if isinstance(category,list):
                return any([compare(text,character,cat) for cat in category])
            elif category in character:
                value = character[category]
                if isinstance(value,str):
                    return look_for(text,str(value))
                elif isinstance(value,list):
                    return any([look_for(text,str(v)) for v in value])
                elif isinstance(value,dict):
                    return any([look_for(text,str(v)) for v in value.values()])
            else:
                return False
            
        if search_prompt: print('Look for:',text)
        fits = [char for char in self.characters if compare(text=text,character=char,category=category)]
        return Dictionary(name=self.name, characters=fits, sorting_key=self.__sorting_key, grammar=self.grammar)
    
    # = –––––––––––––––––––––––––––– links ––––––––––––––––––––––––––– = #
        
    def __clean_link(self,text):
        text = re.sub(r'[.|。|,|，|!|！|?|？]','',text)
        text = text.replace('_','＿').replace('…','＿').replace(' ','')
        text = text.strip('＿')
        return text
    
    def get_linked_grammar(self,character,key='grammar') -> dict:
        # get grammar entries that are linked in character
        
        def match_gram_to_dict_entry(entry,grammar,msg=False) -> bool:
            if hasattr(grammar,'references'):
                references = [self.__clean_link(ref) for ref in grammar.references]
                entry = self.__clean_link(entry)
                if msg: print(entry,references)
                return entry in references
            return False
        
        links={}
        
        if isinstance(character[key],list):
            for n,entry in enumerate(character[key]):
                match_gram = [g for g in self.grammar if match_gram_to_dict_entry(entry,g,False)]
                links[entry]=match_gram
                
        return links
    
    def get_linked_character(self,character,key='grammar') -> list:
        
        # get characters that have grammar from given character linked
        if isinstance(character,Character):
            character=character['simple']
        elif isinstance(character,str):
            character=character
        else:
            character=""
            
        def match_to_entries(search_char,dict_char,msg=False) -> bool:
            entries=dict_char[key]
            if isinstance(entries,list):
                entries = [self.__clean_link(entry) for entry in entries]
                search_char = self.__clean_link(search_char)
                if msg: print(search_char,entries)
                return search_char in entries
            elif isinstance(entries,str):
                search_char = self.__clean_link(search_char)
                entries = self.__clean_link(entries)
                if msg: print(search_char,entries)
                return search_char == entries
            else:
                return False

        match_char = [char for char in self.characters if match_to_entries(character,char,False)]
        return match_char
    
    # = ============================================================== = #
    # =                              READ                              = #
    # = ============================================================== = #
    
    def read(self,filepath:str|Path,add:bool=True,categories=None,file_format:_EXPORT_CHOICES|None=None,**kwargs):
        if isinstance(filepath,str): filepath = Path(filepath)
        directory = filepath.parent
        filename = filepath.stem
        ext = filepath.suffix
        if ext!="": file_format=ext
        file_format=choose_file_ext(file_format)
        if file_format!=None:
            file=filename+file_format
            if file_format == '.txt':
                if 'template' in kwargs.keys(): template = kwargs.pop('template')
                else: print('WARNING: a template is required to read a pleco txt file.')
                return self.__read_pleco(directory/file,add=add,categories=categories,template=template)
            elif file_format == '.jsonl':
                return self.__read_jsonl(directory/file,add=add,categories=categories)
            elif file_format == '.db':
                if 'name' in kwargs.keys(): name = kwargs.pop('name')
                else: name = None
                return self.__read_db(directory/file,add=add,categories=categories,name=name)
            else: return False
        else: return False
            
    def __read_jsonl(self,filepath,add=True,categories=None):
        
        if not os.path.isfile(filepath): return False
        
        try:
            with open(filepath,'r') as file:
                json_list = list(file)
                
            if not add: self.characters=[]
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
            self.set_categories(categories=categories)
            return True
        except:
            return False
        
    def __read_pleco(self,filepath,template,add=True,categories=None):
        
        if not os.path.isfile(filepath): return False
        
        if template!=None:
            l=Loader(template=template)
            with open(filepath) as f:
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
                self.set_categories(categories=categories)
                return True
            else: return False
        else: return False
        
    def __read_db(self,filepath:str|Path,add=True,categories=None,name=None):
        import traceback
        if not os.path.isfile(filepath): return False
        elif isinstance(filepath,str): filepath = Path(filepath)
        conn,cursor = open_db(filepath)       
            
        self.grammar = []
        tables = get_table_names(cursor)
        
        if table_exists(cursor,'Grammar'):
            g_rows = cursor.execute("SELECT * FROM Grammar").fetchall()
            from packages.chd import Grammar
            for row in g_rows:
                data = dict(row)
                try: 
                    idx = data.pop('uniq')
                except: 
                    idx = data.pop('index')
                    
                clean_data = {k: (json.loads(v) if isinstance(v, str) and v.startswith(('[', '{')) else v) 
                                for k, v in data.items()}
                g_obj = Grammar(**clean_data) 
                self.grammar.append(g_obj)

        filename=filepath.stem
        if not table_exists(cursor,'Dictionary'):
            name = 'all'
            if name!=None and table_exists(cursor,name): table = name
            elif table_exists(cursor,self.name): table = self.name
            elif table_exists(cursor,filename): table = filename
            else: return False
        else:
            table = 'Dictionary'
            if name!=None and name not in get_unique_values(cursor,table,'dict_name'): name='all'
            elif name==None: name='all'
            
        if not add: self.characters=[]

        try:
            from packages.chd import Character
            if table=='Dictionary' and name!='all':
                query = f"SELECT * FROM {table} WHERE TRIM(dict_name, ' \n\r\t') = ?"
                c_rows = cursor.execute(query,[f'{name}']).fetchall()
            else:
                query = f"SELECT * FROM {table}"
                c_rows = cursor.execute(query).fetchall()
            for row in c_rows:
                data = dict(row)
                uniq = data.pop('uniq')
                clean_data = {k: (json.loads(v) if isinstance(v, str) and v.startswith(('[', '{')) else v) 
                            for k, v in data.items()}
                c_obj = Character(needed_categories=categories,**clean_data)
                if c_obj.uniq not in self.character_index:
                    self.characters.append(c_obj)
                elif c_obj.uniq in self.character_index:
                    matching_c = [char for char in self.characters if char.uniq == c_obj.uniq][0]
                    if c_obj.default_dtypes != matching_c.default_dtypes:
                        self.characters.remove(matching_c)
                        self.characters.append(c_obj)
                        
        except Exception as e:
            traceback.print_exc()
            return False

        close_db(conn)
        # if read: 
        self.set_categories(categories=categories)
        return True
    
    # = ============================================================== = #
    # =                              WRITE                             = #
    # = ============================================================== = #
    
    def write(self,directory:str|Path='',filename:str|Path|None=None,file_format:_EXPORT_CHOICES|None=None,**kwargs):
        
        if not os.path.isdir(directory): return None
        
        if isinstance(filename,str): filename,ext = os.path.splitext(filename)
        elif isinstance(filename,Path): filename,ext = filename.stem,filename.suffix
        elif filename == None: filename,ext = self.name,""
        else: return None
        
        if ext!="": file_format=ext
        
        file_format=choose_file_ext(file_format)
        
        if file_format!=None:
            file = filename+file_format
            if file_format == '.txt':
                template = kwargs.pop('template')
                categories = None if 'categories' not in kwargs else kwargs.pop('categories')
                self.__to_txt(directory=directory,filename=file,template=template,categories=categories)
            elif file_format == '.jsonl':
                self.__to_jsonl(directory=directory,filename=file)
            elif file_format == '.db':
                if 'clean' in kwargs: 
                    clean=kwargs.pop('clean')
                    self.__to_db(directory=directory,filename=file,clean=clean)
                else: self.__to_db(directory=directory,filename=file)

    def __to_jsonl(self,directory:Path,filename:str):
        if not isinstance(directory,Path): directory=Path(directory)
        if not filename.endswith('jsonl'): filename+='.jsonl'
        with open(directory/filename,'w') as outfile:
            for c in self.characters:
                json.dump(c.to_dict(), outfile, indent=None, ensure_ascii=False)
                outfile.write('\n')
    
    def __to_txt(self,directory:Path,filename:str,template:str,categories:list=None):
        if not isinstance(directory,Path): directory=Path(directory)
        if not filename.endswith('txt'): filename+='.txt'
        with open(directory/filename,'w') as outfile:
            pleco_text=[
                c.to_pleco_entry(template=template,categories=categories)
                for c in self.characters]
            outfile.write('\n'.join(pleco_text))

    def __to_db(self,directory:Path,filename:str,clean=True):
        if not isinstance(directory,Path): directory=Path(directory)
        if not filename.endswith('db'): filename+='.db'
        db_file = directory/filename

        conn,cursor = open_db(db_file)
        
        c_links = []
        table_name = 'Dictionary'
        
        for i,c in enumerate(self.characters):
            c_data = c.to_dict()
            unique = f'{c.unicode_unique_string}_{self.name}'
            
            for entry,result in self.get_linked_grammar(c).items():
                if result!=[]:
                    c_links+=[(unique,grammar.unique_string,entry) for grammar in result]
                else:
                    c_links.append((unique,None,entry))
            
            if i == 0:
                cols = ['"uniq" TEXT UNIQUE','"dict_name" TEXT']+create_column_list(c.default_dtypes)
                if clean: remove_table(cursor,table_name)
                insert_query = create_table(cursor,table_name,cols)
            values = [unique,self.name]+[json.dumps(v) if isinstance(v, (list, dict)) else v for v in c_data.values()]
            cursor.execute(insert_query, values)
                        
        from packages.chd import Grammar
        for i,g in enumerate(self.grammar):
            if isinstance(g,Grammar) and not g.is_empty():
                g_data = g.to_dict()
                if  i == 0:
                    cols = ['"uniq" TEXT UNIQUE']+create_column_list({k:str for k in g_data.keys()})
                    remove_table(cursor,'Grammar')
                    insert_query = create_table(cursor,'Grammar',cols)
                values = [g.unique_string]+[json.dumps(v) if isinstance(v, (list, dict)) else v for v in g_data.values()]
                cursor.execute(insert_query, values)
                
        for i,links in enumerate(c_links):
            if  i == 0:
                cols = [f'"{c}" TEXT' for c in ['character','grammar','entry','dictionary']]
                if clean: cursor.execute(f"DROP TABLE IF EXISTS Links")
                insert_query = create_table(cursor,'Links',cols)
            cursor.execute(insert_query, list(links)+[self.name])
            
        for i,(k,v) in enumerate(self.__categories.items()):
                
            if v==list: v="list"
            elif v==str: v="str"
            elif v==int: v="int"
            elif v==dict: v="dict"
            else: v="str"
            
            if  i == 0:
                cols = [f'"{c}" TEXT' for c in ['category','dtype']]
                if clean: cursor.execute(f"DROP TABLE IF EXISTS Categories")
                insert_query = create_table(cursor,'Categories',cols)
            if not k in get_unique_values(cursor,'Categories','category'):
                cursor.execute(insert_query, [k,v])
                
        close_db(conn)