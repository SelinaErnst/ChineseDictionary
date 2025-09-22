from .entry import entry
from .printentry import plecoprinter, plecoformat


class character():
    def __init__(self,**kwargs):
        self.d=entry(**kwargs)
        self.entry=entry(**kwargs)
        self.printer=plecoprinter(self.entry)   
        self.uniq=(self.entry.simple,self.entry.traditional,self.entry.pronounciation)
        self.__categories=None
        # self.__dictionary=
        
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
    
    def info(self):
        string=''
        for k in self.entry.categories:
            v=self.entry.__dict__[k]
            head='{0:<20}'.format(k)
            if isinstance(v,list): 
                # lists=f"\n{'':<20}- ".join(v)
                lists="".join(["\n"+f"{'':<20}".format(e) for e in v])
                string+=f'{head}- {lists}\n'
            elif isinstance(v,str): string+=f'{head}{v}\n'
            elif v==None: string+=f'{head}\n'
        # print(string)
        return string
    
    @property
    def categories(self):
        return self.entry.categories
    
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
    
    