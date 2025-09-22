
class entry():
    def __init__(self, **kwargs):
        for key,value in kwargs.items():
            self.__dict__[key]=value
        self.__categories=list(kwargs.keys())
        self.__everything=kwargs
    
    @property
    def categories(self):
        self.__categories=[cat for cat in self.__dict__.keys() if not cat.startswith('_')]
        return self.__categories

    @property
    def everything(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}
    
    def to_dict(self):
        return self.everything()
    
    def __repr__(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}
    
    def update(self,**kwargs):
        for key,value in kwargs.items():
            self.__dict__[key]=value
            
    