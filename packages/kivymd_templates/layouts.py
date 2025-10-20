from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    ColorProperty,
    )
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.behaviors import ButtonBehavior

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/layouts.kv')

class ClickableBoxLayout(ButtonBehavior,MDBoxLayout):
    pass
class BottomField(MDAnchorLayout):
    height=NumericProperty(250)

class BottomFieldButton(BottomField):
    text=StringProperty()
    style=StringProperty('filled')
    press_button=ObjectProperty()
    

