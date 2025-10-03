from .entry import entry
from .printentry import plecoprinter, plecoformat


class character():
    def __init__(self,**kwargs):
        self.d=entry(**kwargs)
        self.entry=entry(**kwargs)
        self.printer=plecoprinter(self.entry)   
        self.uniq=(self.entry.simple,self.entry.traditional,self.entry.pronounciation)
        self.__categories=None
        
    def __repr__(self):
        u=['{0:<10}'.format(e) for e in self.uniq]
        s=" | ".join(self.uniq)
        s=f'{s}\n'
        return s
    
    def __str__(self):
        s=", ".join(self.uniq)
        s=f'({s})'
        return s
    
    def to_dict(self):
        return self.entry.to_dict()
    
    def info(self, complete=True):
        string=''
        existing_categories=self.get_existing_categories()
        for cat,values in self.entry.to_dict().items():
            if complete or cat in existing_categories:
                head='{0:17}'.format(cat)
                if isinstance(values,list): 
                    line=f'{head}'
                    tab=f"{'':<17}".format("")
                    for e in values[:-1]:
                        line+=f'- {e}\n{tab}'
                    try:   
                        line+=f'- {values[-1]}\n'
                    except: 
                        pass
                elif isinstance(values,str): line=f'{head}{values}\n'
                elif values==None: line=f'{head}\n'
                else: line=""
                string+=line
        return string
    
    @property
    def categories(self):
        return self.entry.categories
    
    def get_existing_categories(self):
        return [cat for cat,values in self.entry.to_dict().items() if values != None]
    
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
   
    def choose_entry(self,category):
        return self.entry.__dict__[category]
    
    def plecostring(self,
        translation=True,
        information=True,
        meaning=True,
        ancientform=True,
        links=True):
        string=''
        if translation: string+=self.printer.translation()
        if information: string+=self.printer.information()
        if meaning: string+=self.printer.meaning()
        if ancientform: string+=self.printer.ancient_form()
        if links: string+=self.printer.links()
        trad=plecoformat('trad',self.uniq[1])
        uniqstring=f'{self.uniq[0]}{trad}\t{self.uniq[2]}\t'
        return uniqstring+string
    
    def update(self,**kwargs):
        self.entry.update(**kwargs)
        self.d.update(**kwargs)
        self.printer=plecoprinter(self.entry)   
        self.uniq=(self.entry.simple,self.entry.traditional,self.entry.pronounciation)
    
    