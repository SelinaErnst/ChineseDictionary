from kivymd.uix.screen import MDScree
from kivymd.uix.snackbar import MDSnackbar
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior

from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonIcon
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextFieldTrailingIcon
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.card import MDCard


class ChLabel(MDLabel):
    pass

class MyScreen(MDScreen):
    pass

class ErrorMsg(MDSnackbar):
    msg=StringProperty()
    error=StringProperty("ERROR")
    
class DialogLines(MDBoxLayout):
    head=StringProperty()
    
class CustomListItem(RectangularRippleBehavior, ButtonBehavior, MDBoxLayout):
    text = StringProperty()

class MyTitleLabel(MDAnchorLayout):
    text=StringProperty()
    
class MyIconTextButton(MDButton):
    text=StringProperty()
    icon=StringProperty()
    padding=NumericProperty(30)
    _text_left_pad = 0
    _text_right_pad = 0
    _icon_left_pad = 0

class NavigationButton(MDButton):
    text=StringProperty()
    icon=StringProperty()
    # padding=NumericProperty(30)
    # _text_left_pad = 0
    # _text_right_pad = 0
    # _icon_left_pad = 0

class RectangularIconButtton(MDIconButton):
    radius=[0,]

    
class MyTextButton(MDButton):
    text=StringProperty()
    padding=NumericProperty(30)
    
class MyRigidTextButton(MDButton):
    text=StringProperty()

class EntryField(MDBoxLayout):
    text=StringProperty()
    hint=StringProperty()
    role=StringProperty("medium")