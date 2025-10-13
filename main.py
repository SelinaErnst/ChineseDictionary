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
# = –––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––– = #

from packages.screens import (
    SelectFile, 
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
    ScreenManager,
    MDSnackbar,
    MultiLineLabel
)

from kivy.lang import Builder
from kivy.resources import resource_add_path
from kivy.core.text import LabelBase
from packages.kivymd_templates import print_class
print_class('MDLabel',search='theme')

KV="""
<ShowCharacter>:
    MDStackLayout:
        
        MDStackLayout:
            padding: 20,20,20,0
            spacing: 20
            adaptive_height: True
            md_bg_color: app.theme_cls.surfaceBrightColor
            MDBoxLayout:
                orientation: 'horizontal'
                adaptive_height: True
                spacing: 20
                MultiLineLabel:
                    id: simple
                    padding: 20,0,20,0
                    text: root.get_property('simple')
                    label_bg_color: app.theme_cls.onPrimaryContainerColor
                    text_color: app.theme_cls.onPrimaryColor
                    role: 'medium'
                MultiLineLabel:
                    id: traditional
                    padding: 20,0,20,0
                    text: root.get_property('traditional')
                    label_bg_color: app.theme_cls.onPrimaryContainerColor
                    text_color: app.theme_cls.onPrimaryColor
                    role: 'medium'
            MultiLineLabel:
                id: pronounciation
                padding: 20,0,20,0
                text: root.get_property('pronounciation')
                theme_font_size: 'Custom'
                font_size: 7
        ScrollView:
            MDStackLayout:
                # cols: 2
                id: scroll
                size_hint: 1, None
                height: self.minimum_height+(66+2*10)*2
                padding: 20

<MyList>:
    orientation: 'lr-tb'
    adaptive_height: True
<Head>:
    role: 'small'
    label_bg_color: self.theme_cls.onPrimaryContainerColor
    text_color: self.theme_cls.onPrimaryColor
    size_hint_x: None
    width: 370
<Bullets>:
    adaptive_height: True          
<ListElement>:
    label_padding: 20,10,20,10
    label_width: self.width-200
    anchor_x: 'right'
    anchor_y: 'top'
    # md_bg_color: 'red'
    role: 'small'
    label_bg_color: app.theme_cls.surfaceDimColor
    MDAnchorLayout:
        md_bg_color:[0,0,0,0]
        padding: 150,30,0,0
        anchor_x: 'left'
        anchor_y: 'top'
        MDRelativeLayout:
            md_bg_color: app.theme_cls.onPrimaryContainerColor
            size_hint: None,None
            size: 20,20


"""



class ListElement(MultiLineLabel):
    pass
class Head(MultiLineLabel):
    pass

class Bullets(MDStackLayout):

    def create_bullets(self,results,font_name):
        for r in results:
            label=ListElement(text=str(r), font_name=font_name, size_hint=[1,None])
            self.add_widget(label)

class MyList(MDStackLayout):
    prop=StringProperty()
    translations=ListProperty()
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        head_text=self.prop.replace('_',' ').upper()
        head=Head(text=head_text)
        font_name = 'CH' if self.prop.lower()!='german' else 'Roboto'
        bullets=Bullets()
        bullets.create_bullets(results=self.translations,font_name=font_name)
        self.add_widget(head)
        self.add_widget(bullets)
class ShowCharacter(MyScreen):
    character=ObjectProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.build_scroll()
    
    def build_scroll(self):
        self.resize_head()
        # self.clean_scroll()
        self.list_translations('english')
        self.list_translations('german')
        self.list_translations('measure_word')
        self.list_translations('radical')
        self.list_translations('opposite')
        self.list_translations('strokes_count')
        self.list_translations('classifier')
        self.list_translations('variants')
        self.list_translations('relatives')
        self.list_translations('words')
        self.list_translations('others')
        self.list_translations('dict_entries')
        self.list_translations('components')
        self.list_translations('mneomics')
        self.list_translations('usage')
        self.list_translations('ancient')
        self.list_translations('link')
        self.list_translations('origin')
        
    def clean_scroll(self):
        for c in [c for c in self.ids.scroll.children]:
            c.clear_widgets()
            
    def get_property(self,prop):
        if self.character != None:
            existing = self.character.get_existing_categories()
            if prop in existing:
                return self.character.get_property(prop)
    
    def list_translations(self,prop):
        if self.character.get_property(prop) != None:
            translations=self.character.get_property(prop)
            translations=translations if isinstance(translations,list) else [translations]
            l=MyList(prop=prop,translations=translations)
            self.ids.scroll.add_widget(l)
        else:
            pass
            
    def resize_head(self):
        for key in ['simple','traditional']:
            if self.character.get_property(key) == "":
                self.ids[key].ids.label.height=71
                

                
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
    

class ChD(MyApp):
    window_size_myphone= (1080, 2114)
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
        default=True
        screens = [
            Home(name="home"),
            Settings(name='settings',settings=self.settings),
            SelectFile(name="selectfile", default=default),
            DictFileChooser(name="filechooser"),
            DictDirChooser(name='selectdict'),
            ViewDict(name="viewdict", default=default),
        ]
        interface = Interface()
        self.add_window_manager(interface.wm)
        # print(self.wm)    
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
        
    def get_theme_colors(self,style=None,palette=None):
        if style==None: style = self.theme_cls.theme_style
        if palette==None: palette = self.theme_cls.primary_palette
        palette_colors = load_json(self.directory+'/appdata/colors/palette_colors.json')
        return palette_colors[style][palette]
       
if __name__=="__main__":
    ChD().run()

