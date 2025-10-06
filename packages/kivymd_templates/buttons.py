
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

# = ============================================================== = #
# =                            ONLY TEXT                           = #
# = ============================================================== = #

class MyTextButton(MDButton):
    text=StringProperty()
    padding=NumericProperty(30)
    
class RigidTextButton(MyTextButton):
    pass

class FlexTextButton(MyTextButton):
    pass





class NavigationButton(MDButton):
    text=StringProperty()
    icon=StringProperty()

# class RectangularIconButtton(MDIconButton):
#     radius=[0,]

    
