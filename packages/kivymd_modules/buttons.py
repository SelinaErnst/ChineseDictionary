
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
from kivymd.uix.appbar.appbar import MDActionBottomAppBarButton
        
from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/buttons.kv')

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
    