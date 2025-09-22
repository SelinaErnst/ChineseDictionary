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

from screens.select_dict_file import SelectFile, FileChooser, MyAccessDialog
from screens.templates import MyScreen

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
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.textfield import MDTextFieldTrailingIcon
from kivymd.uix.behaviors import RectangularRippleBehavior

# print([d for d in dir(MDLabel) if "" in d and "__" not in d])

KV="""
<ChLabel@MDLabel>
    theme_font_name: "Custom"
    font_name:"CH"


"""

class ErrorMsg(MDSnackbar):
    msg=StringProperty()
    error=StringProperty("ERROR")

class MyTitleLabel(MDAnchorLayout):
    text=StringProperty()
    
class MyIconTextButton(MDButton):
    text=StringProperty()
    icon=StringProperty()
    padding=NumericProperty(30)
    _text_left_pad = 0
    _text_right_pad = 0
    _icon_left_pad = 0
    
class MyTextButton(MDButton):
    text=StringProperty()
    padding=NumericProperty(30)
    
class MyRigidTextButton(MDButton):
    text=StringProperty()

class EntryField(MDBoxLayout):
    text=StringProperty()
    hint=StringProperty()
    role=StringProperty("medium")
    
class WindowManager(ScreenManager):
    pass


class Home(MyScreen):
    pass

class ReloadButton(MDIconButton):
    pass

class DialogLines(MDBoxLayout):
    head=StringProperty()

class CustomListItem(RectangularRippleBehavior, ButtonBehavior, MDBoxLayout):
    text = StringProperty()
  
class NewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty()

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
        self.wm = WindowManager()
        screens = [
            # Home(name="home"),
            SelectFile(name="selectfile"),
            NewDict(name="newdict"),
            FileChooser(name="filechooser")
        ]
        for screen in screens:
            self.wm.add_widget(screen)
        return self.wm
    
    def switch_screen(self,screen_name,direction="right"):
        if screen_name != self.wm.current \
            and screen_name in self.wm.screen_names:
                self.wm.current = screen_name
                self.wm.transition.direction = direction
                return self.wm.current_screen
    
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


