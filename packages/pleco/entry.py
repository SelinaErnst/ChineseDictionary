
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
        return self.everything
    
    def get_dtypes(self):
        return {k: type(v) for k,v in self.__dict__.items() if not k.startswith('_')}

    def update(self,**kwargs):
        for key,value in kwargs.items():
            self.__dict__[key]=value
            
    def add_to(self,key,element):
        if key in self.__dict__.keys():
            before=self.__dict__[key] if self.__dict__[key] != None else []
            if isinstance(before,str): before=[before]
            if not isinstance(element,list):
                if element not in before:
                    self.__dict__[key]=before+[element]
            else:
                self.__dict__[key]=list(set(before)|set(element))
        else:
            self.__dict__[key]=element
    
    def remove_category(self, key):
        if key in self.__dict__.keys():
            self.__dict__[key]=None
             
    def __repr__(self):
        return str({k:v for k,v in self.__dict__.items() if not k.startswith('_')})
    
    def __str__(self):
        return str({k:v for k,v in self.__dict__.items() if not k.startswith('_')})
    

            
    