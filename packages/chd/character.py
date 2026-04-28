from .entry import Entry
# from .printentry import plecoprinter, plecoformat, link_pronunciations, decode_pinyin, encode_pinyin
import re

default_keys={
    'simple':str, #not list
    'traditional':str, #not list
    'pronunciation':str, #not list
}
    
class Character():
    def __init__(self,needed_categories:dict|None=None,**kwargs):
        # defines every category that is included from the start
        # also: ORDER
        if needed_categories!=None: default_keys.update(needed_categories)
        needed_categories = default_keys
        self.__default_info_categories=needed_categories
        
        # here we get either the respective value or None for each default key
        # this excludes all keys that are in kwargs and not a default key
        char_info={k : kwargs[k] if k in kwargs.keys() else None for k in self.__default_info_categories.keys()}
        
        self.entry=Entry(**char_info)
        from .convert_pleco_txt import encode_pinyin
        self.entry.pronunciation = encode_pinyin(self.entry.pronunciation)
        
    def __repr__(self):
        s = str(self)
        s=f'{s}\n'
        return s
    
    def __str__(self):
        uniq = (self.entry.simple,self.entry.traditional,self.pinyin)
        uniq = [e if e not in [None,""] else " " for e in uniq]
        s=" | ".join([str(e) for e in uniq]) #❘
        s=f'〔 {s} 〕'
        return s
    
    def __eq__(self,other):
        if isinstance(other,Character):
            return self.uniq == other.uniq
        else: return False
    
    def __hash__(self):
        return hash(self.uniq)
    
    def __add__(self,other):
        from .dictionary import Dictionary
        if isinstance(other,Character):
            categories = self.default_dtypes
            categories.update(other.default_dtypes)
            return Dictionary(name=None,characters=[self,other])
        if isinstance(other,Dictionary):
            return other + self
    
    def __getitem__(self, key:str):
        return self.__get_category(category=key)
    
    @property
    def categories(self):
        return self.entry.categories

    @property
    def uniq(self):
        return (self.entry.simple,self.entry.traditional,self.pinyin_numeric)
    
    @uniq.setter
    def uniq(self,uniq):
        from .convert_pleco_txt import encode_pinyin
        simple,traditional=uniq[0],uniq[1]
        pronunciation=encode_pinyin(uniq[2])
        self.update(simple=simple,traditional=traditional,pronunciation=pronunciation)
    
    @property
    def pinyin(self):
        from .convert_pleco_txt import decode_pinyin
        return decode_pinyin(self.entry.pronunciation)
    
    @property
    def pinyin_numeric(self):
        from .convert_pleco_txt import encode_pinyin
        self.entry.pronunciation = encode_pinyin(self.entry.pronunciation)
        return self.entry.pronunciation
    
    @property
    def pinyin_toneless(self):
        return re.sub(r'\d+','',self.pinyin_numeric)
    
    @property
    def clean_variants(self):
        from .unicode_characters import chinese_char
        pattern = rf"([{chinese_char}]+)"
        variants = []
        if hasattr(self.entry,'variants') and self.entry.variants!=None:
            for variant in self.entry.variants:
                clean_variant=re.findall(pattern,variant)
                if clean_variant!=[]: variants.append(clean_variant[0])
        return variants
    
    @property
    def default_dtypes(self):
        return self.__default_info_categories
    
    @property
    def image_files(self):
        if hasattr(self.entry,'images') and isinstance(self.entry.images,dict):
            return self.entry.images
        else: return {}
        
    @property
    def unicode_unique_string(self):
        unicode = '_'.join([c.replace('+','') for c in self.convert_to_unicode()])
        string = f'{self.pinyin_numeric}_{unicode}'
        return string

    @property
    def filled(self):
        return [cat for cat,values in self.entry.to_dict().items() if values != None]
    @property
    def missing(self):
        return [cat for cat,values in self.entry.to_dict().items() if values == None]
    @property
    def valid(self):
        return [cat for cat in self.__default_info_categories.keys()]
    
    def update_valid_categories(self,updater:dict={},**kwargs):
        updater.update(**kwargs)
        self.__default_info_categories.update(updater)
    
    def copy(self):
        kwargs = self.to_dict()
        c = Character(needed_categories=self.__default_info_categories,**kwargs)
        return c
    
    def is_radical(self):
        valid_category_names = ['radical']
        return bool(set(self.filled) & set(valid_category_names))
    def is_measure_word(self):
        valid_category_names = ['measure_word']
        return bool(set(self.filled) & set(valid_category_names))
    def is_grammatical(self):
        valid_category_names = ['dict_entries']
        return bool(set(self.filled) & set(valid_category_names))
    def has_translation(self):
        valid_category_names = ['english','german']
        return bool(set(self.filled) & set(valid_category_names))
    def is_empty(self):
        if self.uniq == (None,None,None): return True
        return False
    
    def __get_category(self,category:str):
        if category in self.entry.categories:
            return self.entry.__dict__[category]
        
    def remove(self,category):
        self.entry.remove(category)
        
    def get_dtype(self,category):
        if category in self.__default_info_categories:
            return self.__default_info_categories[category]
    
    def to_dict(self):
        return self.entry.to_dict()
    
    def to_pleco_entry(self,template):
        from .convert_pleco_txt import Writer
        w = Writer(template=template,character=self)
        w.add_uniq()
        w.link_pronunciations()
        formatted_text = w.text
        return formatted_text
    
    def update(self,update_dict={},get_dtype_warning=False,**kwargs):
        update_dict={k : v for k,v in update_dict.items() if k in self.__default_info_categories.keys()}
        kwargs={k : v for k,v in kwargs.items() if k in self.__default_info_categories.keys()}
        kwargs.update(update_dict)
        self.entry.update(**kwargs)
        if get_dtype_warning: self.check_dtype()
        return self
        
    def check_dtype(self,category:str=None):
        dtypes = self.entry.dtypes
        wrong_dtypes=[]
        # for all categories
        if category == None:
            for category in self.categories:
                if self.entry.__dict__[category] != None and \
                    self.__default_info_categories[category] != dtypes[category]:
                        wrong_dtypes+=[category]
            if wrong_dtypes!=[]:
                print(f'The character {self} has incorrect dtypes for categories:',', '.join(wrong_dtypes))
                return False
            else: return True
        # for given category
        elif category in self.__default_info_categories:
            return self.__default_info_categories[category] == dtypes[category]
        
    def update_images(self,kwargs=None):
        if isinstance(kwargs,dict):
            if not hasattr(self.entry,'images') or self.entry.__dict__['images']==None:
                self.entry.__dict__['images']={}
                image_dict={}
            else:
                image_dict=self.entry.__dict__['images']
            image_dict.update(kwargs)
        elif kwargs==None: image_dict=kwargs
        self.entry.__dict__['images']=image_dict
    
        
    def download_svg_from_url(self,url,path,dpi=300,scale=1):
        from kivy.utils import platform
        if platform in ['linux']:
            import cairosvg
            if url.endswith('svg'):
                cairosvg.svg2png(url=url,write_to=path,dpi=dpi,scale=scale)
        
    def convert_to_unicode(self):
        symbols=self.uniq[:2]
        unicode=[]
        for symbol in symbols:
            for e in symbol:
                if isinstance(e,str) and len(e)>0: unicode+=[f'U+{ord(e):04X}']
        return unicode
    
    def merge(self,character,overwrite_all=False,get_warning=False):
        updates = self.find_differences_to(character)
        print(updates)
        actual_updates = {}
        undecided = {}
        for k,v in updates.items():
            if v['current'] == None: 
                # all currently categories with None are overwritten by merge
                actual_updates[k] = v['incoming']
            elif overwrite_all and v['incoming'] != None:
                # by choosing overwrite_all, even when current character has a value it is overwritten
                actual_updates[k] = v['incoming']
            else:
                # if not overwrite_all, there is not a decision made between current or incoming
                undecided[k]=v
        if get_warning: 
            lines = [
                f'- {k}: \n\tcurrent: {v["current"]}\n\tincoming: {v["incoming"]}' 
                for k,v in undecided.items()]
            print('UNDECIDED:','\n'+'\n'.join(lines))
            lines = [
                f'- {k}: \n\tcurrent: {v["current"]}\n\t! incoming: {v["incoming"]}' 
                for k,v in updates.items() if k in actual_updates.keys()]
            print('DECIDED:','\n'+'\n'.join(lines))
        self.update(update_dict=actual_updates,get_dtype_warning=True)     
        return actual_updates, undecided
        
    def find_differences_to(self,character):
        updates={}
        if character != None:
            combined_categories = list(set(character.categories + self.categories))
            for cat in combined_categories:
                if self.__get_category(cat) != character.__get_category(cat):
                    dif_values = {'current': self.__get_category(cat), 'incoming':character.__get_category(cat)}
                    updates[cat]=dif_values
        return updates
    
    def info(self, keep_empty:bool=True):
        if keep_empty: return str(self.entry)
        else:
            filled_lines=[]
            for line in str(self.entry).split('\n'):
                for cat in self.filled:
                    head=f'|{cat.upper()}'
                    if line.startswith(head): filled_lines.append(line)
            return '\n'.join(filled_lines)