import json
from pathlib import Path
import os
from plyer import filechooser
from kivy.utils import platform


from packages.pleco import dictionary


# = ––––––––––––– do not put this below kivy packages –––––––––––– = #
if platform in ["linux","win"]:
    # my phone: KIVY_METRICS_FONTSCALE: 1.15, KIVY_METRICS_DENSITY: 2.8125, KIVY_DPI: 450 -> dp(1): 2.8125. sp(1): ~ 3.2
    # my linux: KIVY_METRICS_FONTSCALE: 1, KIVY_METRICS_DENSITY: 1, KIVY_DPI: 96 -> dp(1): 1, sp(1): 1
    os.environ['KIVY_METRICS_DENSITY'] = '2.8125'
    os.environ['KIVY_DPI'] = '450'
    os.environ['KIVY_METRICS_FONTSCALE'] = '1.15'
    # my phone: Window.size = (1080, 2114) 
# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #
from kivy.core.window import Window
if platform in ["linux","win"]:
    Window.size = (1300, 1000)
    Window.size = (1080, 2114) 
if platform == "android":
    from jnius import cast
    from jnius import autoclass
    from android import mActivity, api_version
    from kivymd.toast import toast
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.INTERNET,
    ])

# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #

from screens import SelectFile, FileChooser, MyAccessDialog
from templates import MyScreen, RectangularIconButtton

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen, Screen
from kivy.lang import Builder
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivy.metrics import Metrics, NUMERIC_FORMATS, dp, sp
from kivy.uix.behaviors import ButtonBehavior

from kivy.uix.button import Button
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dialog.dialog import MDDialog
from kivymd.uix.button import MDButton, MDButtonIcon
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.textfield import MDTextFieldTrailingIcon
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivymd.uix.card import MDCard
from kivymd.uix.navigationdrawer import MDNavigationDrawerItem

# print([d for d in dir(MDButton) if "" in d and "__" not in d])

KV="""
<ChLabel>:
    theme_font_name: "Custom"
    font_name:"CH"

"""


class Interface(MDBoxLayout):
    pass
    
class WindowManager(ScreenManager):
    previous_screen_names=ListProperty()


class Home(MyScreen):
    pass
  
class ViewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty()
    dictionary=ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if platform=="linux":
            dict_dir="/media/selina/SHARE/MyProjects/Pleco/"
            self.dict_file=dict_dir+"plecoformat.txt"
            self.dict_name="test"
            self.read_dict_file()
                
    def read_dict_file(self):
        self.empty_dict()
        can_read = self.dictionary.read(self.dict_file,add=False)
        if can_read:
            self.set_list_items(namelist=self.dictionary.get_simple_list())
        return can_read
    
    def empty_dict(self):
        # self.dictionary=None
        self.dictionary=dictionary(self.dict_name)

    def create_dataitem(self,character):
        char_simp, char_trad, char_pron = character.uniq
        dataitem={
            'character': character,
            'char_simp': char_simp,
            'char_trad': char_trad,
            'char_pron': char_pron,
            'is_radical': character.is_radical(),
            'is_measure_word': character.is_measure_word(),
            'is_grammatical': character.is_grammatical(),
            'has_translation': character.has_translation(),
            'callback':lambda x:x}
        return dataitem 
    
    def add_list_item(self,dataitem,text="",search=False):
        if search:
            pass
            # if text.lower() in name.lower() or text=="":
                # self.rv_scroll.data.append(dataitem)
        else: self.rv_scroll.data.append(dataitem)
    
    def set_list_items(self,text="",namelist=None, search=False):
        self.rv_scroll.data = []
        if namelist != None and isinstance(namelist,list): 
            self.namelist=namelist
        # for name in self.namelist:
        for character in self.dictionary:
            dataitem=self.create_dataitem(character)
            self.add_list_item(dataitem,text=text,search=search)

class DictionaryEntry(MDCard):
    text = StringProperty()
    char_simp = StringProperty()
    char_trad = StringProperty()
    char_pron = StringProperty()
    character = ObjectProperty()
    is_radical = BooleanProperty()
    is_measure_word = BooleanProperty()
    is_grammatical = BooleanProperty()
    has_translation = BooleanProperty()
    
    def get_categories(self):
        print(self.character.info(complete=False))
        
class EntryType(RectangularIconButtton):
    the_size=NumericProperty()
    
    def choose_icon(self, is_type,icons=['alpha-a-box-outline','alpha-a-box']):
        return icons[int(is_type)]
    
    def get_size(self,is_type,sizes=[0,40]):
        # return sizes[int(is_type)]
        return sizes[1]
        
class ChD(MDApp):
    platform=platform
    metrics=Metrics
    # window_size=Window.size
    window_size_myphone= (1080, 2114)
    def __init__(self, **kwargs):
        # Window.maximize()
        # self.s=f"{self.window_size},\n{self.platform}: {self.metrics.fontscale}, {self.metrics.density}, \n{self.metrics.dpi}, {dp(1)}, {sp(1)}"
        super().__init__(**kwargs)
        root_folder = Path(self.directory)
        # print(self.directory,os.listdir(self.directory))
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        resource_add_path(root_folder/"kv_files")
        resource_add_path(root_folder/"fonts")
        self.load_all_kv_files(str(root_folder/'kv_files'))
        Builder.load_string(KV)
        self.theme_colors = self.get_theme_colors() 
        # LabelBase.register(name="CH", fn_regular='Source Han Sans CN Light.otf')
        LabelBase.register(name="CH", fn_regular='DroidSansFallback.ttf')

    def build(self):
        screens = [
            Home(name="home"),
            SelectFile(name="selectfile"),
            FileChooser(name="filechooser"),
            ViewDict(name="newdict"),
        ]
        interface = Interface()
        self.wm = interface.wm
        # print(dir(self.wm))
        for screen in screens:
            self.wm.add_widget(screen)
        return interface
    
    def switch_screen(self,screen_name,direction="right",remember=True):
        if screen_name != self.wm.current \
            and screen_name in self.wm.screen_names:
                if remember: self.wm.previous_screen_names.append(self.wm.current)
                if screen_name=='home': self.wm.previous_screen_names=[]
                self.wm.current = screen_name
                self.wm.transition.direction = direction
                return self.wm.current_screen
    
    def previous_screen(self,direction='left'):
        if self.wm.previous_screen_names != []:
            previous_screen_name=self.wm.previous_screen_names[-1]
            self.wm.previous_screen_names=self.wm.previous_screen_names[:-1]
            self.switch_screen(previous_screen_name,direction,remember=False)
            print(self.wm.previous_screen_names)
            
    def get_theme_colors(self,style=None,palette=None):
        if style==None: style = self.theme_cls.theme_style
        if palette==None: palette = self.theme_cls.primary_palette
        
        with open(self.directory+'/colors/palette_colors.json') as f_in:
            palette_colors=json.load(f_in)
        
        return palette_colors[style][palette]
    
    def get_metrics(self):
        return f"{self.platform}: window size = {Window.size}\ndensity = {self.metrics.density} \ndpi = {self.metrics.dpi} \nfontscale = {self.metrics.fontscale} \ndp(1) = {dp(1)},  sp(1) = {sp(1)}"

    def test(self,msg="TEST"):
        print(msg)

    def permissions_external_storage(self, *args):  
        if platform == "android":
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Environment = autoclass("android.os.Environment")
            Intent = autoclass("android.content.Intent")
            Settings = autoclass("android.provider.Settings")
            Uri = autoclass("android.net.Uri")
            if api_version > 29: 
                if Environment.isExternalStorageManager():
                    # If you don't have access, launch a new activity to show the user the system's dialog
                    # to allow access to the external storage
                    pass
                else:
                    self.show_permission_popup.error_msg = f"Environment not isExternalStorageManager"
                    try:
                        activity = mActivity.getApplicationContext()
                        uri = Uri.parse("package:" + activity.getPackageName())
                        intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                        currentActivity = cast(
                        "android.app.Activity", PythonActivity.mActivity
                        )
                        currentActivity.startActivityForResult(intent, 101)
                    except:
                        intent = Intent()
                        intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                        currentActivity = cast(
                        "android.app.Activity", PythonActivity.mActivity
                        )
                        currentActivity.startActivityForResult(intent, 101)
                    self.show_permission_popup.dismiss()
        else:
            self.show_permission_popup.error_msg = "permissions_external_storage"
            
    def _show_validation_dialog(self, *args):   
           
        if platform == "android":
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                self.show_permission_popup = MyAccessDialog(error_msg="To access files on the phone it is required to grant the app access to the storage.")
            else:
                self.show_permission_popup = MyAccessDialog(error_msg="Storage access was already granted.")
        elif platform == "linux":
            self.show_permission_popup = MyAccessDialog(error_msg="For linux no further storage access needs to be granted.")
        self.show_permission_popup.open()
        
if __name__=="__main__":
    ChD().run()


