from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog.dialog import MDDialog
from kivymd.uix.button import MDButton
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.dialog.dialog import MDDialog


class ChLabel(MDLabel):
    pass

class MyScreen(MDScreen):
    pass

class ErrorMsg(MDSnackbar):
    msg=StringProperty()
    error=StringProperty("ERROR")

class AttentionMsg(MDSnackbar):
    msg=StringProperty()
    attention=StringProperty("ATTENTION")
    
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

class RectangularIconButtton(MDIconButton):
    radius=[0,]

    
class MyTextButton(MDButton):
    text=StringProperty()
    padding=NumericProperty(30)
    
class MyRigidTextButton(MDButton):
    text=StringProperty()

class MyFlexTextButton(MyTextButton):
    pass
    
class EntryField(MDTextField):
    hint=StringProperty()
    is_correct=ObjectProperty()
    
    def _get_has_error(self) -> bool:
        has_error = super()._get_has_error()
        try:
            has_error = (has_error or not self.is_correct())
        except:
            pass
        return has_error
    
class EntryFieldWithIcon(MDBoxLayout):
    text=StringProperty()
    hint=StringProperty()
    role=StringProperty("medium")
    icon=StringProperty()
    press_button=ObjectProperty()
    
    def is_correct(self):
        return True
