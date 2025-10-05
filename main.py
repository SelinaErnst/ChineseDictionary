import json
from pathlib import Path
import os
from plyer import filechooser
from packages.pleco import dictionary

from kivy.utils import platform

# = ––––––––––––– do not put this below kivy packages –––––––––––– = #
if platform in ["linux","win"]:
    # my linux: KIVY_METRICS_FONTSCALE: 1, KIVY_METRICS_DENSITY: 1, KIVY_DPI: 96 -> dp(1): 1, sp(1): 1

    # os.environ['KIVY_METRICS_DENSITY'] = '2.625'
    # os.environ['KIVY_DPI'] = '420'
    # os.environ['KIVY_METRICS_FONTSCALE'] = '1.0'
    
    os.environ['KIVY_METRICS_DENSITY'] = '2.8125'
    os.environ['KIVY_DPI'] = '450'
    os.environ['KIVY_METRICS_FONTSCALE'] = '1.15'

os.environ['KIVY_METRICS_FONTSCALE'] = '1.4'

# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #
from kivy.core.window import Window
if platform in ["linux","win"]:
    # Window.size = (1700, 1500) 
    # Window.maximize()
    # Window.size = (2560, 1411) # Tab S6
    # Window.size = (1411, 2560) # Tab S6
    Window.size = (1080, 2114) # Galaxy S24
if platform == "android":
    from jnius import cast
    from jnius import autoclass
    from android import mActivity, api_version
    from kivymd.toast import toast
    
from kivy.metrics import Metrics, NUMERIC_FORMATS, dp, sp, inch, dpi2px
xpix = Window.size[0]
ypix = Window.size[1]
xinch = xpix/dpi2px(1,'in')
yinch = ypix/dpi2px(1,'in')
diag_inch = (xinch*xinch+yinch*yinch)**.5
    
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.INTERNET,
    ])
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    ActivityInfo = autoclass("android.content.pm.ActivityInfo")
    activity = PythonActivity.mActivity
    activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_USER)
# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #

from screens import (
    SelectFile, 
    FileChooser, 
    MyAccessDialog, 
    ViewDict, 
    Settings,
    )
from templates import MyScreen, EntryFieldWithIcon, MyFlexTextButton, ChLabel

from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.screen import MDScreen, Screen
from kivy.lang import Builder
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase
from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    ColorProperty,
    BooleanProperty
    )
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
from kivymd.uix.textfield import MDTextFieldTrailingIcon, MDTextField
from kivymd.uix.behaviors import RectangularRippleBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.navigationdrawer import MDNavigationDrawerItem, MDNavigationDrawer
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.textfield import MDTextField

# print([d for d in dir(ChLabel) if "copy" in d and "__" not in d])

KV="""
<ChLabel>:
    theme_font_name: "Custom"
    font_name:"CH"
"""

def load_json(path):
    with open(path, "r") as f:
        settings = json.load(f)
    return settings

def dump_json(data,path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    
class Interface(MDBoxLayout):
    pass
    
class WindowManager(ScreenManager):
    previous_screen_names=ListProperty()
    previous_transition_directions=ListProperty()


class Home(MyScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
class ChD(MDApp):
    platform=platform
    metrics=Metrics
    window_size_myphone= (1080, 2114)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root_folder = Path(self.directory)

        resource_add_path(root_folder/"kv_files")
        resource_add_path(root_folder/"fonts")
        resource_add_path(root_folder/"appdata")
        self.load_all_kv_files(str(root_folder/'kv_files'))
        Builder.load_string(KV)
        self.choose_settings()
        self.theme_colors = self.get_theme_colors() 
            
    def build(self):
        default=False
        # default=True
        screens = [
            Home(name="home"),
            SelectFile(name="selectfile", default=default),
            FileChooser(name="filechooser"),
            ViewDict(name="newdict", default=default),
            Settings(name='settings',settings=self.settings)
        ]
        interface = Interface()
        self.wm = interface.wm
        for screen in screens:
            self.wm.add_widget(screen)
        if not os.path.isdir(self.get_setting('app_directory')):
            self.switch_screen('settings','left')
        return interface
    
    def get_setting(self,kind,default=False,settings=None):
        if default: settings = self.load_default_settings()
        else: settings = self.settings if settings == None else settings
        if kind in settings.keys():
            if isinstance(settings[kind], dict) \
                and platform in settings[kind].keys():
                    return settings[kind][platform]
            else:
                return settings[kind]
    
    def load_settings(self):
        default_settings_file = "appdata/default_settings.json" 
        user_settings_file = self.get_setting('app_directory',default=True)+'.config/settings.json'
        settings_file = user_settings_file if os.path.isfile(user_settings_file) else default_settings_file
        self.settings = load_json(settings_file)
    
    def load_default_settings(self):
        return load_json("appdata/default_settings.json")
        
    def choose_settings(self):
        if not hasattr(self, 'settings'): self.load_settings()
        self.theme_cls.theme_style = self.get_setting('theme_style')
        self.theme_cls.primary_palette = self.get_setting('palette')
        self.dict_dir=self.get_setting('import_directory')
        LabelBase.register(name="CH", fn_regular=self.get_setting('chinese_font_file'))
        
    def switch_screen(self,screen_name,direction,remember=True):
        current_screen_name = self.wm.current
        current_direction = self.wm.transition.direction
        if screen_name != current_screen_name \
            and screen_name in self.wm.screen_names:
                if self.wm.previous_screen_names != []\
                    and self.wm.previous_screen_names[-1] == screen_name:
                    self.wm.previous_screen_names = self.wm.previous_screen_names[:-1]
                    self.wm.previous_transition_directions = self.wm.previous_transition_directions[:-1]
                if remember: 
                    self.wm.previous_screen_names.append(current_screen_name)
                    self.wm.previous_transition_directions.append(direction)
                if screen_name=='home': 
                    self.wm.previous_screen_names=[]
                    self.wm.previous_transition_directions=[]
                self.wm.current = screen_name
                self.wm.transition.direction = direction
                return self.wm.current_screen
    
    def previous_screen(self):
        if self.wm.previous_screen_names != []:
            previous_screen_name=self.wm.previous_screen_names[-1]
            previous_direction=self.wm.previous_transition_directions[-1]
            self.wm.previous_screen_names=self.wm.previous_screen_names[:-1]
            self.wm.previous_transition_directions=self.wm.previous_transition_directions[:-1]
            if previous_direction in ['right','left']:
                direction = 'right' if previous_direction == 'left' else 'left'
            elif previous_direction in ['up','down']:
                direction = 'up' if previous_direction == 'down' else 'up'
            self.switch_screen(previous_screen_name,direction,remember=False)
            
    def get_theme_colors(self,style=None,palette=None):
        if style==None: style = self.theme_cls.theme_style
        if palette==None: palette = self.theme_cls.primary_palette
        palette_colors = load_json(self.directory+'/colors/palette_colors.json')
        return palette_colors[style][palette]
    
    def get_metrics(self):
        window_metrics = f"\nwindow size = {Window.size}\ndiagonal = {diag_inch}"
        metrics = f"\ndensity = {self.metrics.density} \ndpi = {self.metrics.dpi} \nfontscale = {self.metrics.fontscale}"
        more_metrics = f"\ndp(1) = {dp(1)} \nsp(1) = {sp(1)} \ninch(1) = {inch(1)}"
        return f"{self.platform}: {window_metrics} {metrics}"

    def get_window_size(self):
        return Window.size
    
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
        
    def apply_palette(self,palette):
        self.theme_cls.primary_palette = palette
        
    def apply_styles(self,style:str=None):
        self.theme_cls.theme_style = style
        
if __name__=="__main__":
    ChD().run()

