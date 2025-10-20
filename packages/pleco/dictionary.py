# import pandas as pd
import json
import os
from .loader import read_plecotxt
from .character import character
import re
from .printentry import encode_pinyin

class dictionary():
    def __init__(self,name,characters=None,sorting_key='pronunciation'):
        self.name = name
        if characters != None and isinstance(characters,list):
            self.characters=characters
        else:
            self.characters=[]
        if self.characters!=[]:
            self.__uniqs=[c.uniq for c in self.characters]
        else:
            self.__uniqs=[]
        self._sorting_key=sorting_key
        self.sort()
        
    @property
    def sorting_key(self):
        return self._sorting_key

    @sorting_key.setter
    def sorting_key(self, key):
        if key in ['simple','traditional','pronunciation']:
            self._sorting_key = key
            self.sort()
        
    def __repr__(self):
        return f'dictionary with {len(self.characters)} character entries'
    def __str__(self):
        lines=[line+'\n' for line in self.get_simple_list()]
        return ''.join(lines)
    def __iter__(self):
        return iter(self.characters)

    def __add__(self,other):
        if isinstance(other,character):
            if other.uniq not in self.__uniqs:
                self.characters.append(other)
                self.__uniqs.append(other.uniq)
            else:
                print(f'character {(other)} was not added to dictionary, it already exists')
        if isinstance(other,dictionary):
            for c in other:
                if c not in self.characters:
                    self.characters.append(c)
                    self.__uniqs.append(c.uniq)                  
                else:
                    print(f'character {c} was not added to dictionary, it already exists')
        self.sort()
        return self
    def __sub__(self,character:character):
        if character.uniq in self.__uniqs:
            self.characters.remove(character)
            self.__uniqs.remove(character.uniq)
        else:
            print('character is not in dictionary')
        self.sort()
        return self
    def __getitem__(self,index):
        if isinstance(index,int) and index < len(self.characters):
            return self.characters[index]
        elif isinstance(index,tuple) and index in self.__uniqs:
            return [c for c in self.characters if c.uniq == index][0]  
        elif isinstance(index,str):
            # will give a list of possibly matching characters
            characters = [c for c in self.characters if index in c.uniq]
            return dictionary(name=self.name,characters=characters)
        elif isinstance(index,slice):
            characters = [c for c in self.characters[index.start:index.stop]]
            return dictionary(name=self.name,characters=characters)
        elif isinstance(index,character):
            index=index.uniq
            return [c for c in self.characters if c.uniq == index][0]  
        else:
            print('WARNING: dictionary cannot work with index',isinstance(index,character))
        
    def __contains__(self, character):
        if character in self.characters or character in self.__uniqs:
            return True
        else:
            return False
    
    def sort(self):
        self.characters.sort(key=lambda x: encode_pinyin(x.get_property(self.sorting_key)) if x.get_property(self.sorting_key)!=None else "")
        self.__uniqs=[c.uniq for c in self.characters]
        return self

    def rename(self,name):
        self.name = name
    
    def read(self,filename,file_format,add=True):
        if file_format == 'pleco':
            return self.read_pleco(filename,add)
        elif file_format == 'jsonl':
            if filename.endswith('.jsonl'):
                return self.read_jsonl(filename,add)
            else: return False
    def read_jsonl(self,filename,add=True):
        try:
            with open(filename,'r') as file:
                json_list = list(file)
            if not add:
                self.characters=[]
                self.__uniqs=[]
            for json_str in json_list:
                entry=json.loads(json_str)
                c = character(**entry)
                if c.uniq not in self.__uniqs:
                    self.characters.append(c)
                    self.__uniqs.append(c.uniq)
            self.sort()
            return True
        except:
            return False
                    
    def read_pleco(self,filename, add=True):
        entrylist=read_plecotxt(filename)
        if entrylist != None:
            if not add: 
                self.characters = []
                self.__uniqs = []
            for char in entrylist:
                counts = sum([int(count) for count in re.findall(r'\((\d*)\)',char['STR'])]) if char['STR']!=None else None
                c=character(
                    simple=char['CHAR_SIMPL'],
                    traditional=char['CHAR_TRADI'],
                    pronunciation=char['CHAR_PRON'],
                    english=char['ENG'],
                    german=char['GER'],
                    measure_word=char['MW'],
                    radical=char['RAD'],
                    opposite=char['OPP'],
                    strokes=char['STR'],
                    strokes_count=counts,
                    classifier=char['CL'],
                    variants=char['VAR'],
                    relatives=char['REL'],
                    words=char['WRD'],
                    others=char['DIS'],
                    dict_entries=char['DICT'],
                    components=char['COMP'],
                    mnemonics=char['MNE'],
                    usage=char['USE'],
                    origin=char['ORG'],
                    ancient=char['ANC'],
                    link=char['LIN']
                    )
                if c.uniq not in self.__uniqs:
                    self.characters.append(c)
                    self.__uniqs.append(c.uniq)
            self.sort()
            return True 
        else:
            return False
    
    
    def write(self,directory='./',filename=None,indices=None,file_format='pleco',**kwargs):
        filename = self.name if filename == None else filename
        entries=self.characters

        if indices!=None:
            if type(indices)==int:
                entries=[e for e in entries[indices:indices+1]]
            elif type(indices)==list:
                entries=[e for i,e in enumerate(entries) if i in indices]
                
        if file_format in ['pleco','txt']:
            components = {k:v for k,v in kwargs if k in ['translation','information','meaning','ancientform','links']}
            filename = filename+'.txt' if filename == self.name else filename
            with open(directory+filename,'w') as file:
                entrystrings=[
                    e.plecostring(**components)
                    for e in entries]
                file.write('\n'.join(entrystrings))
                
        elif file_format=='jsonl':
            filename = filename+'.jsonl' if filename == self.name else filename
            if filename.endswith('.jsonl'):
                with open(directory+filename,'w') as outfile:
                    for e in entries:
                        
                        json.dump(e.to_dict(), outfile)
                        outfile.write('\n')
                        
            # elif file_format=='csv':
        #     df=pd.DataFrame([c.d.everything for c in self.characters])
        #     df.to_csv(filename)
        # else:
        #     return [c.d.everything for c in self.characters]
    
    def get_simple_list(self):
        lines=[]
        for i,c in enumerate(self.characters):
            s=", ".join([str(e) for e in c.uniq])
            lines+=[f'{i}. character: {s}']
        return lines