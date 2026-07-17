import re
from packages.chd import Character, Sentence, Dictionary
from packages.kivy import (
    MyScreen,   
    BooleanProperty,
    ObjectProperty,
    CategoryItem,
    EditElement,
)


class ShowGrammar(MyScreen):
    # edited=BooleanProperty(False)
    editable=BooleanProperty(True)
    grammar = ObjectProperty()
    parent_screen = ObjectProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_scroll()
    
    def build_scroll(self):
        for category in self.grammar.categories:
            self.list_content(category=category,content=self.grammar[category])
            
    def clean_scroll(self):
        # for c in [c for c in self.ids.scroll.children]:
            # c.clear_widgets()
        self.ids.scroll.clear_widgets()
    
    def list_content(self,category,content):
        small_text=['level','title','subtitle','tags']
        long_text=['explanation','sentences','structures','opposite_structures','characters','opposite_characters']
        if category == 'explanation' and isinstance(content,str):
            content = re.sub(r'[■|●|□|○|◼]','■',content)
        if category in small_text:
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=False,line_width=330,head_width=200,editable=self.editable)
        elif category in long_text:
            l=CategoryItem(
                category=category,values=content,
                cols=1,small=False,head_width=None,editable=self.editable)
        else:
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=True,line_width=330,head_width=200,editable=self.editable)
            
        if not self.editable and isinstance(self.grammar[category],Dictionary): 
            if len(self.grammar[category])==0: return None
        if self.editable or self.grammar[category] not in [[],"",None]:
            self.ids.scroll.add_widget(l)
            self.scroll.ids[category]=l
        
    def empty_grammar(self):
        if self.editable:
            self.grammar.clear()
            self.parent_screen.set_list_items()
            self.clean_scroll()
            self.build_scroll()
            self.parent_screen.edited = True
    
    def edit_category(self,category):
        if self.editable:
            title=category.replace('_',' ').title()
            category=category.lower().replace(' ','_')
            content = self.grammar[category]
            dialog = None
            
            if category == "characters":
                content={'simple':'','traditional':'','pronunciation':''}
                title="Add Character"
            if category == "opposite_characters":
                content={'simple':'','traditional':'','pronunciation':''}
                title="Add Opposite Character"
            elif category=="sentences": 
                content={'text':'','pronunciation':'','translation':''}
                title="Add Sentence"
            
            if category == "tags":
                dialog = EditElement(style="custom",allow_multiple=True,dtype=list,title=title,options=self.grammar.valid_tags)
            elif isinstance(content,str):
                dialog = EditElement(style="normal",allow_multiple=False,dtype=str,title=title)
            elif isinstance(content,list) and (len(content)>0 and isinstance(content[0],str) or len(content)==0):
                dialog = EditElement(style="normal",allow_multiple=True,dtype=list,title=title)
            elif isinstance(content,dict): 
                dialog = EditElement(style="dict",title=title)
            if dialog != None:
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
        if category == 'tags':
            entry = entry if entry != None else []
            self.grammar.tags = entry
        elif category == 'title':
            entry = entry if entry != None else ""
            self.grammar.title = entry
        elif category == 'subtitle':
            entry = entry if entry != None else ""
            self.grammar.subtitle = entry
        elif category == 'explanation':
            entry = entry if entry != None else ""
            self.grammar.explanation = entry
        elif category == 'structures':
            entry = entry if entry != None else []
            self.grammar.structures = entry
        elif category == 'opposite_structures':
            entry = entry if entry != None else []
            self.grammar.opposite_structures = entry
        if self.grammar != self.parent_screen.grammar_list[gr_index]:
            kwargs = self.grammar.to_dict()
            self.parent_screen.grammar_list[gr_index].update(**kwargs)
        if category in self.ids.scroll.ids:
            self.ids.scroll.ids[category].remove_content()
            self.ids.scroll.ids[category].list_category(values=self.grammar[category])
        self.parent_screen.set_list_items()