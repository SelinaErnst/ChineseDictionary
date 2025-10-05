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

with open("appdata/palette_colors.json", "r") as f:
    import json
    palette_colors = json.load(f)
    
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
    press_button=ObjectProperty(True)
    is_correct=ObjectProperty()
    # def is_correct(self):
        # return True

        
class ShowOptions(MDDialog):
    title = StringProperty()
    support_text = StringProperty()
    list_height = NumericProperty()
    radius=[20,20,20,20]
    
    def __init__(self, title, options, itemclass, list_height, icons, *args, **kwargs):
        self.itemclass = itemclass
        self.list_height = list_height
        super().__init__(*args, **kwargs)
        self.title = title
        self.options = options
        self.icons = icons
        if options != []:
            self.set_list_items()
        
    def create_dataitem(self,text,**kwargs):
        dataitem={
            'text': text,
            'style': 'text',
            'theme_bg_color': 'Custom',
            'md_bg_color': self.theme_cls.surfaceBrightColor,
            'radius':20,
            'callback':lambda x:x}
        dataitem.update(kwargs)
        if self.title == "Palette":
            dataitem.update(self.add_palette_colors(text))
        
        return dataitem 
    
    def add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)
        
    def set_list_items(self):
        self.rv_scroll.data = []
        if self.icons == []:
            for option in self.options:
                dataitem=self.create_dataitem(option)
                self.add_list_item(dataitem)
        elif len(self.icons) == len(self.options):
            for option,icon in zip(self.options,self.icons):
                dataitem=self.create_dataitem(text=option,icon=icon)
                self.add_list_item(dataitem)
                
    def add_palette_colors(self,palette):
        d = {
            # 'md_bg_color':self.theme_cls.surfaceContainerColor,
            "color_onea":"primaryColor",
            "color_oneb":"primaryContainerColor",
            "color_onec":"onPrimaryColor",
            "color_oned":"onPrimaryContainerColor",
            "color_onee":"primaryFixedColor",
            "color_onef":"onPrimaryFixedColor",
            "color_oneg":"inversePrimaryColor",
            
            "color_twoa":"secondaryColor",
            "color_twob":"secondaryContainerColor",
            "color_twoc":"onSecondaryColor",
            "color_twod":"onSecondaryContainerColor",
            "color_twoe":"secondaryFixedColor",
            "color_twof":"onSecondaryFixedColor",
            
            "color_trea":"tertiaryColor",
            "color_treb":"tertiaryContainerColor",
            "color_trec":"onTertiaryColor",
            "color_tred":"onTertiaryContainerColor",
            "color_tree":"tertiaryFixedColor",
            "color_tref":"onTertiaryFixedColor",
        }
        updatedict = {color:self.get_color(palette,colorname) for color,colorname in d.items()}
        return updatedict
        
    def get_color(self,name,color_name):
        return palette_colors[self.theme_cls.theme_style][name.capitalize()][color_name]
    