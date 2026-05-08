from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.button import MDIconButton
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ListProperty,
    ColorProperty,
    ObjectProperty,
    BooleanProperty,
    )

from packages.chd import Grammar
from .dialogs import EditElement
from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/listitems.kv')

class TableRow(MDBoxLayout):
    # used in: ConfirmChoice
    head=StringProperty()
    head_width=NumericProperty(250)
    content=StringProperty()
    role=StringProperty('small')
    spacing=NumericProperty(0)
    
class CustomListItem(RectangularRippleBehavior, ButtonBehavior, MDAnchorLayout):
    text = StringProperty()
    
class MyListItem(CustomListItem):
    func=ObjectProperty()

class MyMultiLineItem(CustomListItem):
    func=ObjectProperty()
    
class PaletteColor(MDBoxLayout):
    color_name=StringProperty('surfaceContainerLowColor')
    palette=StringProperty()
    
    def update_color(self,palette):
        # print(palette, self.palette)
        if palette not in ["",None]: self.palette=palette
        if self.palette in ["",None]: return 'white'
        else: return self.get_color(palette=self.palette,color_name=self.color_name)
    
    def get_color(self,palette,color_name):
        from packages.chd import load_json
        palette_colors = load_json('appdata/colors/palette_colors.json')
        return palette_colors[self.theme_cls.theme_style][palette.capitalize()][color_name]
    
class PaletteItem(CustomListItem):
    color_onea = ColorProperty()
    color_oneb = ColorProperty()
    color_onec = ColorProperty()
    color_oned = ColorProperty()
    color_onee = ColorProperty()
    color_onef = ColorProperty()
    color_oneg = ColorProperty()
    color_twoa = ColorProperty()
    color_twob = ColorProperty()
    color_twoc = ColorProperty()
    color_twod = ColorProperty()
    color_twoe = ColorProperty()
    color_twof = ColorProperty()
    color_trea = ColorProperty()
    color_treb = ColorProperty()
    color_trec = ColorProperty()
    color_tred = ColorProperty()
    color_tree = ColorProperty()
    color_tref = ColorProperty()
    
class DictionaryItem(CustomListItem):
    character = ObjectProperty()


class EntryType(MDIconButton):
    def choose_icon(self, is_type,icons=['alpha-a-box-outline','alpha-a-box']):
        return icons[int(is_type)]
    
    def get_size(self,is_type,sizes=[0,40]):
        return sizes[int(is_type)]
    
class GrammarItem(RecycleDataViewBehavior,CustomListItem):
    grammar = ObjectProperty(Grammar())
    tags = ListProperty([])
    
    def refresh_view_attrs(self, rv, index, data):
        super().refresh_view_attrs(rv, index, data)
        self.list_tags(data['tags'])
        
    def list_tags(self,tags):
        self.ids.tags.clear_widgets()
        for tag in self.grammar.tags:
            t=Tag(text=tag)
            self.ids.tags.add_widget(t)
            
    def get_category(self,grammar,category):
        if category == "structure":
            result = grammar["structures"]
            if isinstance(result,list) and len(result)>0: return result[0]
            else: return ""
        return grammar[category]
    
class Tag(MDAnchorLayout):
    text=StringProperty()
class CategoryHead(RectangularRippleBehavior, ButtonBehavior,MDAnchorLayout):
    pass

class CategoryLine(MDBoxLayout):
    text=StringProperty()
    small=BooleanProperty(True)
class CategoryText(MDBoxLayout):
    text=StringProperty()
    small=BooleanProperty(True)
class RemovableCategoryLine(MDBoxLayout):
    data=ObjectProperty()
    text=StringProperty()
    content=ObjectProperty()
    category=StringProperty()
    
    def remove_line(self):
        from packages.chd import Character,Sentence
        from main import ChD
        app = ChD.get_running_app()
        child = [child for child in self.content.children if child == self]
        if child != []:
            child = child[0]
            if isinstance(self.data,Character) and self.category=="characters":
                app.wm.current_screen.grammar.characters - self.data
            elif isinstance(self.data,Character) and self.category=="opposite_characters":
                app.wm.current_screen.grammar.opposite_characters - self.data
            elif isinstance(self.data,Sentence) and self.category=="sentences":
                app.wm.current_screen.grammar.remove_sentence(self.data)
            self.content.remove_widget(child)
            if app.wm.current.startswith('G'):
                app.wm.current_screen.parent_screen.edited=True
            
    def edit_line(self):
        from packages.chd import Character,Sentence
        if isinstance(self.data,Character):
            entry = {k:v for k,v in self.data.to_dict().items() if v!=None}
            dtype = Character
            title = 'Edit Character'
        elif isinstance(self.data,Sentence):
            entry = {k:v if v!=None else "" for k,v in self.data.to_dict().items()}
            dtype = Sentence
            title = 'Edit Sentence'
        else: entry,title = {},""
        dialog = EditElement(style="dict",title=title,dtype=dtype,original=self.data)
        dialog.set_entry(entry)
        dialog.open()
        
class CategoryItem(MDBoxLayout):
    
    def __init__(self, category, values, 
                 cols=1,small=True,line_width=330,head_width=325,*args, **kwargs):
        self.title_text=category.replace('_',' ').title()
        self.category=category
        # self.values=values
        self.head_width=head_width # if None -> variable head sizes
        self.line_width=line_width
        self.small=small
        
        if cols!=2: cols=1
        self.cols=cols
        super().__init__(*args, **kwargs)
        self.list_category(values,small=small,width=line_width)

    def list_category(self,values,small=None,width=None):
        self.values=values
        small = self.small if small==None else small
        width = self.line_width if width==None else width
        
        if len(self.content.children)==0:
            from packages.chd import Dictionary, Sentence, Character
            if type(values) in [list,dict,Dictionary]:
                if isinstance(values,dict): values = [f'{k}: {v}' for k,v in values.items()]
                for v in values:
                    if type(v) in [Sentence, Character]:
                        line=RemovableCategoryLine(text=str(v),data=v,content=self.content,category=self.category)
                    else:
                        line=CategoryLine(text=str(v),small=small,width=width)
                    self.content.add_widget(line)
            else:
                line=CategoryText(text=str(values),small=small,width=width)
                self.content.add_widget(line)

    def remove_content(self):
        self.content.clear_widgets()
        
