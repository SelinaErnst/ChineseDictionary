import json
from pathlib import Path
import os
import traceback
from packages.chd import Dictionary, Character, Grammar, Sentence
from kivy.utils import platform
import re

from resizing import change_metrics, window_size

change_metrics()
# window_size()
# window_size(device='GalaxyS24',orientation='portrait')
# window_size(device='Laptop')
# print(window_size(device='Pixel6',orientation='portrait'))
print(window_size(device='Pixel6',orientation='p'))

from kivymd.icon_definitions import md_icons

from packages.screens import (
    DictionaryNew, 
    DictionaryUpload,
    DictionaryChooser,
    ViewDict,
    GrammarList,
    Settings,
    Home,
    ShowCharacter,
    ShowGrammar,
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
    ShowOptions,
    CategoryItem,
    EditElement,
    print_class,
    Builder,
    LabelBase,
    ColorProperty,
    BooleanProperty,
    ObjectProperty,
    MyFileManager,
    ShowImage
)

APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

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

"""



# = ============================================================== = #
# =                              MAIN                              = #
# = ============================================================== = #

class ChD(MyApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # the dictionary need categories (and such that are hidden from user)
        dict_categories = self.load_appdata('dictionary_categories.json','defaults')
        self.__dict_categories = {key: DTYPE_MAP[value] for key, value in dict_categories.items()}
        # self.__hidden_categories = dict_categories['hidden']
        
        # make sure there are default settings 
        self.get_default_settings() 
        self.update_design()

        self.load_all_kv_files(self.root_folder/'screens')
        Builder.load_string(KV)
    
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
        return user_settings_directory/'settings.json'
    
    @property
    def settings(self):
        # get all the settings (user defined settings if available, if not default settings)
        settings = self.load_json(self.default_settings_file)
        if os.path.isfile(self.user_settings_file):
            settings.update(self.load_json(self.user_settings_file))
            
        return settings
    
    def get_setting(self,kind,default=False,settings=None):
        # method to always be able to access app settings 
        
        # some settings always require default (cannot be changed by user)
        default_settings=self.get_default_settings()
        if kind == 'categories':
            result = self.__dict_categories
        elif kind == 'app_directory':
            result = default_settings['app_directory']
        elif kind == 'dict_directory':
            result = default_settings['app_directory']/'dictionaries'
        elif kind == 'image_directory':
            result = default_settings['app_directory']/'.images'
        elif kind == 'config_directory':
            result = default_settings['app_directory']/'.config'
        elif kind == 'grammar_directory':
            result = default_settings['app_directory']/'grammar'
        elif kind == 'dictionary_template':
            result = self._MyApp__appdata/'templates'/default_settings['dictionary_template']
        elif kind == 'grammar_template':
            result = self._MyApp__appdata/'templates'/default_settings['grammar_template']
        else:
            result = super().get_setting(kind=kind, default=default, settings=settings)
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
        default_settings['app_directory'] = Path(settings['app_directory'])
        self.save_default_settings(default_settings)

        # settings directory
        user_settings_directory = self.get_setting('config_directory') 
        os.makedirs(user_settings_directory, exist_ok=True)
        
        # remove keys: they wont be saved under user settings (only default)
        remove = remove + ['access_granted','app_directory','hidden_categories','dictionary_template']
        # user settings
        settings = {k:v for k,v in settings.items() if k not in remove}
        self.dump_json(settings,user_settings_directory/'settings.json')
    
    def save_default_settings(self, settings):
        directories = ['dictionaries','.images','grammar']
        for d in directories:
            os.makedirs(settings['app_directory']/d,exist_ok=True)
        super().save_default_settings(settings)
            
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
        
        def remove_duplications(screen_name):
            all_screen_names = [screen.name for screen in self.wm.screens]
            # print(all_screen_names)
            if screen_name.startswith('C') and sum([name.startswith('C') for name in all_screen_names])>1:
                for name in [name for name in all_screen_names if name.startswith('C')]:
                    if name != screen_name:
                        self.wm.remove_widget(self.wm.get_screen(name))
                    if name in self.wm.previous_screen_names:
                        self.wm.previous_screen_names.remove(name)
            elif screen_name.startswith('G') and sum([name.startswith('G') for name in all_screen_names])>1:
                for name in [name for name in all_screen_names if name.startswith('G')]:
                    if name != screen_name:
                        self.wm.remove_widget(self.wm.get_screen(name))
                    if name in self.wm.previous_screen_names:
                        self.wm.previous_screen_names.remove(name)
        
        remove_duplications(screen_name=screen_name)
        
        # double check before switch if dictionary has unsaved changes
        current_screen = self.wm.current_screen
        if hasattr(current_screen,'edited') and self.wm.current_screen.edited and not force:
            if self.wm.current  == 'view_dict' and not screen_name.startswith('C'):
                support_text='If you do not accept, all the edits to the dictionary will be lost.'
                dialog = ConfirmUnsaved(what='save_dict_edit',name=self.wm.current_screen.dict_name,support_text=support_text)
                dialog.set_attrs(direction=direction,remember=remember,screen_name=screen_name)
                dialog.open()
            elif self.wm.current  == 'gram_list' and not screen_name.startswith('G'):
                support_text='If you do not accept, all the edits to the grammar list will be lost.'
                dialog = ConfirmUnsaved(what='save_gram_edit',name='',support_text=support_text)
                dialog.set_attrs(direction=direction,remember=remember,screen_name=screen_name)
                dialog.open()
            else:
                super().switch_screen(screen_name, direction, remember, home)
        else:
            super().switch_screen(screen_name, direction, remember, home)
            
        try:
            self.wm.current_screen.set_list_items()
        except:
            pass
        # print('P',self.wm.previous_screen_names)
        return self.wm.current_screen
    
    # = ============================================================== = #
    # =                          SURVEILLANCE                          = #
    # = ============================================================== = #
    
    def check_character_for_multiple(self,character:Character):
        repeat=[] # when character in any form exists in dictionaries
        repeat_exact=[] # when EXACT character exists in dictionary
        dict_directory=self.get_setting('dict_directory')
        for some_dict in os.listdir(dict_directory):
            d_path = dict_directory / some_dict / (some_dict+'.jsonl')
            print(d_path)
            if os.path.isfile(d_path):
                some_dict = Dictionary(name=some_dict)
                some_dict.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
                if character in some_dict:
                    repeat.append(some_dict.name)
                    # compare entries for EXACT (all categories)
                    if character.entry == some_dict[character].entry:
                        repeat_exact.append(some_dict.name)
        # returns list of dictionaries where (exact) character is present
        return repeat,repeat_exact
    
    def show_grammar(self,grammar=None,entry=None):
        screen = self.wm.current_screen
        if screen.name.startswith('C') and entry!=None:
            links = screen.parent_dictionary.get_linked_grammar(screen.character)
            if entry in links:
                grammar=links[entry]
        if grammar!=None:
            new_screen = ShowGrammar(name='G',grammar=grammar,parent_screen=self.wm.get_screen('gram_list'),editable=False)
            self.add_screen(screen=new_screen,direction='left')
            
    def show_character(self,character):
        screen = ShowCharacter(character=character, dict_screen=self.wm.get_screen('gram_list'))
        self.add_screen(screen=screen,direction='left')
        
    def show_image(self,image_type,file,size=[700,700]):
        if image_type!="":
            dialog = ShowImage(source=file,title=image_type,image_size=size)
            dialog.open()
        
    def find_character(self,gram_link:Character):
        dict_directory=self.get_setting('dict_directory')
        linked_characters={}
        
        for some_dict in os.listdir(dict_directory):
            d_path = dict_directory / some_dict / (some_dict+'.jsonl')
            if os.path.isfile(d_path):
                some_dict = Dictionary(name=some_dict)
                some_dict.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
                some_dict.set_grammar(self.wm.get_screen('gram_list').grammar_list)
                links = some_dict.get_linked_character(grammar_link=gram_link)
                linked_characters[some_dict.name]={'characters':links,'dictionary':some_dict}
                
        options={f'{dict_name}: {str(c)}':(c,links['dictionary']) for dict_name,links in linked_characters.items() for c in links['characters']}
        
        def func(text):
            char, d = options[text]
            screen = ShowCharacter(character=char, editable=False)
            self.add_screen(screen=screen,direction='left')
        
        if len(options) > 0:
            kwargs={
                "title":"Characters with Grammar Entry",
                'support_text':"",
                "options":options.keys(),
                "itemclass":"LeftListItem",
                "func":func,
            }
            dialog = ShowOptions(**kwargs)
            dialog.open()
            
    def backup(self):
        
        def backup_to(directory):
            self.wm.current_screen.file_manager.close()
            dict_directory=self.get_setting('dict_directory')
            backup_name='ChD_dictionaries_BACKUP.db'
            backup_dir=Path(directory)
            if os.path.isfile(backup_dir/backup_name): 
                os.remove(backup_dir/backup_name)
            for some_dict in os.listdir(dict_directory):
                d_path = dict_directory/some_dict/(some_dict+'.jsonl')
                if os.path.isfile(d_path):
                    some_dict = Dictionary(name=some_dict)
                    some_dict.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
                    some_dict.set_grammar(self.wm.get_screen('gram_list').grammar_list)
                    some_dict.write(directory=backup_dir,filename=backup_name,clean=False)
                    
        self.wm.current_screen.file_manager = MyFileManager(
            description='Choose directory for backup.',
            select_path=backup_to,
            ext=['.____nothing____'])
        self.wm.current_screen.file_manager.show(path=None,use_root_folder=False)    
            
    def restore(self):
        
        def restore_from_backup(file):
            from packages.chd import grammar_to_jsonl, open_db, get_table_names, close_db, get_unique_values
            self.wm.current_screen.file_manager.close()
            conn,cursor = open_db(file)
            tables = get_table_names(cursor)
            has_grammar = 'Grammar' in tables
            # tables = [tab for tab in tables if tab not in ['Grammar','Links']]
            dictionaries = get_unique_values(cursor,'Dictionary','dict_name')
            categories=self.get_setting('categories')
            dict_directory = self.get_setting('dict_directory')
            gr_directory = self.get_setting('grammar_directory')
            gr_path_jsonl=gr_directory/'grammar.jsonl'
            
            overwrite=True
            for name in dictionaries:
                d = Dictionary(name=name)
                d.read(filepath=file,add=False,categories=categories,name=name)
                directory=dict_directory/name
                if not os.path.isdir(directory) or overwrite:
                    os.makedirs(directory, exist_ok=True)
                    d.write(directory=directory,filename=name,file_format='jsonl')
                else:
                    d.write(directory=directory,filename=f'{name}_BACKUP',file_format='jsonl')
            if has_grammar and (not os.path.isfile(gr_path_jsonl) or overwrite):
                grammar_to_jsonl(grammar=d.grammar,path=gr_path_jsonl)
            elif has_grammar:
                gr_path_jsonl=gr_directory/'grammar_BACKUP.jsonl'
                grammar_to_jsonl(grammar=d.grammar,path=gr_path_jsonl)
                
            close_db(conn)
        
        self.wm.current_screen.file_manager = MyFileManager(
            description='Choose backup file.',
            select_path=restore_from_backup,
            ext=[".db"])
        self.wm.current_screen.file_manager.show(path=None,use_root_folder=False)
        
    def clean_files(self):
        pass
                    
if __name__=="__main__":
    ChD().run()

