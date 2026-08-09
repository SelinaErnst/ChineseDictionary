import re
from packages.chd import Character, Sentence, Dictionary
from packages.kivy import (
    MyScreen,   
    BooleanProperty,
    ObjectProperty,
    CategoryItem,
    StringProperty,
    DictProperty
)

class ShowGrammar(MyScreen):
    # edited=BooleanProperty(False)
    editable=BooleanProperty(True)
    grammar = ObjectProperty()
    parent_screen = ObjectProperty()
    
    level = StringProperty()
    title = StringProperty()
    subtitle = StringProperty()
    
    widgets = DictProperty()
    
    def __init__(self, grammar=None,**kwargs):
        self.grammar = grammar
        if self.grammar != None: self.__update_attrs()
        super().__init__(**kwargs)
        # self.build_scroll()
        
    def __update_attrs(self):
        self.level = self.grammar.level
        self.title = self.grammar.title
        self.subtitle = self.grammar.subtitle
        
    def build_scroll(self,grammar=None):
        from functools import partial
        from kivy.clock import Clock
        
        self.clean_scroll()
        if grammar!=None: 
            self.grammar = grammar
            self.__update_attrs()
        self.parent_screen = self.get_screen('gram_list')
        

        def list_all_content(grammar):
            # queue = list(grammar.categories)
            # def list_next(p):
            #     if not queue: return 
            #     category = queue.pop(0)
            #     self.list_content(category=category,content=grammar[category])
            #     Clock.schedule_once(list_next,.1)
            # Clock.schedule_once(list_next,0)
            
            for category in grammar.categories:
                self.list_content(category=category,content=grammar[category])
        
        # Clock.schedule_once(lambda *args: list_all_content(grammar=self.grammar), 0.25)
        list_all_content(grammar=self.grammar)
            
    def clean_scroll(self):
        self.ids.scroll.clear_widgets()
    
    def list_content(self,category,content):
        small_bullets=['tags']
        small_text=['structures','opposite_structures','characters','opposite_characters']
        long_text=['explanation','sentences']
        # rest=['level','title','subtitle']
        if category == 'explanation' and isinstance(content,str):
            content = re.sub(r'[■|●|□|○|◼]','■',content)
        if category in small_text:
            # list of rows next to head (take up all the rest space)
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=False,line_width=330,head_width=470,editable=self.editable)
        elif category in long_text:
            # list of rows below head
            l=CategoryItem(
                category=category,values=content,
                cols=1,small=False,head_width=None,editable=self.editable)
        elif category in small_bullets:
            # list of rows next to head (don't take up all the rest space)
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=True,line_width=500,head_width=250,editable=self.editable)
        else:
            # list of rows next to head (take up all the rest space)
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=False,line_width=330,head_width=250,editable=self.editable)
            
        if not self.editable and isinstance(self.grammar[category],Dictionary): 
            if len(self.grammar[category])==0: return None
        if self.editable or self.grammar[category] not in [[],"",None]:
            self.ids.scroll.add_widget(l)
            self.scroll.ids[category]=l
        
    def empty_grammar(self):
        if self.editable:
            self.grammar.clear()
            self.parent_screen.set_list_items()
            # self.clean_scroll()
            self.build_scroll()
            self.parent_screen.edited = True
    
    def edit_category(self,category):
        if self.editable:
            title=category.replace('_',' ').title()
            category=category.lower().replace(' ','_')
            content = self.grammar[category]
            
            if category == "characters":
                content={'simple':'','traditional':'','pronunciation':''}
                title="Add Character"
            if category == "opposite_characters":
                content={'simple':'','traditional':'','pronunciation':''}
                title="Add Opposite Character"
            elif category=="sentences": 
                content={'text':'','pronunciation':'','translation':''}
                title="Add Sentence"
                
            dialog = self.my_app.pre_loaded_widgets['edit_element']
            
            if category == "tags":
                dialog.choose_content(style='custom',options=self.get_tags(),allow_multiple=True,dtype=list,title='Tags')
            elif isinstance(content,str):
                dialog.choose_content(style='normal',allow_multiple=False,dtype=str,title=title)
            elif isinstance(content,list) and (len(content)>0 and isinstance(content[0],str) or len(content)==0):
                dialog.choose_content(style='normal',allow_multiple=True,dtype=list,title=title)
            elif isinstance(content,dict): 
                dialog.choose_content(style='dict',title=title)
            else: dialog = None
            
            if dialog != None:
                # print('\n\nedit_category',content)
                dialog.set_entry(entry=content)
                dialog.open()
            
    def update_category(self,category,entry,original=None):
        self.parent_screen.edited = True
        gr_index = self.parent_screen.grammar_list.index(self.grammar)
        if category.startswith('add') or category.startswith('edit'):
            if category.endswith('character') and entry!=None:
                entry = Character(**entry)
                if original!=None and original in self.grammar.opposite_characters:
                    self.grammar.opposite_characters-original
                    self.grammar.add_opp_character(entry)
                    category="opposite_characters"
                elif original!=None and original in self.grammar.characters:
                    self.grammar.characters-original
                    self.grammar.add_character(entry)
                    category="characters"
                elif category == 'add_opposite_character':
                    self.grammar.add_opp_character(entry)
                    category="opposite_characters"
                elif category == 'add_character':
                    self.grammar.add_character(entry)
                    category="characters"
                    
            elif category.endswith('sentence') and entry!=None:
                entry = Sentence(**entry)
                if original!=None and original in self.grammar.sentences: 
                    self.grammar.remove_sentence(original)
                    self.grammar.add_sentence(entry)
                    category="sentences"
                elif category == 'add_sentence':
                    self.grammar.add_sentence(entry)
                    category="sentences"
                    
        if category == 'level':
            entry = entry if entry != None else ""
            self.grammar.level = entry
            self.__update_attrs()
        elif category == 'title':
            entry = entry if entry != None else ""
            self.grammar.title = entry
            self.__update_attrs()
        elif category == 'subtitle':
            entry = entry if entry != None else ""
            self.grammar.subtitle = entry
            self.__update_attrs()
        elif category == 'tags':
            entry = entry if entry != None else []
            self.grammar.tags = entry
        elif category == 'structures':
            entry = entry if entry != None else []
            self.grammar.structures = entry
        elif category == 'opposite_structures':
            entry = entry if entry != None else []
            self.grammar.opposite_structures = entry
        elif category == 'explanation':
            entry = entry if entry != None else ""
            self.grammar.explanation = entry
        if self.grammar != self.parent_screen.grammar_list[gr_index]:
            kwargs = self.grammar.to_dict()
            self.parent_screen.grammar_list[gr_index].update(**kwargs)
        if category in self.ids.scroll.ids:
            self.ids.scroll.ids[category].remove_content()
            self.ids.scroll.ids[category].list_category(values=self.grammar[category])
        self.parent_screen.set_list_items()
    
    def get_tags(self):
        
        def __tag_list(tag_list=[],mark_head='>',mark_comment='#',count=0):        
            if tag_list == []: return [],0
            elif tag_list[0].startswith(mark_head): return [],0
            elif tag_list[0].startswith(mark_comment): 
                next_tags,count = __tag_list(tag_list=tag_list[1:],mark_head=mark_head,count=count)
                return next_tags, count+1
            else: 
                next_tags,count = __tag_list(tag_list=tag_list[1:],mark_head=mark_head,count=count)
                return [tag_list[0]]+next_tags, count+1
        
        def __tag_dict(tag_list:list=[],tag_dict:dict={},mark_head:str='>',mark_comment:str='#'):
            if tag_list==[]:
                pass
            elif tag_list[0].startswith(mark_head):
                head = tag_list[0].lstrip('>').strip()
                tags,n_tags = __tag_list(tag_list[1:])
                tag_dict.update({head:[t for t in tags if not t.startswith(mark_comment)]})
                __tag_dict(tag_list=tag_list[n_tags+1:],tag_dict=tag_dict,mark_head=mark_head,mark_comment=mark_comment)
            else:
                tags,n_tags = __tag_list(tag_list)
                __tag_dict(tag_list=tag_list[n_tags:],tag_dict=tag_dict,mark_head=mark_head,mark_comment=mark_comment)
            return tag_dict
    
        grammar_tags = self.get_app_file('grammar_tags')
        if grammar_tags==None:
            grammar_tags=[]
            self.my_app.save_app_config(grammar_tags,'grammar_tags')
        tags = __tag_dict(grammar_tags,{},'>','#')
        
        # print('\n\nget_tags',tags)
        
        return tags