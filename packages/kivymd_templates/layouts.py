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
from kivy.uix.behaviors import ButtonBehavior

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/layouts.kv')

class BottomField(MDAnchorLayout):
    height=NumericProperty(250)

class BottomFieldButton(BottomField):
    text=StringProperty()
    style=StringProperty('filled')
    press_button=ObjectProperty()
    

