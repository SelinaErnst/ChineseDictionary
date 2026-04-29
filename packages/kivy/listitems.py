from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.button import MDIconButton
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ColorProperty,
    ObjectProperty,
    BooleanProperty,
    )

from packages.chd import Grammar
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
        print(palette, self.palette)
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

class CategoryItem(CustomListItem):
    key = StringProperty()
        
class EntryType(MDIconButton):
    def choose_icon(self, is_type,icons=['alpha-a-box-outline','alpha-a-box']):
        return icons[int(is_type)]
    
    def get_size(self,is_type,sizes=[0,40]):
        return sizes[int(is_type)]
    
class GrammarItem(CustomListItem):
    grammar = ObjectProperty()
    
    def __init__(self, **kwargs):
        self.grammar = Grammar()
        super().__init__(**kwargs)
        
    def get_category(self,grammar,category):
        if category == "structure":
            result = grammar["structures"]
            if isinstance(result,list) and len(result)>0: return result[0]
            else: return ""
        # elif category == "level_color":
            # if self.level.startswith('A'): return 'green'
            # elif self.level.startswith('B'): return 'orange'
            # elif self.level.startswith('C'): return 'red'
            # else: 
            # return self.theme_cls.onPrimaryColor
        return grammar[category]
        