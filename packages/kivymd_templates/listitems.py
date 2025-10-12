from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.button import MDIconButton
from .labels import MultiLineLabel, MDLabel

from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ColorProperty,
    ObjectProperty,
    BooleanProperty,
    )

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
    
class CustomListItem(RectangularRippleBehavior, ButtonBehavior, MDBoxLayout):
    text = StringProperty()
    
class MultiLineItem(RectangularRippleBehavior,ButtonBehavior,MDLabel):
    # text=StringProperty()
    # font_style=StringProperty('Label')
    # role=StringProperty('medium')
    pass
    
class PaletteItem(CustomListItem):
    # text = StringProperty()
    color = ColorProperty()
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
    
# CustomListItem
class DirectoryItem(MultiLineItem):
    setting=StringProperty('A')
    
class DictionaryItem(CustomListItem):
    # text = StringProperty()
    char_simp = StringProperty()
    char_trad = StringProperty()
    char_pron = StringProperty()
    character = ObjectProperty()
    is_radical = BooleanProperty()
    is_measure_word = BooleanProperty()
    is_grammatical = BooleanProperty()
    has_translation = BooleanProperty()
    translation = StringProperty()
    # callback = ObjectProperty(lambda x: x)
            
    def see_properties(self):
        from main import ChD, ShowCharacter
        app = ChD.get_running_app()
        char_string = f'C_{self.char_simp}_{self.char_trad}_{self.char_pron}'
        screen = ShowCharacter(name=char_string, character = self.character)
        app.wm.add_widget(screen)
        app.switch_screen(char_string,'left')
        print(self.character.info())
        # for i,l in screen.ids.items():
        #     l.item_list.set_list()
        
class EntryType(MDIconButton):
    the_size=NumericProperty()
    
    def choose_icon(self, is_type,icons=['alpha-a-box-outline','alpha-a-box']):
        return icons[int(is_type)]
    
    def get_size(self,is_type,sizes=[0,40]):
        return sizes[int(is_type)]
        # return sizes[1]

class EntryInfo(MDAnchorLayout):
    the_size=NumericProperty()