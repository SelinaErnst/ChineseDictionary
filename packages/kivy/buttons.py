
from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    ColorProperty,
    )
from kivymd.uix.button import MDButton
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.appbar.appbar import MDActionBottomAppBarButton
        
from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/buttons.kv')

# = ============================================================== = #
# =                             TOGGLE                             = #
# = ============================================================== = #

class Toggle(MDStackLayout):
    include = ListProperty()
    exclude = ListProperty()
    
    def switch(self,child):
        for c in self.children:
            if c == child:
                child.toggle_on()
            else:
                c.toggle_off()
                
class ToggleButton(MDButton):
    active_filter=StringProperty('ignore')
    padding=NumericProperty(20)
    
    def toggle_on(self):
        self.active_filter = 'include'
        self.style = 'filled'
        self.parent.include.append(self.text)
        
    def toggle_off(self):
        self.active_filter = 'ignore'
        self.style = 'tonal'
        if self.text in self.parent.include: self.parent.include.remove(self.text)
        
    def toggle_two(self,only_one=True):
        from main import ChD
        app = ChD.get_running_app()
        if only_one:
            self.parent.switch(self)
        else:
            if self.active_filter == 'ignore':
                self.toggle_on()
            elif self.active_filter == 'include':
                self.toggle_off()
        app.wm.current_screen.set_list_items()

    def toggle_three(self):

        if self.active_filter == 'ignore':
            self.active_filter = 'include'
            self.style = 'filled'
            self.parent.include.append(self.text)
        elif self.active_filter == 'include':
            self.active_filter = 'exclude'
            self.style = 'tonal'
            self.parent.include.remove(self.text)
            self.parent.exclude.append(self.text)
        elif self.active_filter == 'exclude':
            self.active_filter = 'ignore'
            self.style = 'tonal'
            self.parent.exclude.remove(self.text)
            
        from main import ChD
        app = ChD.get_running_app()
        app.wm.current_screen.set_list_items()

        if self.parent.include != [] or self.parent.exclude != []:
            app.wm.current_screen.filter_button.style = 'filled'
        elif self.parent.include == [] and self.parent.exclude == []:
            app.wm.current_screen.filter_button.style = 'elevated'

class IconTextToggleButton(ToggleButton):
    _text_left_pad = 0
    _text_right_pad = 0
    _icon_left_pad = 0
    
class TextToggleButton(ToggleButton):
    pass

# = ============================================================== = #
# =                          ICON AND TEXT                         = #
# = ============================================================== = #

class MyIconTextButton(MDButton):
    text=StringProperty()
    icon=StringProperty()
    padding=NumericProperty(30)
    _text_left_pad = 0
    _text_right_pad = 0
    _icon_left_pad = 0
    
class RigidIconTextButton(MyIconTextButton):
    # width determines size of Button
    # used in: MakeDecision
    pass

class MultiLineIconTextButton(MyIconTextButton):
    # when text has \n
    pass

# used with Interface
class NavigationButton(MDButton):
    text=StringProperty()
    icon=StringProperty()

# = ============================================================== = #
# =                            ONLY TEXT                           = #
# = ============================================================== = #

class MyTextButton(MDButton):
    text=StringProperty()
    padding=ListProperty([30,30,30,30])
    font_style=StringProperty('Label')
    role=StringProperty('large')
    
class RigidTextButton(MyTextButton):
    pass

class FlexTextButton(MyTextButton):
    pass


# = ============================================================== = #
# =                              ICON                              = #
# = ============================================================== = #

class MyIconButton(MDButton):
    size=ListProperty([100,100])
    icon=StringProperty()
    