
import os
import json
from packages.chd import Grammar
from packages.kivy import (
    MyScreen,   
    ListProperty,
    BooleanProperty,
)
from .show_gram import ShowGrammar

class GrammarList(MyScreen):
    edited=BooleanProperty(False)
    grammar_list=ListProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for child in self.filter.children:
            child.toggle_off()
        self.set_up_screen()
        
    def set_up_screen(self):
        self.edited = False 
        self.grammar_list = []
        self.grammar_list = self.get_grammar_list()
        self.set_list_items()
        
    def get_grammar_list(self):
        path=os.path.join(self.get_setting('app_directory'),'grammar','grammar.jsonl')
        grammar_list = self.read_grammar_jsonl(path)
        grammar_list = list(set(grammar_list))
        def get_sorting_keys(data):
            if isinstance(data,Grammar): return (data.level.lower(),data.title.lower(),data.subtitle.lower())
            else: return ""
        grammar_list.sort(key=lambda data: get_sorting_keys(data))
        return grammar_list
    
    def read_grammar_jsonl(self,path):
        grammar_list=[]
        if os.path.isfile(path):
            with open(path,'r') as file:
                json_list = list(file)
            for json_str in json_list:
                entry=json.loads(json_str)
                grammar_entry = Grammar(**entry)
                grammar_list.append(grammar_entry)
        return grammar_list
    
    def save_grammar(self):
        self.edited=False
        gr_path_jsonl=os.path.join(self.get_setting('grammar_directory'),'grammar.jsonl')
        gr_path_txt=os.path.join(self.get_setting('grammar_directory'),'grammar.txt')
        template=self.get_setting('grammar_template')
        
        from packages.chd import grammar_to_txt, grammar_to_jsonl

        grammar_to_jsonl(grammar=self.grammar_list,path=gr_path_jsonl)
        grammar_to_txt(grammar=self.grammar_list,path=gr_path_txt,template=template)
        
    def create_dataitem(self,grammar,**kwargs):
        dataitem={'grammar':grammar,'callback':lambda x:x}
        dataitem.update(grammar.to_dict())
        kwargs={k:v for k,v in kwargs.items() if v!=None}
        kwargs.update({'tags':grammar.tags.copy()})
        dataitem.update(kwargs)
        return dataitem 
        
    def set_list_items(self):
        from kivy.clock import Clock
        Clock.max_iteration = 24
        self.rv_scroll.data = []
        
        def apply_filter(dataitem):
            include,exclude = self.filter.include,self.filter.exclude
            if dataitem['grammar'].level in include: return True
            elif dataitem['grammar'].level in exclude: return False
            elif include==[] and dataitem['grammar'].level=="": return True
            else: return False
            
        def apply_search(dataitem):
            search_entry = self.search.text
            title = dataitem['grammar'].title.lower()
            subtitle = dataitem['grammar'].subtitle.lower()
            tags = dataitem['grammar'].tags
            if search_entry.lower() in title: return True
            elif search_entry.lower() in subtitle: return True
            elif any([search_entry.lower() in tag.lower() for tag in tags]): return True
            else: return False
        
        for gr in self.grammar_list:
            dataitem=self.create_dataitem(grammar=gr)
            if apply_filter(dataitem) and apply_search(dataitem):
                self.add_list_item(dataitem)
            
    def add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)
        
    def select_grammar(self,grammar):
        screen = ShowGrammar(name='G',grammar=grammar, parent_screen=self)
        self.add_screen(screen=screen,direction='left')
        
    def add_grammar(self):
        grammar=Grammar()
        self.grammar_list.append(grammar)
        screen = ShowGrammar(name='G',grammar=grammar, parent_screen=self)
        self.add_screen(screen=screen,direction='left')
        