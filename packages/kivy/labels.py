from kivymd.uix.label import MDLabel
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.behaviors import ButtonBehavior

from kivy.properties import (
    StringProperty, 
    NumericProperty,
    ObjectProperty,
    ListProperty,
    BooleanProperty,
    )

from kivy.lang import Builder
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'labels.kv'))
class ChLabel(MDLabel):
    pass
class ClickableLabel(ButtonBehavior,MDLabel):
    pass

# class AnchoredLabel(MDAnchorLayout):
#     text=StringProperty()
#     font_style=StringProperty('Label')
#     role=StringProperty('medium')
#     halign=StringProperty('left')
#     # height=NumericProperty(100)
    
class MultiLineLabel(MDAnchorLayout):
    press_button=ObjectProperty()

class TitleLabels(MDBoxLayout):
    left_text=StringProperty()
    right_text=StringProperty()
    font_style=StringProperty('Title')
    role=StringProperty('medium')
    