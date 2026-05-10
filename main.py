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
window_size(device='GalaxyS24',orientation='portrait')

from kivymd.icon_definitions import md_icons

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
    ShowOptions,
    CategoryItem,
    EditElement,
    print_class,
    Builder,
    LabelBase,
    ColorProperty,
    BooleanProperty,
    ObjectProperty,
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
<GrammarList>:
    rv_scroll: rv_scroll
    filter: filter
    search: search
    bottom_nav: bottom_nav
    
    MDBoxLayout:
        orientation: 'vertical'
        MDBoxLayout:
            md_bg_color: app.custom.colors['head']
            orientation: 'vertical'
            adaptive_height: True
            padding: 20
            MDBoxLayout:
                size_hint_y: None
                height: filter.height
                orientation: 'horizontal'
                spacing: 50
                MDLabel:
                    text: 'Level'
                    font_style: "Title"
                    role: 'small'
                    adaptive_width: True
                    theme_text_color: "Custom"
                    text_color: app.custom.colors['button_fg']
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
                anchor_y: 'bottom'
                anchor_x: 'left'
                EntryField:
                    id: search
                    theme_font_name: "Custom"
                    font_name:"CH"
                    color_normal: app.custom.colors['textfield_search']
                    color_focus: app.custom.colors['textfield_search']
                    on_text: root.set_list_items()
                    allow_empty: True     
        MDRecycleView:
            id: rv_scroll
            viewclass: 'GrammarItem'
            RecycleBoxLayout:
                id: scroll
                padding: 20,20,20,300
                orientation: "vertical"
                size_hint: 1, None
                height: self.minimum_height
                default_size_hint: 1, None
                default_height: None
                spacing: 10
                
    MDBottomSheet:
        id: bottom_nav
        radius: 0
        size_hint: None,None
        height: 170
        width: Window.width 
        sheet_type: "standard"
        md_bg_color: app.custom.colors['bottom']


        BottomSheetDragHandleContainer:
            padding: 20
            MDAnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                size_hint_y: None
                height: bottom_nav.height-2*20
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_width: True
                    size_hint_y: None
                    height: self.parent.height
                    spacing: 50
                    MyIconButton:
                        text: 'Add'
                        icon: 'plus'
                        size: self.parent.height, self.parent.height
                        style: 'text'
                        md_bg_color: bottom_nav.md_bg_color
                        on_release: root.add_grammar()
                    MyIconButton:
                        text: 'Save'
                        icon: 'content-save'
                        style: 'text'
                        size: self.parent.height, self.parent.height
                        md_bg_color: bottom_nav.md_bg_color
                        on_release: root.save_grammar()
                
<Level@TextToggleButton>:
    font_style: 'Title'
    role: 'medium'
    width: self.height
    kind: 'select_multiple'
    custom_color: app.custom.colors['level'+self.text]
    custom_font_color: app.custom.colors['text_level'+self.text]
                

<ShowGrammar>:
    scroll: scroll
    bottom_nav: bottom_nav
    ScrollView:
        MDStackLayout:
            id: scroll
            size_hint: 1, None
            # height: self.minimum_height+(66+2*10)*2
            height: self.minimum_height+300
            padding: 10
            spacing: 20   
                        
    MDBottomSheet:
        id: bottom_nav
        radius: 0
        size_hint: None,None
        height: 170
        width: Window.width 
        sheet_type: "standard"
        md_bg_color: app.custom.colors['bottom']


        BottomSheetDragHandleContainer:
            padding: 20
            MDAnchorLayout:
                anchor_x: 'center'
                anchor_y: 'center'
                size_hint_y: None
                height: bottom_nav.height-2*20
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_width: True
                    size_hint_y: None
                    height: self.parent.height
                    spacing: 50
                    MyIconButton:
                        text: 'Empty'
                        icon: 'eraser'
                        size: self.parent.height, self.parent.height
                        style: 'text'
                        md_bg_color: bottom_nav.md_bg_color
                        on_release: root.empty_grammar()
"""

class ShowGrammar(MyScreen):
    # edited=BooleanProperty(False)
    editable=BooleanProperty(True)
    grammar = ObjectProperty()
    parent_screen = ObjectProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_scroll()
    
    def build_scroll(self):
        for category in self.grammar.categories:
            self.list_content(category=category,content=self.grammar[category])
            
    def clean_scroll(self):
        # for c in [c for c in self.ids.scroll.children]:
            # c.clear_widgets()
        self.ids.scroll.clear_widgets()
    
    def list_content(self,category,content):
        small_text=['level','title','subtitle','tags']
        long_text=['explanation','sentences','structures','opposite_structures','characters','opposite_characters']
        if category == 'explanation' and isinstance(content,str):
            content = re.sub(r'[■|●|□|○|◼]','■',content)
        if category in small_text:
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=False,line_width=330,head_width=200,editable=self.editable)
        elif category in long_text:
            l=CategoryItem(
                category=category,values=content,
                cols=1,small=False,head_width=None,editable=self.editable)
        else:
            l=CategoryItem(
                category=category,values=content,
                cols=2,small=True,line_width=330,head_width=200,editable=self.editable)
            
        if not self.editable and isinstance(self.grammar[category],Dictionary): 
            if len(self.grammar[category])==0: return None
        if self.editable or self.grammar[category] not in [[],"",None]:
            self.ids.scroll.add_widget(l)
            self.scroll.ids[category]=l
        
    def empty_grammar(self):
        if self.editable:
            self.grammar.clear()
            self.parent_screen.set_list_items()
            self.clean_scroll()
            self.build_scroll()
            self.parent_screen.edited = True
    
    def edit_category(self,category):
        if self.editable:
            title=category.replace('_',' ').title()
            category=category.lower().replace(' ','_')
            content = self.grammar[category]
            dialog = None
            
            if category == "characters":
                content={'simple':'','traditional':'','pronunciation':''}
                title="Add Character"
            if category == "opposite_characters":
                content={'simple':'','traditional':'','pronunciation':''}
                title="Add Opposite Character"
            elif category=="sentences": 
                content={'text':'','pronunciation':'','translation':''}
                title="Add Sentence"
            
            if category == "tags":
                dialog = EditElement(style="custom",allow_multiple=True,dtype=list,title=title,options=self.grammar.valid_tags)
            elif isinstance(content,str):
                dialog = EditElement(style="normal",allow_multiple=False,dtype=str,title=title)
            elif isinstance(content,list) and (len(content)>0 and isinstance(content[0],str) or len(content)==0):
                dialog = EditElement(style="normal",allow_multiple=True,dtype=list,title=title)
            elif isinstance(content,dict): 
                dialog = EditElement(style="dict",title=title)
            if dialog != None:
                dialog.set_entry(entry=content)
                dialog.open()
            
    def update_category(self,category,entry,original=None):
        self.parent_screen.edited = True
        gr_index = self.parent_screen.grammar_list.index(self.grammar)
        if category.startswith('add') or category.startswith('edit'):
            if category.endswith('character') and entry!=None:
                entry = Character(**entry)
                if original!=None and original in self.grammar.opposite_characters:
                    self.grammar.opposite_characters-original
                    self.grammar.add_opp_character(entry)
                    category="opposite_characters"
                elif original!=None and original in self.grammar.characters:
                    self.grammar.characters-original
                    self.grammar.add_character(entry)
                    category="characters"
                elif category == 'add_opposite_character':
                    self.grammar.add_opp_character(entry)
                    category="opposite_characters"
                elif category == 'add_character':
                    self.grammar.add_character(entry)
                    category="characters"
                    
            elif category.endswith('sentence') and entry!=None:
                entry = Sentence(**entry)
                if original!=None and original in self.grammar.sentences: 
                    self.grammar.remove_sentence(original)
                    self.grammar.add_sentence(entry)
                    category="sentences"
                elif category == 'add_sentence':
                    self.grammar.add_sentence(entry)
                    category="sentences"
                    
        if category == 'level':
            entry = entry if entry != None else ""
            self.grammar.level = entry
        if category == 'tags':
            entry = entry if entry != None else []
            self.grammar.tags = entry
        elif category == 'title':
            entry = entry if entry != None else ""
            self.grammar.title = entry
        elif category == 'subtitle':
            entry = entry if entry != None else ""
            self.grammar.subtitle = entry
        elif category == 'explanation':
            entry = entry if entry != None else ""
            self.grammar.explanation = entry
        elif category == 'structures':
            entry = entry if entry != None else []
            self.grammar.structures = entry
        elif category == 'opposite_structures':
            entry = entry if entry != None else []
            self.grammar.opposite_structures = entry
        if self.grammar != self.parent_screen.grammar_list[gr_index]:
            kwargs = self.grammar.to_dict()
            self.parent_screen.grammar_list[gr_index].update(**kwargs)
        if category in self.ids.scroll.ids:
            self.ids.scroll.ids[category].remove_content()
            self.ids.scroll.ids[category].list_category(values=self.grammar[category])
        self.parent_screen.set_list_items()
class GrammarList(MyScreen):
    edited=BooleanProperty(False)
    grammar_list=ListProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for child in self.filter.children:
            child.toggle_off()
        self.set_up_screen()
        
    def set_up_screen(self):
        self.edited = False 
        self.grammar_list = []
        self.grammar_list = self.get_grammar_list()
        self.set_list_items()
        
    def get_grammar_list(self):
        path=os.path.join(self.get_setting('app_directory'),'grammar','grammar.jsonl')
        grammar_list = self.read_grammar_jsonl(path)
        grammar_list = list(set(grammar_list))
        def get_sorting_keys(data):
            if isinstance(data,Grammar): return (data.level.lower(),data.title.lower(),data.subtitle.lower())
            else: return ""
        grammar_list.sort(key=lambda data: get_sorting_keys(data))
        return grammar_list
    
    def read_grammar_jsonl(self,path):
        grammar_list=[]
        if os.path.isfile(path):
            with open(path,'r') as file:
                json_list = list(file)
            for json_str in json_list:
                entry=json.loads(json_str)
                grammar_entry = Grammar(**entry)
                grammar_list.append(grammar_entry)
        return grammar_list
    
    def save_grammar(self):
        self.edited=False
        gr_path_jsonl=os.path.join(self.get_setting('grammar_directory'),'grammar.jsonl')
        gr_path_txt=os.path.join(self.get_setting('grammar_directory'),'grammar.txt')
        template=self.get_setting('grammar_template')
        
        def grammar_to_jsonl(grammar:list,path):
            with open(path,'w') as outfile:
                for g in grammar:
                    if not g.is_empty():
                        json.dump(g.to_dict(), outfile, indent=None, ensure_ascii=False)
                        outfile.write('\n')
                    
        def grammar_to_txt(grammar,path,template):
            with open(path,'w') as file:
                text=[]
                for g in grammar:
                    if not g.is_empty():
                        text.append(g.to_text(template=template))
                file.write('\n'.join(text))

        grammar_to_jsonl(grammar=self.grammar_list,path=gr_path_jsonl)
        grammar_to_txt(grammar=self.grammar_list,path=gr_path_txt,template=template)
        
    def create_dataitem(self,grammar,**kwargs):
        dataitem={'grammar':grammar,'callback':lambda x:x}
        dataitem.update(grammar.to_dict())
        kwargs={k:v for k,v in kwargs.items() if v!=None}
        kwargs.update({'tags':grammar.tags.copy()})
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
            elif include==[] and dataitem['grammar'].level=="": return True
            else: return False
            
        def apply_search(dataitem):
            search_entry = self.search.text
            title = dataitem['grammar'].title.lower()
            subtitle = dataitem['grammar'].subtitle.lower()
            tags = dataitem['grammar'].tags
            if search_entry.lower() in title: return True
            elif search_entry.lower() in subtitle: return True
            elif any([search_entry.lower() in tag.lower() for tag in tags]): return True
            else: return False
        
        for gr in self.grammar_list:
            dataitem=self.create_dataitem(grammar=gr)
            if apply_filter(dataitem) and apply_search(dataitem):
                self.add_list_item(dataitem)
            
    def add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)
        
    def select_grammar(self,grammar):
        screen = ShowGrammar(name='G',grammar=grammar, parent_screen=self)
        self.add_screen(screen=screen,direction='left')
        
    def add_grammar(self):
        grammar=Grammar()
        self.grammar_list.append(grammar)
        screen = ShowGrammar(name='G',grammar=grammar, parent_screen=self)
        self.add_screen(screen=screen,direction='left')
        
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
        
        # some settings always require default (cannot be changed by user)
        default_settings=self.get_default_settings()
        if kind == 'categories':
            result = self.__dict_categories
        elif kind == 'app_directory':
            result = default_settings['app_directory']
        elif kind == 'dict_directory':
            result = default_settings['app_directory']+'dictionaries/'
        elif kind == 'image_directory':
            result = default_settings['app_directory']+'images/'
        elif kind == 'config_directory':
            result = default_settings['app_directory']+'.config/'
        elif kind == 'grammar_directory':
            result = default_settings['app_directory']+'grammar/'
        elif kind == 'dictionary_template':
            result = self._MyApp__appdata+'templates/'+default_settings['dictionary_template']
        elif kind == 'grammar_template':
            result = self._MyApp__appdata+'templates/'+default_settings['grammar_template']
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
        default_settings['app_directory'] = settings['app_directory']
        self.save_default_settings(default_settings)

        # settings directory
        user_settings_directory = self.get_setting('config_directory') 
        os.makedirs(user_settings_directory, exist_ok=True)
        
        # remove keys: they wont be saved under user settings (only default)
        remove = remove + ['access_granted','app_directory','hidden_categories','dictionary_template']
        # user settings
        settings = {k:v for k,v in settings.items() if k not in remove}
        self.dump_json(settings,user_settings_directory+"settings.json")
    
    def save_default_settings(self, settings):
        directories = ['dictionaries/','images/','grammar/']
        for d in directories:
            os.makedirs(settings['app_directory']+d,exist_ok=True)
        super().save_default_settings(settings)
            
    def copy_images(self,dest_dir,default=True):
        app_directory=self.get_setting('app_directory')
        if default: src_path=os.path.join(self.root_folder,'.images')
        else: src_path=self.get_setting('image_directory')
        dest_dir=os.path.join(app_directory,'images')
        for img in os.listdir(src_path):
            self.import_file(os.path.join(src_path,img),dest_dir,img)
    
    
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
            d_path = f'{dict_directory}/{some_dict}/{some_dict}.jsonl'
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
        
    def find_character(self,gram_link:Character):
        dict_directory=self.get_setting('dict_directory')
        linked_characters={}
        
        for some_dict in os.listdir(dict_directory):
            d_path = f'{dict_directory}/{some_dict}/{some_dict}.jsonl'
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

if __name__=="__main__":
    ChD().run()

