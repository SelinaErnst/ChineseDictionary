from .entry import entry
from .printentry import plecoprinter, plecoformat, link_pronunciations, decode_pinyin, encode_pinyin
import re

defaultkeys={
    'simple':str, #not list
    'traditional':str, #not list
    'pronunciation':str, #not list
    'english':list,
    'german':list,
    'measure_word':list,
    'radical':list,
    'opposite':list,
    'strokes':str,
    'strokes_count':int, #not list
    'classifier':list,
    'variants':list,
    'relatives':list,
    'words':list,
    'others':list,
    'dict_entries':list,
    'components':list,
    'mnemonics':list,
    'usage':list,
    'origin':str, #not list
    'ancient':list,
    'images':dict, #not list
    'link':list,
    'image_urls':list,
}

class character():
    def __init__(self, startkeys=None,**kwargs):
        # defines every category that is included from the start
        # also: ORDER
        self.default_keys=defaultkeys if startkeys == None else startkeys
        
        startkeys={k : kwargs[k] if k in kwargs.keys() else None for k in self.default_keys.keys()}
        if 'pronounciation' in kwargs.keys(): startkeys.update({'pronunciation':kwargs['pronounciation']})
        
        self.entry=entry(**startkeys)
        self.entry.pronunciation = encode_pinyin(self.entry.pronunciation)
        self.__printer=plecoprinter(self.entry)   
        self.__uniq=(self.entry.simple,self.entry.traditional,self.entry.pronunciation)
        # self.__dictionary=None
        
    def __repr__(self):
        uniq=list(self.__uniq)
        uniq[2]=self.show_pinyin()
        u=['{0:<10}'.format(str(e)) for e in self.__uniq]
        s=" | ".join([str(e) for e in uniq])
        s=f'{s}\n'
        return s
    
    def __str__(self):
        uniq=list(self.__uniq)
        # uniq[2]=self.show_pinyin()
        s=", ".join([str(e) for e in uniq])
        s=f'({s})'
        return s
    
    def to_dict(self):
        return self.entry.to_dict()
    
    def info(self, complete=True):
        string=''
        existing_categories=self.get_existing_categories()
        for cat,values in self.entry.to_dict().items():
            if complete or cat in existing_categories:
                head='\n'+'{0:17}'.format(cat)
                if isinstance(values,list): 
                    line=f'{head}'
                    tab=f"{'':<17}".format("")
                    for i,e in enumerate(values):
                        if i+1 != len(values):
                            line+=f'- {e}\n{tab}'
                        else:
                            line+=f'- {e}'
                elif isinstance(values,dict): 
                    line=f'{head}'
                    tab=f"{'':<17}".format("")
                    for i,(k,v) in enumerate(values.items()):
                        if i+1 != len(values):
                            line+=f'- {k}: {v}\n{tab}'
                        else:
                            line+=f'- {k}: {v}'
                elif type(values) in [str,int]: line=f'{head}{values}'
                elif values==None: line=f'{head}'
                else: line=""
                string+=line
        return string
    
    @property
    def categories(self):
        return self.entry.categories

    @property
    def uniq(self):
        return (self.entry.simple,self.entry.traditional,self.entry.pronunciation)
    
    @property
    def printer(self):
        return plecoprinter(self.entry)
    
    def get_existing_categories(self):
        return [cat for cat,values in self.entry.to_dict().items() if values != None]
    
    def get_missing_categories(self):
        return [cat for cat,values in self.entry.to_dict().items() if values == None]
    
    def is_radical(self):
        valid_category_names = ['radical']
        return bool(set(self.get_existing_categories()) & set(valid_category_names))
    def is_measure_word(self):
        valid_category_names = ['measure_word']
        return bool(set(self.get_existing_categories()) & set(valid_category_names))
    def is_grammatical(self):
        valid_category_names = ['dict_entries']
        return bool(set(self.get_existing_categories()) & set(valid_category_names))
    def has_translation(self):
        valid_category_names = ['english','german']
        return bool(set(self.get_existing_categories()) & set(valid_category_names))
   
    def get_property(self,category):
        if category in self.entry.categories:
            return self.entry.__dict__[category]
    
    def get_default_dtype(self,category):
        if category in self.default_keys:
            return self.default_keys[category]
    
    def remove_property(self,category):
        self.entry.remove_category(category)
    
    def allows_multiple(self,category,defaultkeys=defaultkeys):
        if category in defaultkeys.keys():
            if defaultkeys[category]==list:
                return True
            else:
                return False
        else:
            return False
        
    def plecostring(self,
        translation=True,
        information=True,
        meaning=True,
        ancientform=True,
        words_and_characters=True,
        links=True,
        ):
        string=''
        if translation: string+=self.__printer.translation()
        if information: string+=self.__printer.information()
        if meaning: string+=self.__printer.meaning()
        if ancientform: string+=self.__printer.ancient_form()
        if words_and_characters: string+=self.__printer.words_and_characters()
        if links: string+=self.__printer.links()
        trad=plecoformat('trad',self.__uniq[1])
        uniqstring=f'{self.__uniq[0]}{trad}\t{encode_pinyin(self.__uniq[2])}\t'
        return link_pronunciations(uniqstring+string)
    
    def update(self,kwargs,get_dtype_warning=False):

        self.entry.update(**kwargs)
        self.__printer=plecoprinter(self.entry)   
        self.__uniq=(self.entry.simple,self.entry.traditional,self.entry.pronunciation)
        if get_dtype_warning: self.check_dtypes()
        
    def check_dtypes(self):
        dtypes = self.entry.get_dtypes()
        wrong_dtypes=[]
        for category in self.categories:
            if self.entry.__dict__[category] != None and \
                self.default_keys[category] != dtypes[category]:
                    wrong_dtypes+=[category]
        if wrong_dtypes!=[]:
            print(f'The character {self} has incorrect dtypes for categories:',', '.join(wrong_dtypes))
            return False
        else: return True
        
    def update_images(self,kwargs):
        if not hasattr(self.entry,'images') or self.entry.__dict__['images']==None:
            self.entry.__dict__['images']={}
            image_dict={}
        else:
            image_dict=self.entry.__dict__['images']
        image_dict.update(kwargs)
        self.entry.__dict__['images']=image_dict
        
    def convert_to_unicode(self, character=None):
        character=self.__uniq[:2] if character==None else character
        if isinstance(character, str):
            if len(character)>0:
                character=[c for c in character]
            elif len(character)==1:
                unicode=f'U+{ord(c):04X}'
            else:
                unicode=None
        if isinstance(character,list) or isinstance(character,tuple):
            unicode=[]
            for char in character:
                for c in char:
                    if isinstance(c,str) and len(c)>0: unicode+=[f'U+{ord(c):04X}']
        return unicode
    
    def show_pinyin(self):
        return decode_pinyin(self.entry.pronunciation)
    
    def remove_pinyin(self, text=None):
        text = self.entry.pronunciation if text==None else text
        text = encode_pinyin(text)
        text = re.sub(r'\d+', '', text)
        return text
    
    def unicode_unique_string(self):
        unicode = '_'.join([c.replace('+','') for c in self.convert_to_unicode()])
        pronunciation = self.uniq[2]
        string = f'{pronunciation}_{unicode}'
        return string