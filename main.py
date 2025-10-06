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
    

# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #

from screens import (
    SelectFile, 
    FileChooser, 
    ViewDict, 
    Settings,
    )

from packages.kivymd_templates.screens import MyScreen
from packages.kivymd_templates.labels import ChLabel
from packages.kivymd_templates.snackbars import ErrorMsg
from packages.kivymd_templates.dialogs import GrantAccess, grant_permissions_external_storage
from packages.kivymd_templates.buttons import FlexTextButton
from packages.kivymd_templates.layouts import BottomField
from packages.kivymd_templates.textfield import EntryField, EntryFieldWithIcon

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
from kivymd.uix.recycleview import MDRecycleView

# print([d for d in dir(MDScreen) if "on_" in d and "__" not in d])
print('CHD')

KV="""

    
<ShowCharacter>:

"""

def load_json(path):
    with open(path, "r") as f:
        settings = json.load(f)
    # print(path,settings)
    return settings

def dump_json(data,path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return True
    
my_examples=load_json('appdata/defaults/my_directories.json')
default_settings=load_json('appdata/defaults/default_settings.json')

class Interface(MDBoxLayout):
    pass
    
class WindowManager(ScreenManager):
    previous_screen_names=ListProperty()
    previous_transition_directions=ListProperty()

class Home(MyScreen):
    
        def __init__(self, *args,**kwargs):
            super().__init__(*args,**kwargs)
                    
class ShowCharacter(MyScreen):
    character=ObjectProperty()
    
    def get_property(self,prop):
        if self.character != None:
            existing = self.character.get_existing_categories()
            if prop in existing:
                return self.character.get_property(prop)
        
class ChD(MDApp):
    platform=platform
    metrics=Metrics
    window_size_myphone= (1080, 2114)
    has_access=False
    settings=None
    root_folder='./'
    import_dir_example=my_examples['import_directory'][platform]
    app_dir_example=my_examples['app_directory'][platform]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root_folder = Path(self.directory)
        self.root_folder = str(root_folder.resolve())+'/'
        resource_add_path(root_folder/"appdata"/"fonts")
        self.choose_settings()
        
        self.load_all_kv_files(str(root_folder/'screens'))
        Builder.load_string(KV)
    
    def build(self):
        default=False
        screens = [
            Home(name="home"),
            Settings(name='settings',settings=self.settings),
            SelectFile(name="selectfile", default=default),
            FileChooser(name="filechooser"),
            ViewDict(name="newdict", default=default),
        ]
        interface = Interface()
        self.wm = interface.wm
        for screen in screens:
            self.wm.add_widget(screen)
        if not os.path.isdir(self.get_setting('app_directory')):
            self.switch_screen('settings','left')
              
        return interface
    
    def on_start(self):
        if not self.settings['access_granted']:
            print(not self.settings['access_granted'])
            self._show_validation_dialog()
        else:
            self.has_access = True

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        
    def hook_keyboard(self,window,key,*largs):
        if key == 27:
            if self.dismiss_dialog():
                return True
            return self.previous_screen()
        return False
    
    def get_setting(self,kind,default=False,settings=None):
        if self.settings != None or settings != None:
            if default: settings = self.load_default_settings()
            else: settings = self.settings if settings == None else settings
            if kind in settings.keys():
                if isinstance(settings[kind], dict) \
                    and platform in settings[kind].keys():
                        return settings[kind][platform]
                else:
                    return settings[kind]
        else:
            return ""
    
    def load_settings(self):
        default_settings_file = self.root_folder+".config/default_settings.json"
        user_settings_file = self.get_setting('app_directory',default=True)+'.config/settings.json'
        settings_file = user_settings_file if os.path.isfile(user_settings_file) else default_settings_file
        self.settings = load_json(settings_file)
        return self.settings
    
    def save_default_settings(self, default_settings, update):
        if update: self.settings=default_settings
        if os.path.isdir(self.root_folder): os.makedirs(self.root_folder+".config/", exist_ok=True)
        dump_json(default_settings,self.root_folder+".config/default_settings.json")
        
    def load_default_settings(self):
        return load_json(self.root_folder+".config/default_settings.json")
        
    def choose_settings(self):
        try:
            self.settings=self.load_default_settings()
        except:
            device_default_settings={k:v if not isinstance(v,dict) else v[platform] for k,v in default_settings.items()}
            self.save_default_settings(default_settings=device_default_settings,update=True)
        try:
            self.load_settings()
        except Exception as err:
            print("load_settings", err)
        
        
        self.theme_cls.theme_style = self.get_setting('theme_style')
        self.theme_cls.primary_palette = self.get_setting('palette')
        self.dict_dir=self.get_setting('import_directory')
        LabelBase.register(name="CH", fn_regular=self.get_setting('chinese_font_file'))
        
    def switch_screen(self,screen_name,direction,remember=True):
        current_screen_name = self.wm.current
        current_direction = self.wm.transition.direction
        current_screen = self.wm.current_screen
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
                if current_screen_name.startswith('C'):
                    self.wm.remove_widget(current_screen)
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
            return True
        else:
            return False
        
    def dismiss_dialog(self):
        if hasattr(self.wm.current_screen,'dialog') \
            and self.wm.current_screen.dialog._is_open:
                self.wm.current_screen.dialog.dismiss()
                return True
        else: return False
        
    def get_theme_colors(self,style=None,palette=None):
        if style==None: style = self.theme_cls.theme_style
        if palette==None: palette = self.theme_cls.primary_palette
        palette_colors = load_json(self.directory+'/appdata/colors/palette_colors.json')
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

    def _show_validation_dialog(self):
        if platform == "android":
            done=False
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                support_text="To access files on the phone it is required to grant the app access to the storage."
                deny_text='No'
            else:
                done=True
                support_text="Storage access was already granted."
                deny_text='Return'
        elif platform == "linux":
            done=True
            support_text=f"For {platform} no further storage access needs to be granted."
            deny_text='Return'

        self.show_permission_popup = GrantAccess(
            support_text=support_text, deny_text=deny_text, done=done)
        self.show_permission_popup.open()
        
    def apply_palette(self,palette):
        self.theme_cls.primary_palette = palette
        
    def apply_styles(self,style:str=None):
        self.theme_cls.theme_style = style
        
if __name__=="__main__":
    ChD().run()

