import json
from pathlib import Path
import os
import traceback
from packages.chd import Dictionary, Character, Grammar
from kivy.utils import platform

from resizing import change_metrics, window_size

change_metrics()
window_size(device='GalaxyS24',orientation='portrait')

from packages.screens import (
    DictionaryNew, 
    DictionaryUpload,
    DictionaryChooser,
    ViewDict,
    Settings,
    Home,
    ShowCharacter,
    Interface,
    WindowManager,
    )

from packages.kivy import (
    MyApp,
    MyScreen,
    ListProperty,
    MDBoxLayout,
    ScreenManager,
    ConfirmUnsaved,
    print_class,
    Builder,
    LabelBase,
    ColorProperty
)

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

DTYPE_MAP = {
    "list": list,
    "str": str,
    "int": int,
    "dict": dict,
}

# print_class('MDLabel',search='size')
# print('main')

# = ============================================================== = #
# =                             GRAMMAR                            = #
# = ============================================================== = #

from packages.kivy import MyScreen

KV="""
<GrammarList>:
    rv_scroll: rv_scroll
    filter: filter
    search: search
    MDBoxLayout:
        orientation: 'vertical'
        padding: 20
        Toggle:
            id: filter
            height: self.minimum_height
            Level:
                text: 'A1'
            Level:
                text: 'A2'
            Level:
                text: 'B1'
            Level:
                text: 'B2'
            Level:
                text: 'C1'
            Level:
                text: 'C2'
        MDAnchorLayout:
            size_hint_y: None
            height: search.height+20
            anchor_y: 'top'
            anchor_x: 'left'
            MDTextField:
                id: search
                theme_font_name: "Custom"
                font_name:"CH"
                on_text: root.set_list_items()
                
        MDBoxLayout:
            MDRecycleView:
                id: rv_scroll
                viewclass: 'GrammarItem'
                RecycleBoxLayout:
                    id: scroll
                    padding: 0,0,0,300
                    orientation: "vertical"
                    size_hint: 1, None
                    height: self.minimum_height
                    default_size_hint: 1, None
                    default_height: None
                    spacing: 10
                
<Level@TextToggleButton>:
    font_style: 'Title'
    role: 'large'
    width: self.height
    on_release: self.toggle_two(only_one=False)
    custom_color: app.custom.colors['level'+self.text]
    custom_font_color: app.custom.colors['text_level'+self.text]
                
"""
gr1={
    'level':'B1',
    'title':'Expressing AGAIN in the past',
    'subtitle':'Expresses repetition of a an action that has already occurred in the past',
    'structures':['(Subj. +) 又 + Verb + 了'],
    'opposite_structures':['(Subj. +) 又 + 不 / 没 + Verb (+ 了)'],
    'explanation':"又 [yòu] is used in declarative sentences and describes the simple repetition of actions. This repeated action has already occurred once in the past. It doesn't have to be in quick succession; it happened before, and now it's happened again. 再  [hái] and 还  [zài] can be used to indicate 'again' or repeating a previous action.",
}
gr1=Grammar(**gr1)

gr2={
    'level':'B2',
    'title':'Emphasizing negation   ',
    # 'subtitle':'Expresses repetition of a an action that has already occurred in the past',
    'structures':['(Subj. +) 又 + Verb + 了'],
    'opposite_structures':['(Subj. +) 又 + 不 / 没 + Verb (+ 了)'],
    'explanation':"又 [yòu] is used in declarative sentences and describes the simple repetition of actions. This repeated action has already occurred once in the past. It doesn't have to be in quick succession; it happened before, and now it's happened again. 再  [hái] and 还  [zài] can be used to indicate 'again' or repeating a previous action.",
}
gr2=Grammar(**gr2)

class GrammarList(MyScreen):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_list_items()
        for child in self.filter.children:
            child.toggle_on()
        
    @property        
    def grammar_list(self):
        g = [gr1,gr2]*100
        return g
        
    def create_dataitem(self,grammar,**kwargs):
        dataitem={'grammar':grammar,'callback':lambda x:x}
        dataitem.update(grammar.to_dict())
        if grammar.level.startswith('A'): color='blue'
        elif grammar.level.startswith('B'): color='green'
        # elif grammar.level.startswith('B'): color=self.theme_cls.levelB
        elif grammar.level.startswith('C'): color='orange'
        kwargs={k:v for k,v in kwargs.items() if v!=None}
        kwargs.update({'level_color':color})
        dataitem.update(kwargs)
        return dataitem 
        
    def set_list_items(self):
        from kivy.clock import Clock
        Clock.max_iteration = 24
        self.rv_scroll.data = []
        
        def apply_filter(dataitem):
            include,exclude = self.filter.include,self.filter.exclude
            if dataitem['grammar'].level in include: return True
            elif dataitem['grammar'].level in exclude: return False
            else: return False
            
        def apply_search(dataitem):
            search_entry = self.search.text
            title = dataitem['grammar'].title.lower()
            subtitle = dataitem['grammar'].subtitle.lower()
            if search_entry.lower() in title: return True
            elif search_entry.lower() in subtitle: return True
            else: return False
        
        for gr in self.grammar_list:
            dataitem=self.create_dataitem(grammar=gr)
            if apply_filter(dataitem) and apply_search(dataitem):
                self.add_list_item(dataitem)
            
    def add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)

# = ============================================================== = #
# =                              MAIN                              = #
# = ============================================================== = #



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
        super().build()
        interface = Interface()
        self.add_window_manager(interface.wm)
        Screen = self.get_screen_widget('home')
        self.wm.add_widget(Screen(name='home'))
        self.add_more_screens()
        return interface
    
    def add_more_screens(self):
        for name in [screen.name for screen in self.wm.screens]:
            screen_instance = self.wm.get_screen(name)
            if name != 'home': self.wm.remove_widget(screen_instance)
        screens = [screen(name=name) for name,screen in self.__screen_map.items() if name!='home']
        for screen in screens:
            self.wm.add_widget(screen)
    
    def reload(self,name:str|None=None):
        self.switch_screen('home','right')
        if name!=None  and name in [screen.name for screen in self.wm.screens]:
            screen_instance = self.wm.get_screen(name)
            self.wm.remove_widget(screen_instance)
            Screen = self.get_screen_widget(name)
            self.wm.add_widget(Screen(name=name))
        else:
            self.add_more_screens()
    
    @property
    def __screen_map(self):
        screen_map={
            'home': Home,
            'settings': Settings,
            'new_dict': DictionaryNew, # creates new dictionary
            'upload_dict': DictionaryUpload, # creates new dictionary
            'select_dict': DictionaryChooser, # creates new dictionary
            'view_dict': ViewDict, # creates new dictionary
            'gram_list': GrammarList,
        }
        return screen_map
    
    def get_screen_widget(self,name):
        return self.__screen_map[name]

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
    # =                          SURVEILLANCE                          = #
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

