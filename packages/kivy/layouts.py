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

from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
import os
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'layouts.kv'))

class MyScrollView(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Only bind keyboard listeners if running on Android
        if platform == 'android':
            Window.bind(on_keyboard_height=self.on_keyboard_height)
    def on_keyboard_height(self, window, height):
        print('\n'*5,window, height)
class ClickableBoxLayout(ButtonBehavior,MDBoxLayout):
    pass
class BottomField(MDAnchorLayout):
    height=NumericProperty(250)

class BottomFieldButton(BottomField):
    text=StringProperty()
    # style=StringProperty('filled')
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

from kivy.clock import Clock

class ShowFileContent(MDBoxLayout):
    text=StringProperty()
    file=StringProperty()
    # allow_new=BooleanProperty()
    
    def __init__(self,allow_new=False,create_tmp=False, *args, **kwargs):
        self.allow_new = allow_new
        self.create_tmp = create_tmp
        super().__init__(*args, **kwargs)
    
    def read_file(self,file:str|None=None,allow_new:bool|None=None,create_tmp:bool|None=None):
        self.allow_new = allow_new if allow_new != None else self.allow_new
        self.create_tmp = create_tmp if create_tmp != None else self.create_tmp
        
        text = ""
        if file!=None: self.file=file
        if (self.file==None or not os.path.isfile(self.file)) and not self.allow_new: return None
        elif self.file!=None and os.path.isfile(self.file):
            with open(self.file) as f:
                lines = f.readlines()
                text=''.join(lines)
        
        self.text = text
        Clock.schedule_once(lambda dt: self.reset_scroll())
        self.open()
        
    def reset_scroll(self):
        self.input.cursor = (0, 0)
        
    def change_file(self,file:str|None=None):
        from main import ChD
        app:ChD = ChD.get_running_app()
        
        if file!=None: self.file=file
        
        directory = os.path.dirname(str(self.file))
        
        if not os.path.isdir(directory): self.allow_new=False
        
        if self.create_tmp:
            # always create new tmp / overwrite
            self.allow_new = True
            # former removal is reversed
            if str(self.file) in app.tmp_files_rm: app.tmp_files_rm.pop(str(file))
            elif Path(self.file) in app.tmp_files_rm.values():
                pop = [f for f,rm in app.tmp_files_rm.items() if str(rm) == str(self.file)][0]
                app.tmp_files_rm.pop(str(pop))
            
            self.file = str(app.tmp_file(self.file))
        
        if os.path.isfile(self.file) or self.allow_new:
            with open(self.file, "w") as f:
                f.write(self.input.text.rstrip('\n'))
        
        app.dismiss_dialog()
        self.file=""
    
    def open(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        app.open_dialog(self)
        