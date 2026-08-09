import json
from pathlib import Path
import os
import traceback
# from typing_extensions import override
from packages.chd import Dictionary, Character, Grammar, Sentence
from kivy.utils import platform
import re

from kivy.config import Config
icon_path=Path(__file__).resolve().parent/'appdata'/'images'/'book_icon.png'
Config.set('kivy', 'window_icon', icon_path)
from resizing import change_metrics, window_size

device='Laptop'
# device='GalaxyS24'
# device='Pixel6'
# device='TabS6'
orientation='max'
# orientation='portrait'
# orientation='landscape'

change_metrics(device)
window_size(device,orientation)

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
    )

from packages.kivy import (
    MyApp,
    print_class,
    Builder,
    LabelBase,
)

APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

DTYPE_MAP = {
    "list": list,
    "str": str,
    "int": int,
    "dict": dict,
}

# print_class('MDStackLayout',search='widget')
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
        # self.__dict_categories = self.get_all_categories()
        
        # make sure there are default settings
        self.get_default_settings()
        self.update_design()

        self.load_all_kv_files(self.root_folder/'screens')
        Builder.load_string(KV)
    
    def pre_load_widgets(self):
        from packages.screens import DictSettings
        
        super().pre_load_widgets()
        self.pre_loaded_widgets.update({
            'grammar':ShowGrammar(name='G'),
            'character':ShowCharacter(),
            'grammar_protect':ShowGrammar(name='G',editable=False),
            'character_protect':ShowCharacter(editable=False),
            'dict_settings' : DictSettings(),
        })
    
    def build(self):
        super().build()
        interface = Interface()
        self.add_window_manager(interface.wm)
        Screen = self.get_screen_widget('home')
        self.wm.add_widget(Screen(name='home'))
        self.add_more_screens()
        # self.switch_screen('settings','down')
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
    def app_files(self):
        # found all at self.config_dir
        return {
            'categories':'dictionary_categories.json',
            'settings':'default_settings.json',
            'filter':'dictionary_filter.json',
            'backup':'Backups/data.db',
            'grammar_tags':'grammar_tags.txt',
            }
        
    @property
    def app_directories(self):
        directories = {
            'dict_directory':'dictionaries',
            'image_directory':'.images',
            'grammar_directory':'grammar',
            'template_directory':'templates',
            'config_directory':'.config'
            }
        return directories
    
    @property
    def settings(self):
        # get all the settings (user defined settings if available, if not default settings)
        settings = self.get_app_file('settings')
        if os.path.isfile(self.user_settings_file):
            settings.update(self.load_json(self.user_settings_file))
        return settings
    
    # @override
    def get_setting(self,kind,default=False,settings=None):
        # method to always be able to access app settings 
        # some settings always require default (cannot be changed by user)
        default_settings=self.get_default_settings()
        if kind == 'categories':
            result = {key: DTYPE_MAP[value] for key, value in self.get_categories().items()}
        elif kind == 'templates':
            result = self.get_all_templates()
        elif kind == 'tmp_directory':
            result = self.config_dir/'tmp'
            os.makedirs(result,exist_ok=True)
        elif kind == 'app_directory':
            result = default_settings['app_directory']
        elif kind in self.app_directories:
            result = default_settings['app_directory']/self.app_directories[kind]
        elif kind == 'grammar_template':
            result = self.root_folder/'appdata'/'templates'/default_settings['grammar_template']
        else:
            result = super().get_setting(kind=kind, default=default, settings=settings)
        return result
         
    def reset_settings(self):
        # delete all user settings and revert back to default
        self.remove_user_settings()
            
        self.wm.get_screen('settings').update_settings()
        self.update_design()
    
    def remove_user_settings(self):
        config_directory = self.get_setting('config_directory')
        if os.path.isfile(self.user_settings_file): 
            os.remove(self.user_settings_file)
            if self.root_folder != self.app_directory \
                and len(os.listdir(config_directory)) == 0:
                    os.rmdir(config_directory)
          
    def save_user_settings(self, settings, remove=[]):
        
        # former user settings (possibly .config folder as well)
        self.remove_user_settings()
        
        # the app directory in default settings needs to be changed 
        default_settings = self.get_default_settings()
        app_directory = Path(settings['app_directory'])
        default_settings['app_directory'] = app_directory
        self.app_directory = app_directory
        self.save_app_config(default_settings,'settings')

        # settings directory
        user_settings_directory = self.get_setting('config_directory') 
        os.makedirs(user_settings_directory, exist_ok=True)
        
        # remove keys: they wont be saved under user settings (only default)
        # remove = remove + ['app_directory','chinese_font_file']
        keep = ['theme_style','palette','import_directory']
        # user settings
        settings = {k:v for k,v in settings.items() if k in keep}
        self.dump_json(settings,user_settings_directory/'settings.json')
    
    def change_app_directory(self,directory):
        default_settings = self.get_default_settings()
        default_settings['app_directory']=directory
        import_dir = default_settings['import_directory']
        if os.path.exists(directory):
            self.app_directory = Path(directory)
            self.save_app_config(default_settings,'settings')
            for d in self.app_directories.values():
                os.makedirs(Path(directory)/d,exist_ok=True)
        
    def get_categories(self):
        
        categories = self.get_app_file('categories')
        if categories!=None: return categories
        
        categories = self.get_app_data('dictionary_categories.json','defaults')
        categories = {} if categories==None else categories
        
        self.save_app_config(categories,'categories')
        return categories
    
    def tmp_file(self,file,tmp_directory=None):
        if tmp_directory==None: tmp_directory = self.get_setting('tmp_directory')
        return super().tmp_file(file=file,tmp_directory=tmp_directory)
    
    def tmp_file_rm(self,file,tmp_directory=None):
        if tmp_directory==None: tmp_directory = self.get_setting('tmp_directory')
        tmp_directory = self.get_setting('tmp_directory')
        return super().tmp_file_rm(file=file,tmp_directory=tmp_directory)
            
    def remove_file(self,file,create_tmp=False,tmp_directory=None):
        if tmp_directory==None: tmp_directory = self.get_setting('tmp_directory')
        return super().remove_file(file=file,create_tmp=create_tmp,tmp_directory=tmp_directory)
        
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
                name = self.wm.current_screen.dict_name
                support_text=f'If you do not accept, all the edits to the dictionary <{name}> will be lost.'
                dialog = self.pre_loaded_widgets['save_dict']
                dialog.set_attrs(support_text=support_text,direction=direction,remember=remember,screen_name=screen_name)
                dialog.open()
            elif self.wm.current  == 'gram_list' and not screen_name.startswith('G'):
                support_text='If you do not accept, all the edits to the grammar list will be lost.'
                dialog = self.pre_loaded_widgets['save_gram']
                dialog.set_attrs(support_text=support_text,direction=direction,remember=remember,screen_name=screen_name)
                dialog.open()
            else:
                super().switch_screen(screen_name, direction, remember, home)
        else:
            super().switch_screen(screen_name, direction, remember, home)
            
        if hasattr(self.wm.current_screen,'set_up_screen'):
            self.wm.current_screen.set_up_screen()

        return self.wm.current_screen
    
    # = ============================================================== = #
    # =                        EDIT DICTIONARIES                       = #
    # = ============================================================== = #
    
    def move_character(self,character:Character):
        dict_directory=self.get_setting('dict_directory')
        
        def copy_to_dict(dict_name):
            d_path = dict_directory / dict_name / (dict_name+'.jsonl')
            some_dict = Dictionary(name=dict_name)
            some_dict.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
            if character not in some_dict:
                some_dict+=character
                some_dict.write(directory=dict_directory/dict_name,file_format='jsonl',clean=True)
            elif character in some_dict and character.entry != some_dict[character].entry:
                pass
        
        kwargs={
            "title":"Move Character to other Dictionary",
            'support_text':"Choose which dictionary the selected character should be copied to.",
            "options":[str(d) for d in os.listdir(dict_directory)],
            "itemclass":"MyListItem",
            "func": copy_to_dict
        }
        dialog = self.pre_loaded_widgets['options']
        dialog.list_options(**kwargs)
        dialog.open()
        
    # = ============================================================== = #
    # =                          SURVEILLANCE                          = #
    # = ============================================================== = #
    
    def check_character_for_multiple(self,character:Character):
        repeat=[] # when character in any form exists in dictionaries
        repeat_exact=[] # when EXACT character exists in dictionary
        dict_directory=self.get_setting('dict_directory')
        for some_dict in os.listdir(dict_directory):
            d_path = dict_directory / some_dict / (some_dict+'.jsonl')
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
    
    def find_grammar(self,character=None,entry=None):
        grammar_list = self.wm.get_screen('gram_list').read_grammar_jsonl()
        screen = self.wm.current_screen
        if character==None and screen.name.startswith('C') and entry!=None:
            character = screen.character
            dictionary = screen.parent_dictionary
        elif character!=None:
            dictionary = Dictionary()
        else:
            return None
        
        dictionary.set_grammar(grammar_list)
        links = dictionary.get_linked_grammar(character,key='grammar')
        grammar=links[entry] if entry in links else []
        
        def grammar_name(g):
            name = f'Level {g.level}: {g.title}'
            if g.subtitle!="": name+=f'\n{g.subtitle}'
            return name

        options={grammar_name(g):g for g in grammar}
        
        def func(text):
            grammar = options[text]
            if grammar!=None:
                screen = self.my_app.pre_loaded_widgets['grammar_protect']
                screen.build_scroll(grammar=grammar)
                self.add_screen(screen=screen,direction='left')
        
        if isinstance(grammar,list) and len(grammar)>0:
            kwargs={
                "title":"Characters with Grammar Entry",
                'support_text':"",
                "options":options.keys(),
                "itemclass":"LeftListItem",
                "func":func,
            }
            dialog = self.pre_loaded_widgets['options']
            dialog.list_options(**kwargs)
            dialog.open()
        

    def find_character(self,character:Character=None,key='grammar'):
        dict_directory=self.get_setting('dict_directory')
        linked_characters={}
        screen = self.wm.current_screen
        if not isinstance(character,Character) and screen.name.startswith('C'):
            og_dict_name = screen.parent_dictionary.name
            from packages.chd.unicode_characters import chinese_char, not_chinese_char
            result = re.match(rf'([{chinese_char}]*)[/|\s](.*)\s*\[([{not_chinese_char}]*?)\].*',character)
            if result != None: 
                simple,traditional,pronunciation = [v if v!="" else None for v in result.groups()]
                character = Character(simple=simple,traditional=traditional,pronunciation=pronunciation)
            else: return None
        else: og_dict_name=""
        
        for some_dict in os.listdir(dict_directory):
            d_path = dict_directory / some_dict / (some_dict+'.jsonl')
            if os.path.isfile(d_path):
                some_dict = Dictionary(name=some_dict)
                some_dict.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
                grammar_list = self.wm.get_screen('gram_list').read_grammar_jsonl()
                some_dict.set_grammar(grammar_list)
                links = some_dict.get_linked_character(character=character,key=key)
                linked_characters[some_dict.name]={'characters':links,'dictionary':some_dict}
        
        def char_name(dict_name,character):
            return f'{dict_name}: {str(character)}'
        
        options={char_name(dict_name,c):(c,dict_name) for dict_name,links in linked_characters.items() for c in links['characters']}
        
        def func(text):
            char, dict_name = options[text]
            
            if og_dict_name=="" or og_dict_name!=dict_name:
                config_filename=f'{dict_name.lower().replace(" ","_")}_config.json'
                config_file = self.get_setting('dict_directory')/dict_name/config_filename
                config = {'name':dict_name,'categories':{},'template':"",'sort_key':'pronunciation','sort_order':'ascending'}
                
                if not os.path.isfile(config_file):
                    categories = self.get_categories()
                    updater = {'categories':list(categories)}
                    config.update(updater)
                else:
                    updater = self.load_json(config_file)
                    if updater['name'] == dict_name: config.update(updater)
                    
                test_dict = Dictionary(name=dict_name)
                screen = self.pre_loaded_widgets['character_protect']
                screen.set_background(config=config,dict_screen=None, parent_dictionary=test_dict)
                screen.build_scroll(character=char)
                self.add_screen(screen=screen,direction='left')
                
            else:
                screen = self.wm.current_screen
                idx = screen.parent_dictionary.index(char.uniq)
                screen.show_other(idx,'left')
        
        if len(options) > 0:
            kwargs={
                "title":"Character found in Dictionaries",
                'support_text':"",
                "options":options.keys(),
                "itemclass":"LeftListItem",
                "func":func,
            }
            dialog = self.pre_loaded_widgets['options']
            dialog.list_options(**kwargs)
            dialog.open()
            
    def get_all_templates(self):
        template_directory = self.get_setting('template_directory')
        templates = os.listdir(template_directory) if os.path.isdir(template_directory) else []
        return templates
    
    def rename_category(self,rename_map:dict):
        dict_directory=self.get_setting('dict_directory')
        
        def replace_keys(old_dict,rename_map):
            return {rename_map.get(k, k): v for k, v in old_dict.items()}
                
        
        for some_dict in os.listdir(dict_directory):
            filepath = dict_directory/some_dict/(some_dict+'.jsonl')
            if os.path.isfile(filepath):
                
                with open(filepath,'r') as in_file:
                    json_list = list(in_file)
                new_entry_list = []
                for json_str in json_list:
                    entry=json.loads(json_str)
                    entry=replace_keys(entry,rename_map)
                    new_entry_list.append(entry)
                
                with open(filepath,'w') as out_file:
                    for entry in new_entry_list:
                        json.dump(entry, out_file, indent=None, ensure_ascii=False)
                        out_file.write('\n')
                        
    # = ============================================================== = #
    # =                             BACKUP                             = #
    # = ============================================================== = #
                
    def backup(self,directory=None,filename=None):
        
        def backup_to(directory,filename=filename):
            self.dismiss_file_manager()
            dict_directory=self.get_setting('dict_directory')
            if filename==None: 
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d")
                filename='ChD_BACKUP_'+timestamp
            if not filename.endswith('.db'): filename+='.db'
            backup_dir=Path(directory)
            if os.path.isfile(backup_dir/filename): 
                os.remove(backup_dir/filename)
            for some_dict in os.listdir(dict_directory):
                d_path = dict_directory/some_dict/(some_dict+'.jsonl')
                if os.path.isfile(d_path):
                    some_dict = Dictionary(name=some_dict)
                    some_dict.read(d_path,file_format='jsonl',add=False,categories=self.get_setting('categories'))
                    grammar_list = self.wm.get_screen('gram_list').get_grammar_list()
                    some_dict.set_grammar(grammar_list)
                    some_dict.write(directory=backup_dir,filename=filename,clean=False)

        if directory==None:  
            kwargs = {
                'description' : 'Choose directory for backup.',
                'select_path' : backup_to,
                'ext' : ['.____nothing____'],
            }
            file_manager = self.pre_loaded_widgets['file_manager']
            file_manager.set_attrs(**kwargs)
            file_manager.show(path=None,use_root_folder=False)
            self.wm.current_screen.file_manager = file_manager
        else:
            backup_to(directory=directory)
            
    def restore(self):
        
        data_file = self.get_app_file('backup')
        # if os.path.isfile(data_file):
        #     from packages.chd import open_db, get_table_columns
        #     conn,cursor = open_db(data_file)
        #     query = f"SELECT * FROM Categories"
        #     rows= cursor.execute(query).fetchall()
        #     categories = {dict(row)['category']:dict(row)['dtype'] for row in rows}
        #     return categories
        
        def restore_from_backup(file):
            from packages.chd import grammar_to_jsonl, open_db, get_table_names, close_db, get_unique_values
            self.dismiss_file_manager()
            conn,cursor = open_db(file)
            tables = get_table_names(cursor)
            has_grammar = 'Grammar' in tables
            # tables = [tab for tab in tables if tab not in ['Grammar','Links']]
            dictionaries = get_unique_values(cursor,'Dictionary','dict_name')
            dict_directory = self.get_setting('dict_directory')
            gr_directory = self.get_setting('grammar_directory')
            gr_path_jsonl=self.get_setting('grammar_directory')/'grammar.jsonl'
            
            overwrite=True
            for name in dictionaries:
                d = Dictionary(name=name)
                d.read(filepath=file,add=False,categories=self.get_setting('categories'),name=name)
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
        
        kwargs = {
            'description' : 'Choose backup file.',
            'select_path' : restore_from_backup,
            'ext' : ['.db'],
        }
        file_manager = self.pre_loaded_widgets['file_manager']
        file_manager.set_attrs(**kwargs)
        file_manager.show(path=None,use_root_folder=False)
        self.wm.current_screen.file_manager = file_manager
            
    def clean_files(self):
        pass
                    
if __name__=="__main__":
    ChD().run()

