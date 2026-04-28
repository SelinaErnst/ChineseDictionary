import json
from pathlib import Path
import os
import traceback
# from plyer import filechooser
from packages.chd import Dictionary, Character
from kivy.utils import platform

from resizing import change_metrics, window_size

change_metrics()
window_size(device='GalaxyS24',orientation='portrait')

from kivy.metrics import Metrics, dp, sp

from packages.screens import (
    DictionaryNew, 
    DictionaryUpload,
    DictionaryChooser,
    ViewDict,
    Settings,
    ShowCharacter
    )

from packages.kivymd_modules import (
    MyApp,
    MyScreen,
    ObjectProperty,
    ListProperty,
    StringProperty,
    MDBoxLayout,
    MDStackLayout,
    MDAnchorLayout,
    ScreenManager,
    MDSnackbar,
    MultiLineLabel,
    ButtonBehavior,
    AddElement,
    ShowOptions,
    AttentionMsg,
    ErrorMsg,
    MyFileManager,
    ConfirmUnsaved,
    MDLabel
)

from kivy.lang import Builder
from kivy.core.text import LabelBase
from packages.kivymd_modules import print_class

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

DTYPE_MAP = {
    "list": list,
    "str": str,
    "int": int,
    "dict": dict,
}

print_class('MDLabel',search='size')
# print('main')

KV="""

        
"""

class Interface(MDBoxLayout):
    pass
    
class WindowManager(ScreenManager):
    previous_screen_names=ListProperty()
    previous_transition_directions=ListProperty()

class Home(MyScreen):
    
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
class ChD(MyApp):
    window_size_myphone= (1080, 2114)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # the dictionary need categories (and such that are hidden from user)
        dict_categories = self.load_appdata('dictionary_categories.json','defaults')
        self.__dict_categories = {key: DTYPE_MAP[value] for key, value in dict_categories.items()}
        # self.__hidden_categories = dict_categories['hidden']
        
        # make sure there are default settings 
        self.get_default_settings() 
        self.update_design()

        self.load_all_kv_files((self.root_folder+'screens'))
        Builder.load_string(KV)
        print(self.get_metrics())
    
    def build(self):
        screens = [
            Home(name="home"), 
            Settings(name='settings'),
            DictionaryNew(name='new_dict'), # creates new dictionary
            DictionaryUpload(name="upload_dict"), # creates new based on file
            DictionaryChooser(name='select_dict'), # select from existing
            ViewDict(name="view_dict"), # view selected dictionary
        ]
        
        interface = Interface()
        self.add_window_manager(interface.wm)
        for screen in screens:
            self.wm.add_widget(screen)
        return interface
    
    def on_start(self):
        return super().on_start()
    
    # = ============================================================== = #
    # =                            SETTINGS                            = #
    # = ============================================================== = #
    
    @property
    def user_settings_file(self):
        # app_directory
        user_settings_directory = self.get_setting('config_directory',default=True)
        return user_settings_directory + 'settings.json'
    
    @property
    def settings(self):
        # get all the settings (user defined settings if available, if not default settings)
        settings = self.load_json(self.default_settings_file)
        if os.path.isfile(self.user_settings_file):
            settings.update(self.load_json(self.user_settings_file))
        return settings
    
    def get_setting(self,kind,default=False,settings=None):
        # method to always be able to access app settings 
    
        if kind == 'categories':
            result = self.__dict_categories
        elif kind == 'app_directory':
            result = self.get_default_settings()['app_directory']
        elif kind == 'dict_directory':
            result = self.get_default_settings()['app_directory']+'dictionaries/'
        elif kind == 'image_directory':
            result = self.get_default_settings()['app_directory']+'.images/'
        elif kind == 'config_directory':
            result = self.get_default_settings()['app_directory']+'.config/'
        elif kind == 'pleco_template':
            result = self._MyApp__appdata+'templates/'+self.get_default_settings()['pleco_template']
        else:
            result = super().get_setting(kind, default, settings)
        return result
         
    def reset_settings(self):
        # delete all user settings and revert back to default
        self.remove_user_settings()
            
        self.wm.get_screen('settings').update_settings()
        self.update_design()
    
    def remove_user_settings(self):
        app_directory = self.get_setting('app_directory')
        config_directory = self.get_setting('config_directory')
        if os.path.isfile(self.user_settings_file): 
            os.remove(self.user_settings_file)
            if self.root_folder != app_directory \
                and len(os.listdir(config_directory)) == 0:
                    os.rmdir(config_directory)
          
    def save_user_settings(self, settings, remove=[]):
        
        # former user settings (possibly .config folder as well)
        self.remove_user_settings()
        
        # the app directory in default settings needs to be changed 
        default_settings = self.get_default_settings()
        default_settings['app_directory'] = settings['app_directory']
        self.save_default_settings(default_settings)

        # settings directory
        user_settings_directory = self.get_setting('config_directory') 
        os.makedirs(user_settings_directory, exist_ok=True)
        
        # remove keys: they wont be saved under user settings (only default)
        remove = remove + ['access_granted','app_directory','hidden_categories','pleco_template']
        # user settings
        settings = {k:v for k,v in settings.items() if k not in remove}
        self.dump_json(settings,user_settings_directory+"settings.json")
    
    def save_default_settings(self, settings):
        directories = ['dictionaries/','images/']
        for d in directories:
            os.makedirs(settings['app_directory']+d,exist_ok=True)
        
        return super().save_default_settings(settings)
    
    # = ============================================================== = #
    # =                             DESIGN                             = #
    # = ============================================================== = #
    
    def update_design(self):
        # set theme colors
        self.apply_palette(self.get_setting('palette'))
        self.apply_theme(self.get_setting('theme_style'))
        # set font
        LabelBase.register(name="CH", fn_regular=self.get_setting('chinese_font_file'))

    # = ============================================================== = #
    # =                         SCREEN MANAGER                         = #
    # = ============================================================== = #
    
    def switch_screen(self, screen_name, direction, remember=True, home='home',force=False):
        # double check before switch if dictionary has unsaved changes
        if self.wm.current == 'view_dict' \
            and not screen_name.startswith('C') \
                and self.wm.current_screen.edited \
                    and not force:
                        kwargs={
                            "title":"Save Changes",
                            'support_text': 'If you do not accept, all the edits to the dictionary will be lost.'
                        }
                        dialog = ConfirmUnsaved(**kwargs)
                        dialog.direction = direction
                        dialog.remember = remember
                        dialog.screen_name = screen_name
                        dialog.open()
                        switched=None
        else:
            switched = super().switch_screen(screen_name, direction, remember, home)
        # screens are only switched if the new_screen_name differs from old one
        # and the new_screen_name is part of available screen_names
        if switched != None: 
            # when switched:  some screens are removed from memory
            previous_screen_name = switched['previous']['screen_name']
            previous_screen = switched['previous']['screen']
            # current_screen = switched['current']['screen']
            if previous_screen_name.startswith('C'):
                self.wm.remove_widget(previous_screen)
                if screen_name=='view_dict':
                    self.wm.current_screen.set_list_items()
                    
        return self.wm.current_screen
    
    # = ============================================================== = #
    # =                              OTHER                             = #
    # = ============================================================== = #
    
    def check_character_for_multiple(self,character:Character):
        repeat=[] # when character in any form exists in dictionaries
        repeat_exact=[] # when EXACT character exists in dictionary
        dict_directory=self.get_setting('dict_directory')
        for d in os.listdir(dict_directory):
            d_path = f'{dict_directory}/{d}/{d}.jsonl'
            if os.path.isfile(d_path):
                d = Dictionary(name=d)
                d.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
                if character in d:
                    repeat.append(d.name)
                    # compare entries for EXACT (all categories)
                    if character.entry == d[character].entry:
                        repeat_exact.append(d.name)
        # returns list of dictionaries where (exact) character is present
        return repeat,repeat_exact
    
if __name__=="__main__":
    ChD().run()

