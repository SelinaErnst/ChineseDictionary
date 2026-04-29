
class Entry():
    def __init__(self, **kwargs):
        for key,value in kwargs.items():
            if not key.startswith('_'): self.__dict__[key]=value
    
    def __str__(self):
        width=23
        distance=f"{'':<{width}}".format("",width=width)
        def write_list(head:str,values:list|dict,distance:str=distance):
            line=head
            for i,element in enumerate(values):
                if isinstance(values,list):
                    if i+1 != len(values): line+=f'| - {element}\n|{distance[:-1]}'
                    else: line+=f'| - {element}'
                elif isinstance(values,dict):
                    el_values = values[element]
                    if i+1 != len(values): line+=f'| - {element}: {el_values}\n|{distance[:-1]}'
                    else: line+=f'| - {element}: {el_values}'
            return line
        
        string=''
        for cat,values in self.to_dict().items():
            cat='|{0:{width}}'.format(cat.upper(),width=width-3)
            head='\n'+'{0:{width}}'.format(cat,width=width)
            if type(values) in [list,dict]: line = write_list(head=head,values=values)
            elif type(values) in [str,int]: line=f'{head}| {values}'
            elif values==None: line=f'{head}|'
            else: line=""
            string+=line
        return string
    
    def __repr__(self):
        return str(self)   
    
    def __iter__(self):
        for key in self.categories:
            yield (key, self.__dict__[key]) 
            
            
    def __eq__(self,other):
        if isinstance(other,Entry):
            
            def compare_dict(a,b):
                are_dict = lambda a,b: isinstance(a,dict) and isinstance(b,dict)
                are_list = lambda a,b: isinstance(a,list) and isinstance(b,list)
                
                if are_dict(a,b):                
                    all_categories = set(list(a.keys())+list(b.keys()))
                    a = {k:a[k] if k in a.keys() else None for k in all_categories}
                    b = {k:b[k] if k in b.keys() else None for k in all_categories}
                    
                    
                    compare_non = [a[k] == b[k] for k in all_categories if not are_dict(a[k],b[k]) and not are_list(a[k],b[k])]
                    compare_are_dict = [compare_dict(a[k],b[k]) for k in all_categories if are_dict(a[k],b[k])]
                    compare_are_list = [sorted(a[k])==sorted(b[k]) for k in all_categories if are_list(a[k],b[k])]
                    
                    compare_all = compare_non+compare_are_dict+compare_are_list
                    result = all(compare_all)
                    
                    if not result: print('\n'*5,len(compare_all),[(a[k],b[k]) for k in all_categories if a[k]!=b[k]])
                    
                    return all(compare_all)
                else: return a==b
            
            result = compare_dict(self.content,other.content)
            
                
            return result
        
    def __getitem__(self,index:str|list|int|slice):
        if isinstance(index,str):
            if index in self.categories:
                return self.content[index]
        elif isinstance(index,list) and isinstance(index[0],str):
            return {k:v for k,v in self.content.items() if k in index}
        elif isinstance(index,int):
            if index < len(self.categories):
                category = self.categories[index]
                return category,self.content[category]
        elif isinstance(index,slice):
            categories = self.categories[index.start:index.stop]
            return {k:v for k,v in self.content.items() if k in categories}
        else:
            from .character import Character
            print('WARNING: dictionary cannot work with index',isinstance(index,Character))


    @property
    def categories(self):
        return list(self.content.keys())

    @property
    def content(self):
        return {k:v for k,v in self.__dict__.items() if not k.startswith('_')}
    @property
    def dtypes(self):
        return {k: type(v) for k,v in self.__dict__.items() if not k.startswith('_')}

    def to_dict(self):
        return self.content

    def update(self,**kwargs):
        for key,value in kwargs.items():
            if not key.startswith('_'): self.__dict__[key]=value
            
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
    
    def remove(self, key):
        if key in self.__dict__.keys():
            self.__dict__[key]=None