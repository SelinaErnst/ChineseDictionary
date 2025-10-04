# import pandas as pd
from .loader import read_plecotxt
from .character import character

class dictionary():
    def __init__(self,name,characters:list=[]):
        self.name = name
        self.characters=characters
        if self.characters!=[]:
            self.__uniqs=[c.uniq for c in self.characters]
        else:
            self.__uniqs=[]
    def __repr__(self):
        return f'dictionary with {len(self.characters)} character entries'
    def __str__(self):
        lines=[line+'\n' for line in self.get_simple_list()]
        # for i,c in enumerate(self.characters):
            # s=", ".join(c.uniq)
            # lines+=[f'{i}. character: {s}\n']
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
        return self
    def __sub__(self,character:character):
        if character.uniq in self.__uniqs:
            self.characters.remove(character)
            self.__uniqs.remove(character.uniq)
        else:
            print('character is not in dictionary')
        return self
    def __getitem__(self,index):
        if isinstance(index,int) and index < len(self.characters):
            return self.characters[index]
        elif isinstance(index,tuple) and index in self.__uniqs:
            return [c for c in self.characters if c.uniq == index][0]  
        elif isinstance(index,str):
            print(index,len([c for c in self.characters if index in c.uniq]))
            # will give a list of possibly matching characters
            characters = [c for c in self.characters if index in c.uniq]
            return dictionary(name=self.name,characters=characters)
        elif isinstance(index,slice):
            characters = [c for c in self.characters[index.start:index.stop]]
            return dictionary(name=self.name,characters=characters)
        else:
            print('WARNING: dictionary cannot work with index')
        
    def __contains__(self, character):
        if character in self.characters or character in self.__uniqs:
            return True
        else:
            return False
        
    def read(self,filename, add=True):
        entrylist=read_plecotxt(filename)
        if entrylist != None:
            if not add: 
                self.characters = []
                self.__uniqs = []
            for char in entrylist:
                c=character(
                    simple=char['CHAR_SIMPL'],
                    traditional=char['CHAR_TRADI'],
                    pronounciation=char['CHAR_PRON'],
                    english=char['ENG'],
                    german=char['GER'],
                    measure_word=char['MW'],
                    radical=char['RAD'],
                    opposite=char['OPP'],
                    strokes=char['STR'],
                    classifier=char['CL'],
                    variants=char['VAR'],
                    relatives=char['REL'],
                    words=char['WRD'],
                    others=char['DIS'],
                    dict_entries=char['DICT'],
                    components=char['COMP'],
                    mneomics=char['MNE'],
                    usage=char['USE'],
                    origin=char['ORG'],
                    ancient=char['ANC'],
                    link=char['LIN']
                    )
                if c.uniq not in self.__uniqs:
                    self.characters.append(c)
                    self.__uniqs.append(c.uniq)
            return True 
        else:
            return False
    
    
    def write(self,filename,indices=None,fileformat='pleco'):
        if fileformat=='pleco':
            with open(filename,'w') as file:
                if indices==None:
                    entrystrings=[c.plecostring() for c in self.characters]
                else:
                    if type(indices)==int:
                        entrystrings=[c.plecostring() for c in self.characters[indices:indices+1]]
                    elif type(indices)==list:
                        entrystrings=[c.plecostring() for i,c in enumerate(self.characters) if i in indices]
                        
                file.write('\n'.join(entrystrings))
        # elif fileformat=='csv':
        #     df=pd.DataFrame([c.d.everything for c in self.characters])
        #     df.to_csv(filename)
        else:
            return [c.d.everything for c in self.characters]
    
    def get_simple_list(self):
        lines=[]
        for i,c in enumerate(self.characters):
            s=", ".join(c.uniq)
            lines+=[f'{i}. character: {s}']
        return lines