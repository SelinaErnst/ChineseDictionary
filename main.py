import json
from pathlib import Path
import os
from plyer import filechooser
from packages.pleco import dictionary, decode_pinyin
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
# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #

from packages.screens import (
    SelectFile, NameDict,
    DictFileChooser, 
    DictDirChooser,
    ViewDict,
    Settings,
    )

from packages.kivymd_templates import (
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
)

from kivy.lang import Builder
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase
from packages.kivymd_templates import print_class

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# print_class('MDButtonIcon',search='theme')

print('main')

KV="""
<ShowCharacter>:
    bottom_nav: bottom_nav

    MDStackLayout:
        
        MDBoxLayout:
            adaptive_height: True
            orientation: 'horizontal'
            md_bg_color: app.theme_cls.surfaceBrightColor
            padding: 20,20,20,20
            spacing: 20
            MDStackLayout:
                adaptive_height: True
                # md_bg_color: 'green'
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_height: True
                    spacing: 10
                    MultiLineLabel:
                        id: simple
                        text: root.get_property('simple')
                        label_bg_color: app.theme_cls.onPrimaryContainerColor
                        text_color: app.theme_cls.onPrimaryColor
                        role: 'medium'
                        font_style: "Title"
                    MultiLineLabel:
                        id: traditional
                        text: root.get_property('traditional')
                        label_bg_color: app.theme_cls.onPrimaryContainerColor
                        text_color: app.theme_cls.onPrimaryColor
                        role: 'medium'
                        font_style: "Title"
                Separator:
                MDBoxLayout:
                    orientation: 'horizontal'
                    adaptive_height: True
                    MDBoxLayout:
                        size_hint: None,None
                        size: 0,root.default_height
                    MultiLineLabel:
                        id: pronunciation
                        text: root.character.show_pinyin()
                        role: 'medium'
                        font_style: "Label"
                        label_padding: 20,12,0,12
            MDAnchorLayout:
                anchor_y: 'bottom'
                anchor_x: 'right'
                size_hint_x: None
                width: edit.size[0]
                MDStackLayout:
                    size_hint: None, None
                    width: edit.size[0]
                    height: 2*edit.size[0]+20
                    MyIconButton:
                        id: edit
                        size: root.default_height, root.default_height
                        icon: 'pencil'
                        style: 'text'
                        on_release:  root.edit_character()
                    Separator:
                    MyIconButton:
                        size: edit.size
                        icon: 'plus'
                        style: 'text'
                        on_release: root.select_new_category()
        ScrollView:
            MDStackLayout:
                id: scroll
                size_hint: 1, None
                height: self.minimum_height+(66+2*10)*2
                padding: 20
                spacing: 20
                
                
    MDBottomSheet:
        id: bottom_nav
        size_hint_y: None
        height: 170
        sheet_type: "modal"

        BottomSheetDragHandleContainer:
            padding: 20
            adaptive_height: True
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
                        text: 'Export'
                        icon: 'auto-upload'
                        style: 'text'
                        size: self.parent.height, self.parent.height
                        on_release:
                            root.export_character()
                            bottom_nav.set_state("toggle")
                    MyIconButton:
                        text: 'Upload Image'
                        icon: 'image-search'
                        style: 'text'
                        size: self.parent.height, self.parent.height
                        on_release: 
                            root.choose_png_file()
                            bottom_nav.set_state("toggle")
                    MyIconButton:
                        text: 'Delete'
                        icon: 'delete'
                        style: 'text'
                        size: self.parent.height, self.parent.height
                        on_release: 
                            current_screen = app.switch_screen('viewdict','right')
                            current_screen.del_character(root.character)
                     
<MyList>:
    orientation: 'horizontal'
    adaptive_height: True
<Head>:
    role: 'small'
    label_bg_color: self.theme_cls.onPrimaryContainerColor
    text_color: self.theme_cls.onPrimaryColor
    font_name: "Roboto"
    bold: True
    on_release: app.wm.current_screen.edit_property(root.text)
<Bullets>:
    adaptive_height: True          
<ListElement>:
    label_padding: 25,10,20,10
    label_width: self.width-35
    anchor_x: 'right'
    anchor_y: 'top'
    # md_bg_color: 'red'
    role: 'small'
    label_bg_color: app.theme_cls.surfaceDimColor
    MDAnchorLayout:
        md_bg_color:[0,0,0,0]
        padding: 23,20,0,0
        anchor_x: 'left'
        anchor_y: 'top'
        MDRelativeLayout:
            md_bg_color: app.theme_cls.onPrimaryContainerColor
            size_hint: None,None
            size: 20,20
"""


class ListElement(MultiLineLabel):
    pass
class Head(ButtonBehavior, MultiLineLabel):
    pass

class Bullets(MDStackLayout):

    def create_bullets(self,results,font_name='CH'):
        for r in results:
            label=ListElement(text=str(r), font_name=font_name, size_hint=[1,None])
            self.add_widget(label)
    
    def remove_bullets(self):
        self.clear_widgets()

class MyList(MDBoxLayout):
    prop=StringProperty()
    translations=ListProperty()
    bullets=ObjectProperty()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        head_text=self.prop.replace('_',' ').capitalize()
        head_label=Head(text=head_text)
        head = MDAnchorLayout(anchor_y='top', anchor_x="left", size_hint_x=None, width=320)
        head.add_widget(head_label)
        font_name = 'CH' if self.prop.lower()!='german' else 'Roboto'
        self.bullets=Bullets()
        self.bullets.create_bullets(results=self.translations)
        self.add_widget(head)
        # self.children[0].add_widget(head_label)
        self.add_widget(self.bullets)

class ShowCharacter(MyScreen):
    parent_dictionary=ObjectProperty(None)
    character=ObjectProperty()
    dict_screen=ObjectProperty(None)
    categories=ListProperty()
    head_categories=['simple','traditional','pronunciation']
    not_listed_categories=['strokes','ancient','images','image_urls']
    default_height=78
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.build_scroll()
    
    def build_scroll(self):
        self.resize_head()
        for category in self.character.get_existing_categories():
            if category not in self.not_listed_categories \
                and category not in self.head_categories:
                    self.list_translations(category)
        
    def clean_scroll(self):
        for c in [c for c in self.ids.scroll.children]:
            c.clear_widgets()
    
    def update_character(self):
        for category in self.head_categories:
            if category in self.ids:
                if category == 'pronunciation':
                    # text=decode_pinyin(self.character.get_property(category))
                    text=self.character.show_pinyin()
                else:
                    text=self.character.get_property(category)
                self.ids[category].label.text = text
        if self.dict_screen != None:
            self.dict_screen.set_list_items()
            
    def resize_head(self):  
        for key in self.head_categories:
            if self.character.get_property(key) == "":
                self.ids[key].ids.label.height=self.default_height
                
    def list_translations(self,prop,translations=None):
        translations=self.character.get_property(prop) if translations==None else translations
        if  translations != None and prop not in self.categories:
            self.categories.append(prop)
            translations=translations if isinstance(translations,list) else [translations]
            l=MyList(prop=prop,translations=translations)
            self.ids.scroll.add_widget(l)
            self.ids.scroll.ids[prop]=l
        else:
            pass
        
    def remove_translations(self,prop):
        if prop in self.ids.scroll.ids:
            self.categories.remove(prop)
            self.ids.scroll.remove_widget(self.ids.scroll.ids[prop])
              
    def get_property(self,prop):
        if self.character != None:
            existing = self.character.get_existing_categories()
            if prop in existing:
                return self.character.get_property(prop)
    
    def edit_property(self,category):
        title=category
        category=category.lower().replace(' ','_')
        allow_multiple=self.character.allows_multiple(category)
        if allow_multiple: support_text=f"Using '-' and a new line indicates a new bullet point."
        else: support_text="Information about the character can be edited here."
        kwargs={
            "title":title,
            "support_text":support_text,
        }
        entry = self.character.get_property(category)
        if hasattr(self,'dialog'): self.dialog.dismiss()
        self.dialog = AddElement(**kwargs)
        self.dialog.allow_multiple = allow_multiple
        # print(entry, self.character.info())
        if isinstance(entry,list):
            self.dialog.ids.input.text='- '+'\n- '.join(entry)
        else:
            self.dialog.ids.input.text=str(entry) if entry!=None else ""
        self.dialog.open()
    
    def edit_character(self):
        kwargs={
            "title":'Character',
            "support_text":f"'-' separates these categories: simple, traditional, pronunciation",
        }
        entries=[]
        for category in self.head_categories:
            entries += [self.character.get_property(category)]
        self.dialog = AddElement(**kwargs)
        self.dialog.ids.input.text='- '+'\n- '.join(entries)
        self.dialog.open()
        
    def select_new_category(self):
        missing_categories=[cat for cat in self.character.get_missing_categories() if cat not in self.not_listed_categories]
        hidden_categories=[cat for cat in self.character.get_existing_categories() if cat in self.not_listed_categories]
        kwargs={
            "title":"Select the category",
            'support_text':"The categories shown here will contain information about the character. By selecting one of them, a new entry can be given.",
            "options":missing_categories+hidden_categories,
            "itemclass":"CategoryItem",
            "list_height":500
        }
                   
        self.dialog = ShowOptions(**kwargs) 
        self.dialog.open()
        
    def choose_png_file(self):
        from kivymd.uix.filemanager import MDFileManager
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            ext=[".png"], 
        )
        self.open_file_manager()
        
    def open_file_manager(self):
        if platform == 'android':
            from android.storage import primary_external_storage_path
            directory=primary_external_storage_path()
        else:
            directory=os.path.expanduser("~")
        self.file_manager.show(directory)
        self.manager_open = True
        
    def select_path(self, path):
        self.exit_manager()
        from main import SCRIPT_DIR
        file_name = f'{self.character.unicode_unique_string()}.png'
        directory=SCRIPT_DIR/'character_images'/'ancient_characters'
        if self.move_and_rename_file(src_path=path,dest_dir=directory,new_name=file_name):
            kwargs={'ancient_image':os.path.join(str(directory), file_name)}
            self.character.update_images(kwargs)
        
    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()
        
    def move_and_rename_file(self,src_path, dest_dir, new_name):
        dest_path = os.path.join(str(dest_dir), new_name)
        try:
            import shutil
            shutil.move(src_path, dest_path)
            AttentionMsg(attention='Image was uploaded',msg=f'Ancient image was defined as {dest_path}, based on {src_path}').open()
            return True
        except Exception as err:
            # error=f"{type(err).__name__}"
            ErrorMsg(error='Image was not uploaded',msg=str(err)).open()
            return False
        
    def export_character(self):
        from main import ChD
        app = ChD.get_running_app()
        file=self.character.unicode_unique_string()
        d=dictionary(file,characters=[self.character])
        dict_directory = app.get_setting('dict_directory')
        directory=dict_directory+f'{self.parent_dictionary.name}/'
        d.write(directory=directory,filename=f'{file}.txt',file_format='pleco')
        AttentionMsg(attention='File was created',msg=f'The character {self.character} was stored in {directory}{file}.txt').open()
        
def load_json(path, default_dir=SCRIPT_DIR):
    path=path if default_dir==None else Path(default_dir)/path
    with open(path, "r") as f:
        settings = json.load(f)
    return settings

def dump_json(data,path, default_dir=SCRIPT_DIR):
    path=path if default_dir==None else Path(default_dir)/path
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return True
    
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
        root_folder = Path(self.directory)
        self.root_folder = str(root_folder.resolve())+'/'
        resource_add_path(root_folder/"appdata"/"fonts")
        
        my_examples=load_json(self.root_folder+'appdata/defaults/my_directories.json')
        self.import_dir_example=my_examples['import_directory'][platform]
        self.app_dir_example=my_examples['app_directory'][platform]
        self.choose_settings()
        
        self.load_all_kv_files(str(root_folder/'screens'))
        Builder.load_string(KV)
    
    def build(self):
        default=False
        screens = [
            Home(name="home"),
            Settings(name='settings',settings=self.settings),
            SelectFile(name="selectfile", default=default),
            NameDict(name='namedict'),
            DictFileChooser(name="filechooser"),
            DictDirChooser(name='selectdict'),
            ViewDict(name="viewdict", default=default),
        ]
        interface = Interface()
        self.add_window_manager(interface.wm)
        for screen in screens:
            self.wm.add_widget(screen)
        if not os.path.isdir(self.get_setting('app_directory')):
            self.switch_screen('settings','left')
        return interface
    
    def on_start(self):
        if not self.settings['access_granted']:
            # print(not self.settings['access_granted'])
            self._show_validation_dialog()
        else:
            self.has_access = True

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
        
    
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
            elif kind == 'dict_directory':
                try:
                    return settings['app_directory']+'dictionaries/'
                except:
                    return settings['app_directory'][platform]+'dictionaries/'
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
            my_default_settings=load_json('appdata/defaults/default_settings.json')
            device_default_settings={k:v if not isinstance(v,dict) else v[platform] for k,v in my_default_settings.items()}
            self.save_default_settings(default_settings=device_default_settings,update=True)
        try:
            self.load_settings()
        except Exception as err:
            print("load_settings", err)
        
        
        self.theme_cls.theme_style = self.get_setting('theme_style')
        self.theme_cls.primary_palette = self.get_setting('palette')
        self.dict_dir=self.get_setting('import_directory')
        # LabelBase.register(name="CH", fn_regular=self.get_setting('chinese_font_file'))
        LabelBase.register(name="CH", fn_regular='Source Han Sans CN Normal.otf')
        
    def get_palette_colors(self,style=None,palette=None):
        palette_colors = load_json('appdata/colors/palette_colors.json')
        return palette_colors
    
    def delete_dictionary(self,name):
        dict_directory = self.get_setting('dict_directory')
        if os.path.isdir(dict_directory):
            if name in os.listdir(dict_directory):
                import shutil
                shutil.rmtree(dict_directory+name)        
            else:
                ErrorMsg(error='Cannot delete',msg=f"The dictionary {name} cannot be found in the directory {dict_directory}.").open()

if __name__=="__main__":
    ChD().run()

