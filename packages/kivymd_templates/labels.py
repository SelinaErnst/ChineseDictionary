from kivymd.uix.label import MDLabel
from kivymd.uix.anchorlayout import MDAnchorLayout

from kivy.properties import (
    StringProperty, 
    )

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/labels.kv')

class ChLabel(MDLabel):
    pass

class AnchoredLabel(MDAnchorLayout):
    text=StringProperty()
    font_style=StringProperty('Label')
    role=StringProperty('medium')
    # height=NumericProperty(100)
    anchor_x=StringProperty('center')
    
class MultiLineLabel(MDAnchorLayout):
    text=StringProperty()
    font_style=StringProperty('Label')
    role=StringProperty('medium')
    anchor_x=StringProperty('left')

class TitleLabel(AnchoredLabel):
    pass