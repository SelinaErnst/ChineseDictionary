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
from kivymd.uix.floatlayout import MDFloatLayout

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
    
class BlockingAnchorLayout(MDAnchorLayout):

    def on_touch_down(self, touch):
        # 1. Let the children (Label, Buttons on top) try to use the touch first
        if super().on_touch_down(touch):
            return True
        
        # 2. If no child handled it, check if the touch is within the layout
        if self.collide_point(*touch.pos):
            # 3. Eat the touch so it doesn't reach the widgets UNDER the layout
            return True
            
        return False
    
class BlockingFloatLayout(MDFloatLayout):
    
    def on_touch_down(self, touch):
        # 1. Let the children (Label, Buttons on top) try to use the touch first
        if super().on_touch_down(touch):
            return True
        
        # 2. If no child handled it, check if the touch is within the layout
        if self.collide_point(*touch.pos):
            # 3. Eat the touch so it doesn't reach the widgets UNDER the layout
            return True
            
        return False