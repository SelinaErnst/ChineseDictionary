from kivymd.uix.label import MDLabel
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.properties import (
    StringProperty, 
    NumericProperty,
    ObjectProperty,
    ListProperty,
    BooleanProperty,
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
    halign=StringProperty('left')
    # height=NumericProperty(100)
    
class MultiLineLabel(MDAnchorLayout):
    text=StringProperty()
    font_style=StringProperty('Label')
    bold=BooleanProperty(False)
    theme_font_size=StringProperty('Primary')
    font_size=NumericProperty()
    font_name=StringProperty('CH')
    text_color=ObjectProperty(None)
    role=StringProperty('medium')
    label_width=ObjectProperty(None)
    label_padding=ListProperty([20,0,20,0])
    label_bg_color=ObjectProperty(None)
    halign=StringProperty('left')
class TitleLabel(AnchoredLabel):
    pass

class TitleLabels(MDBoxLayout):
    left_text=StringProperty()
    right_text=StringProperty()
    font_style=StringProperty('Title')
    role=StringProperty('medium')
    
class TitleLabelsWithIcon(MDBoxLayout):
    left_text=StringProperty()
    right_text=StringProperty()
    font_style=StringProperty('Title')
    role=StringProperty('medium')
    icon=StringProperty('magnify')
    press_button=ObjectProperty()
    