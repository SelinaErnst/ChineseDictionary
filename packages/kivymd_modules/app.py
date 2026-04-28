import os
import json
from pathlib import Path
from kivy.utils import platform
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.metrics import Metrics, NUMERIC_FORMATS, dp, sp, inch, dpi2px
from kivy.resources import resource_add_path
from pathlib import Path
from .dialogs import GrantAccess, ChooseAppDirectory
# from .snackbars import AttentionMsg


APP_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent

def access_granted():
    if platform == 'android':
        from android import api_version
        from jnius import autoclass
        if api_version > 29:
            Environment = autoclass("android.os.Environment")
            return Environment.isExternalStorageManager()
        else: return False
    else: return True
    
class MyApp(MDApp):
    platform=platform
    metrics=Metrics
    settings=None
    root_folder='./'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        root_folder = Path(self.directory)
        self.root_folder = self.directory+'/'
        self.__appdata = self.root_folder+"appdata/"
        self.__config = self.root_folder+".config/"
        os.makedirs(self.__appdata,exist_ok=True)
        os.makedirs(self.__config,exist_ok=True)
        for folder in ['defaults','colors','fonts','templates']:
            os.makedirs(self.__appdata+folder,exist_ok=True)
    
        resource_add_path(self.__appdata+'fonts')
        
    def on_start(self):
        if not access_granted():
            self.__show_validation_dialog()
        else:
            # self.has_access = True
            if self.get_setting('app_directory')=="":
                self.__decide_on_app_directory()

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        
    def test(self,msg="TEST"):
        print(msg)
        
    def load_json(self,file,directory=APP_DIR):
        path=file if directory==None else Path(directory)/file
        with open(path, "r") as f:
            settings = json.load(f)
        return settings
    
    def dump_json(self,data,file, directory=APP_DIR):
        path=file if directory==None else Path(directory)/file
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    
    # = ============================================================== = #
    # =                            SETTINGS                            = #
    # = ============================================================== = #
        
    @property
    def default_settings_file(self):
        return self.__config + 'default_settings.json'

    @property
    def settings(self):
        return self.load_json(self.default_settings_file)

    def get_setting(self,kind,default=True,settings=None):
        if default: settings = self.get_default_settings()
        elif settings == None: settings = self.settings
        
        if kind in settings.keys():
            result = settings[kind]
        else:
            print(f'{kind} not found in settings')
            result = ""
        return result

    def get_default_settings(self):
        # get DEFAULT settings        
        if os.path.isfile(self.default_settings_file):
            # getting default settings from specified default_settings_file (under .config)
            default_settings = self.load_json(self.default_settings_file)
        else:
            #  get default settings from appdata folder defaults (only necessary first time)
            default_settings=self.load_appdata('default_settings.json','defaults')
            default_settings={k:v if not isinstance(v,dict) else v[platform] for k,v in default_settings.items()}
            self.save_default_settings(default_settings)
        return default_settings
    
    def save_default_settings(self, settings):
        self.dump_json(settings,self.default_settings_file)

    def load_appdata(self,file,typ):
        if typ in ['defaults','colors']:
            if typ == 'defaults': directory = self.__appdata+'defaults/'
            elif typ == 'colors': directory = self.__appdata+'colors/'
            if os.path.isfile(directory+file): 
                return self.load_json(file,directory=directory)
            else:
                print(f'file ({file}) was not found in directory ({directory})')
        else:
            print(f'load_appdata not defined for type {typ}')
            
    def __show_validation_dialog(self):
        done=False
        if self.platform == "android":
            from jnius import autoclass
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                support_text="To access files on the phone it is required to grant the app access to the storage."
                deny_text='No'
            else:
                done=True
                support_text="Storage access was already granted."
                deny_text='Return'
        elif self.platform == "linux":
            done=True
            support_text=f"For {self.platform} no further storage access needs to be granted."
            deny_text='Return'
        else:
            support_text=f'Access for {self.platform} might be necessary.'
            deny_text='No'
            
        self.show_permission_popup = GrantAccess(
            support_text=support_text, deny_text=deny_text, done=done)
        self.show_permission_popup.open()
        
    def __decide_on_app_directory(self):
        self.show_directory_popup = ChooseAppDirectory()
        self.show_directory_popup.open()
    
    # = ============================================================== = #
    # =                             DESIGN                             = #
    # = ============================================================== = #
    
    def apply_palette(self,palette='Lavender'):
        self.theme_cls.primary_palette = palette
    
    def apply_theme(self,style:str='Dark'):
        self.theme_cls.theme_style = style
    
    def switch_theme(self):
        if self.theme_cls.theme_style == 'Dark':
            self.apply_theme('Light')
        elif self.theme_cls.theme_style == 'Light':
            self.apply_theme('Dark')
            
    def get_palette_colors(self):
        palette_colors = self.load_appdata('palette_colors.json','colors')
        return palette_colors
    
    # = ============================================================== = #
    # =                         SCREEN MANAGER                         = #
    # = ============================================================== = #
    
    def hook_keyboard(self,window,key,*largs):
        if key == 27:
            if self.dismiss_all():
                return True
            else:
                return self.previous_screen()
        return False    
    
    def add_window_manager(self,wm):
        self.wm = wm    
        
    def dismiss_dialog(self):
        if hasattr(self.wm.current_screen,'dialog') \
            and self.wm.current_screen.dialog._is_open:
                self.wm.current_screen.dialog.dismiss()
                return True
        else: return False
        
    def dismiss_file_manager(self):
        if hasattr(self.wm.current_screen,'file_manager') \
            and self.wm.current_screen.file_manager._window_manager_open:
                self.wm.current_screen.file_manager.close()
    
    def dismiss_widget(self):
        if hasattr(self.wm.current_screen,'layout'):
            del self.wm.current_screen.layout
            widget = self.wm.current_screen.ids.pop('layout')
            for child in self.wm.current_screen.children:
                if child==widget: self.wm.current_screen.remove_widget(child)
            return True
        else: return False
    
    def dismiss_all(self):
        if self.dismiss_dialog():
            return True
        elif self.file_manager_back():
            return True
        elif self.dismiss_widget():
            return True
        else:
            return False

    def open_widget(self,widget):
        self.dismiss_all()
        self.wm.current_screen.layout = widget
        self.wm.current_screen.add_widget(widget)
        self.wm.current_screen.ids['layout'] = widget

    def file_manager_back(self):
        if hasattr(self.wm.current_screen,'file_manager') \
            and self.wm.current_screen.file_manager._window_manager_open:
                self.wm.current_screen.file_manager.back()
                return True
        else: return False

    def hide_widget(self,widget,do_hide=True):
        if hasattr(widget, 'saved_attrs'):
            if not do_hide:
                widget.height, widget.size_hint_y, widget.width, widget.size_hint_x, widget.opacity, widget.disabled = widget.saved_attrs
                del widget.saved_attrs
        elif do_hide:
            widget.saved_attrs = widget.height, widget.size_hint_y, widget.width, widget.size_hint_x, widget.opacity, widget.disabled
            widget.height, widget.size_hint_y, widget.width, widget.size_hint_x, widget.opacity, widget.disabled = 0, None, 0, None, 0, True
        
    def switch_screen(self,screen_name,direction,remember=True,home='home'):
        previous_screen_name = self.wm.current
        previous_direction = self.wm.transition.direction
        previous_screen = self.wm.current_screen
        if screen_name != previous_screen_name \
            and screen_name in self.wm.screen_names:
                if self.wm.previous_screen_names != []\
                    and self.wm.previous_screen_names[-1] == screen_name:
                    self.wm.previous_screen_names = self.wm.previous_screen_names[:-1]
                    self.wm.previous_transition_directions = self.wm.previous_transition_directions[:-1]
                if remember: 
                    self.wm.previous_screen_names.append(previous_screen_name)
                    self.wm.previous_transition_directions.append(direction)
                if screen_name==home: 
                    self.wm.previous_screen_names=[]
                    self.wm.previous_transition_directions=[]
                self.wm.current = screen_name
                self.wm.transition.direction = direction
                switched = {'previous': 
                    {'screen_name':previous_screen_name,
                     'screen':previous_screen}, 
                            'current':
                    {'screen_name':screen_name,
                     'screen':self.wm.current_screen}}
                return switched
            
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
        
    # = ============================================================== = #
    # =                             METRICS                            = #
    # = ============================================================== = #
    
    @property
    def window_size(self):
        return Window.size
    
    @property
    def __diag_inch(self):
        xpix = self.window_size[0]
        ypix = self.window_size[1]
        xinch = xpix/dpi2px(1,'in')
        yinch = ypix/dpi2px(1,'in')
        diag_inch = (xinch*xinch+yinch*yinch)**.5
        return diag_inch
    
    def get_metrics(self):
        window_metrics = f"\nwindow size = {self.window_size}\ndiagonal = {self.__diag_inch}"
        metrics = f"\ndensity = {self.metrics.density} \ndpi = {self.metrics.dpi} \nfontscale = {self.metrics.fontscale}"
        more_metrics = f"\ndp(1) = {dp(1)} \nsp(1) = {sp(1)} \ninch(1) = {inch(1)}"
        return f"{self.platform}: {window_metrics} {metrics}"