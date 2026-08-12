import re
import os
from pathlib import Path
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.textinput import TextInput
from kivy.metrics import dp, sp
from kivy.clock import Clock

if platform == 'android':
    from jnius import cast
    from jnius import autoclass
    from android import mActivity, api_version
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.INTERNET,
    ])
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    ActivityInfo = autoclass("android.content.pm.ActivityInfo")
    activity = PythonActivity.mActivity
    activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_USER)


from packages.chd import Dictionary, Character
from packages.chd import convert_to_dtype, convert_pronunciations
from packages.chd import load_json

from .layouts import BlockingFloatLayout
from .buttons import MultipleToggle
from .listitems import OptionItem
from .images import CenterImage
from .labels import AnchoredLabel

from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    )

from kivy.lang import Builder
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'dialogs.kv'))

def grant_permissions_external_storage():  
    if platform == "android":
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Environment = autoclass("android.os.Environment")
        Intent = autoclass("android.content.Intent")
        Settings = autoclass("android.provider.Settings")
        Uri = autoclass("android.net.Uri")
        if api_version > 29: 
            if Environment.isExternalStorageManager():
                msg="Storage access was already granted."
            else:
                try:
                    activity = mActivity.getApplicationContext()
                    uri = Uri.parse("package:" + activity.getPackageName())
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION, uri)
                    currentActivity = cast(
                    "android.app.Activity", PythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)
                    msg="Storage access is now granted."
                except:
                    intent = Intent()
                    intent.setAction(Settings.ACTION_MANAGE_ALL_FILES_ACCESS_PERMISSION)
                    currentActivity = cast(
                    "android.app.Activity", PythonActivity.mActivity
                    )
                    currentActivity.startActivityForResult(intent, 101)
                    msg="I don't know what happened."
        else:
            msg=f'This action is only for android api versions 30 and higher. This device is at {api_version}.'
    else:
        msg=f"This action is only for android devices. This device is working with {platform}."
    return msg

# = ============================================================== = #
# =                            CONTAINER                           = #
# = ============================================================== = #
    
class MakeDecision(MDBoxLayout):
    confirm_text=StringProperty('YES')
    confirm_icon=StringProperty('check')
    deny_text=StringProperty('NO')
    deny_icon=StringProperty('close')
    deny_func=ObjectProperty(None)
    accept_func=ObjectProperty(None)
    button_width=NumericProperty(350)
    
    
class DoAction(MDBoxLayout):
    text=StringProperty('ACTION')
    icon=StringProperty('info')
    action=ObjectProperty(None)
    button_width=NumericProperty(350)
    
# class MakeSimpleDecision(MDDialogButtonContainer):
class MakeSimpleDecision(MDBoxLayout):
    confirm_icon=StringProperty('check')
    deny_icon=StringProperty('close')
    deny_func=ObjectProperty()
    accept_func=ObjectProperty()
    button_width=NumericProperty(150)
    
class SimpleClose(MDBoxLayout):
    pass

class FileContent(MDBoxLayout):
    # init
    file_path=StringProperty()
    dict_name=StringProperty()
    # covered by load_file
    file_name=StringProperty()
    file_format=StringProperty()
    count=StringProperty()
    first_line=StringProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

    def set_attrs(_self, **kwargs):
        for k,v in kwargs.items():
            if v!=None: setattr(_self, k, v)

    def load_file(self,file=None,name=None):
        self.file_path = file if file!=None else self.file_path
        self.dict_name = name if name!=None else self.dict_name
        if os.path.isfile(self.file_path):
            count,first_line=0,""
            try:
                with open(self.file_path, "r") as f:
                    first_line = f.readline().strip()
                    count = sum(1 for _ in f)+1
            except:
                count=""
                first_line=""
            self.count=str(count)
            self.first_line = first_line
            if self.file_name=="": self.file_name=os.path.basename(self.file_path)
            file_path,ext = os.path.splitext(self.file_path)
            if ext!="": self.file_format=ext
class Options(MDBoxLayout):
    max_h = NumericProperty(1000)
    min_h = NumericProperty(300)
    data = ListProperty()
    item = ObjectProperty()
    is_open = BooleanProperty(True)
    selection = StringProperty()
    
    def __init__(self,data=None,**kwargs):
        super().__init__(**kwargs)
        if self.is_open: self.set_list_items(data=data)
        self.add_decision = True
            
    def set_attrs(_self, **kwargs):
        for k,v in kwargs.items():
            if v!=None: setattr(_self, k, v)
        
    def on_data(self,instance,value):
        # self.data = value
        if value not in [None,[],{}]: 
            self.set_list_items(data=value)
        
    def set_list_items(self,data):
        
        if data==None: data=[]
        elif data!=[]: self.data=data
        if not self.is_open: return None
        
        if hasattr(self,'scroll') and self.scroll!=None and len(self.scroll.children)>0: self.clear_scroll()
        
        for value in data:
            element = OptionItem(text=value,func=self.choose)
            # element = OptionItem()
            self.scroll.ids[value]=element
            self.scroll.add_widget(element)
            
    def close_options(self):
        if self.is_open:
            self.is_open = False
            for c in [c for c in self.scroll.children]:
                self.scroll.remove_widget(c)
            self.scroll.do_layout()
        else:
            self.is_open = True
            self.set_list_items(data=self.data)
            self.scroll.do_layout()
            
    def choose(self,selection):
        self.selection = selection
        
    def clear_selection(self):
        self.selection = ""
        # self.ids['input'].text = ""
        
    def update_data(self,data):
        self.data = data
        
    def clear_scroll(self):
        self.scroll.ids={}
        for c in [c for c in self.scroll.children]:
            self.scroll.remove_widget(c)
            
class ToggleOptions(Options):
    data = ObjectProperty()
    include = ListProperty()
    
    def on_include(self,instance,value):
        # self.include = value
        if self.data not in [[],{}] and self.include!=[]: 
            self.set_list_items(data=self.data,include=self.include)
        
    def set_list_items(self,data=[],include=None):
        if data==None: data=[]
        elif data!=[]: self.data=data
        if include==None: include=[]
        elif include=="all": include=data
        elif include=="none": include=[]
        
        if hasattr(self,'scroll') and self.scroll!=None:
            if len(self.scroll.children)>0: self.clear_scroll()
            self.clear_selection()

        if isinstance(data,list):
            for option in data:
                state = "on" if option in include else "off"
                self.add_item(value=option,state=state)
        elif isinstance(data,dict):
            for head,options in data.items():
                self.add_head(head)
                for option in options:
                    state = "on" if option in include else "off"
                    self.add_item(value=option,state=state)
            self.add_head('Uncategorized')
            
    def add_item(self,value,state='off'):
        element = MultipleToggle(text=value,kind='select_multiple',disabled=False)
        self.scroll.ids[value]=element
        self.scroll.add_widget(element)
        if state == "on":
            element.toggle_on()
            
    def add_head(self,text):
        from main import ChD
        app:ChD=ChD.get_running_app()
        element = AnchoredLabel(text=text,min_padding=30,md_bg_color=app.custom.colors['button_bg'],role='small',radius=app.radius,text_color=app.custom.colors['button_fg'])
        self.scroll.add_widget(element)
        
    def clear_scroll(self):
        self.scroll.ids={}
        self.clear_selection()
        # self.data = []
        # self.include = []
        # for c in [c for c in self.scroll.children]:
            # self.scroll.remove_widget(c)
        self.scroll.clear_widgets()
            
    def clear_selection(self):
        # print('clear_selection',self.scroll.include)
        self.scroll.include=[]
        self.scroll.exclude=[]

class DictOptions(Options):
    data = DictProperty()
    mode = StringProperty('value')
    del_func = ObjectProperty()
                
    def add_option(self):
        def add_category(text):
            if text!="" and text not in self.data.keys(): 
                self.data.update({text:''})

        add_key = AddOption(add_option=add_category)
        add_key.key = '___add___'
        self.scroll.add_widget(add_key)

    def set_list_items(self,data={}):
        if data==None: data={}
        elif isinstance(data,dict): self.data=data
        if data!={} and len(self.scroll.children)>0: self.clear_scroll()
        for k,v in data.items():
            self.add_item(key=k,value=v)
        if self.mode == 'del_element':
            self.add_option()
    
    def add_item(self,key,value):
        if self.mode == "value":
            element=DictValue(key=str(key),value=str(value))
        elif self.mode == "element":
            element=DictElement(key=str(key),value=str(value))
        elif self.mode == "del_element":
            element=DictElementDel(key=str(key),value=str(value),del_func=self.delete_key)
        self.scroll.ids[key]=element
        self.scroll.add_widget(element)
            
    def delete_key(self,key):

        if callable(self.del_func):
            self.del_func(key)

        for c in [c for c in self.scroll.children if c.key == key]:
            self.scroll.remove_widget(c)
            self.scroll.ids.pop(key)
            self.data.pop(key)

    def clear_scroll(self):
        self.scroll.ids={}
        # self.data = {}
        for c in [c for c in self.scroll.children]:
            self.scroll.remove_widget(c)
            
class LazyOptions(MDBoxLayout):
    itemclass = StringProperty()
    options = ListProperty()
    icons = ListProperty()
    max_h = NumericProperty(1200)
    min_h = NumericProperty(0)
    
    def __init__(self,func=None,data=None,item_args={},*args,**kwargs):
        super().__init__(*args, **kwargs)
        if self.options != []: self.set_list_items(func=func,data=data,**item_args)
    
    def set_options(self,options:list):
        self.options=options
        
    def set_attrs(_self, **kwargs):
        for k,v in kwargs.items():
            if v!=None: setattr(_self, k, v)
    
    def create_dataitem(self,text,**kwargs):
        kwargs={k:v for k,v in kwargs.items() if v!=None}
        dataitem={'text': str(text),'callback':lambda x:x}
        dataitem.update(kwargs)
        # print(dataitem.keys())
        return dataitem 
    
    def add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)
        
    def set_list_items(self,**kwargs):
        self.rv_scroll.data = []
        if self.icons == []:
            for option in self.options: 
                dataitem=self.create_dataitem(text=option,**kwargs) 
                self.add_list_item(dataitem)
        elif len(self.icons) == len(self.options):
            for option,icon in zip(self.options,self.icons):
                dataitem=self.create_dataitem(text=option,icon=icon,**kwargs)
                self.add_list_item(dataitem)

class PaletteOptions(LazyOptions):
    
    def __init__(self,*args,**kwargs):
        from pathlib import Path
        self.palette_colors = load_json(Path('appdata')/'colors'/'palette_colors.json')
        self.options = self.get_palettes()
        super().__init__(*args,**kwargs)
    
    def create_dataitem(self,text,**kwargs):
        kwargs.update(self.add_palette_colors(text))
        dataitem = super().create_dataitem(text,**kwargs)
        return dataitem
    
    def add_palette_colors(self,palette):
        d = {
            "color_onea":"primaryColor",
            "color_oneb":"primaryContainerColor",
            "color_onec":"onPrimaryColor",
            "color_oned":"onPrimaryContainerColor",
            "color_onee":"primaryFixedColor",
            "color_onef":"onPrimaryFixedColor",
            "color_oneg":"inversePrimaryColor",
            
            "color_twoa":"secondaryColor",
            "color_twob":"secondaryContainerColor",
            "color_twoc":"onSecondaryColor",
            "color_twod":"onSecondaryContainerColor",
            "color_twoe":"secondaryFixedColor",
            "color_twof":"onSecondaryFixedColor",
            
            "color_trea":"tertiaryColor",
            "color_treb":"tertiaryContainerColor",
            "color_trec":"onTertiaryColor",
            "color_tred":"onTertiaryContainerColor",
            "color_tree":"tertiaryFixedColor",
            "color_tref":"onTertiaryFixedColor",
        }
        
        updatedict = {color:self.get_color(palette,colorname) for color,colorname in d.items()}
        return updatedict
        
    def get_color(self,name,color_name):
        return self.palette_colors[self.theme_cls.theme_style][name.capitalize()][color_name]
    
    def get_palettes(self):
        from kivy.utils import hex_colormap
        all_colors=[palette.capitalize() for palette in hex_colormap.keys()]
        # from kivy.utils import hex_colormap
        from main import APP_DIR
        with open(APP_DIR/'appdata'/'colors'/'palette_colors.txt','r') as f:
            colors=[l.strip('\n') for l in f.readlines()]
        colors = [c for c in colors if '#' not in c]
        return colors

class DictValue(MDBoxLayout):
    key=StringProperty()
    value=StringProperty()
    
class DictElement(MDBoxLayout):
    key=StringProperty()
    value=StringProperty()
    
class DictElementDel(DictElement):
    del_func=ObjectProperty()
    
    def delete(self):
        
        if callable(self.del_func):
            success = self.del_func(self.key)

class AddOption(MDBoxLayout):

    def __init__(self, add_option=None, *args, **kwargs):
        if add_option!=None: self.add_option=add_option
        super().__init__(*args, **kwargs)
    
    def add_option(self,text):
        pass
    
class AddProperty(MDBoxLayout):
    add_func=ObjectProperty()
    
    def __init__(self, add_property=None, *args, **kwargs):
        if add_property!=None: self.add_property=add_property
        super().__init__(*args, **kwargs)
    def add_property(self,key,value):
        if callable(self.add_func):
            success = self.add_func(key,value)
            if success: 
                self.ids['key'].text = ""
                self.ids['value'].text = ""
                
class ElementInput(TextInput):
    max_h=NumericProperty(1000)
    min_h=NumericProperty(300)
    mode=StringProperty()
    
    def clear(self):
        self.text = ""

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[1] in ('enter', 'numpadenter') and self.mode=='bullet':
            cursor_pos = self.cursor_index()
            before_cursor = self.text[:cursor_pos]
            after_cursor = self.text[cursor_pos:]
            bullet_string = "\n- "
            new_index = cursor_pos + len(bullet_string)
            self.cursor = self.get_cursor_from_index(new_index)
            self.text = before_cursor + bullet_string + after_cursor
            return True

        return super().keyboard_on_key_down(window, keycode, text, modifiers)    

# = ============================================================== = #
# =                             DIALOGS                            = #
# = ============================================================== = #

class CustomDialog(BlockingFloatLayout):
    decision = ObjectProperty()
    add_decision=BooleanProperty(False)
    title=StringProperty()
    support_text=StringProperty()
    dialog_width=ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        
    def set_attrs(_self, **kwargs):
        for k,v in kwargs.items():
            setattr(_self, k, v)
    
    def on_add_decision(self,instance,value):
        if value and hasattr(self,'decision') and self.decision!=None:
            decision=SimpleClose()
            if len(self.decision.children)>0: self.decision.clear_widgets()
            self.decision.add_widget(decision)
                
    def deny_func(self):
        pass
    def accept_func(self):
        pass
       
    def open(self):
        from main import ChD
        app = ChD.get_running_app()
        app.open_dialog(self)
        
    def dismiss(self):
        from main import ChD
        app = ChD.get_running_app()
        app.dismiss_dialog()
        
class ConfirmDecision(CustomDialog):
    name=StringProperty()
    direction=StringProperty('left')
    confirm_text=StringProperty('Yes')
    deny_text=StringProperty('No')
    support_text=StringProperty('')
    
    def __init__(self,what=None,do_choice=True,accept_func=None,deny_func=None,*args,**kwargs):
        if not do_choice: 
            self.confirm_text=""
            self.deny_text=""
            
        super().__init__(*args,**kwargs)

        self.choose_action(what=what,do_choice=do_choice,accept_func=accept_func,deny_func=deny_func)
        
    def choose_action(self,what=None,do_choice=True,accept_func=None,deny_func=None):
        decision_map={
            'delete_dictionary':[self.delete_dictionary,self.do_nothing],
            'delete_character':[self.delete_character,self.do_nothing],
            'export_character':[self.export_character,self.do_nothing],
            'save_dict_edit':[self.save_dict_changes,self.continue_to_next_screen],
            'save_gram_edit':[self.save_gram_changes,self.continue_to_next_screen],
            'access':[self.permissions_external_storage,self.permission_denied],
        }
        
        if not do_choice: 
            self.confirm_text=""
            self.deny_text=""
            
        if what!=None and what in decision_map: 
            self.accept_func=decision_map[what][0]
            self.deny_func=decision_map[what][1]
        if accept_func != None: self.accept_func = accept_func
        if deny_func != None: self.deny_func = deny_func
        
        if len(self.decision.children) > 0: self.decision.clear_widgets()
        if do_choice:
            decision=MakeDecision(button_width=365,
                confirm_text=self.confirm_text,deny_text=self.deny_text,
                deny_func=self.deny_func,accept_func=self.accept_func)
            self.decision.add_widget(decision)     
        else:
            self.add_decision=True

    def do_nothing(self):
        pass
    
    # = ––––––––––––––––––––––––––– delete ––––––––––––––––––––––––––– = #
    
    def delete_dictionary(self):
        from main import ChD
        app=ChD .get_running_app()
        file = self.name
        dict_directory = app.get_setting('dict_directory')
        if os.path.isdir(dict_directory):
            if file in os.listdir(dict_directory):
                import shutil
                shutil.rmtree(dict_directory/file)        
                app.previous_screen()
                if hasattr(app.wm.current_screen,'set_files'):
                    app.wm.current_screen.set_files()
                
    def delete_character(self):
        from main import ChD
        app=ChD.get_running_app()
        character = app.wm.current_screen.character
        # app.switch_screen("view_dict",'right')
        app.previous_screen()
        current_screen = app.wm.current_screen
        if character in current_screen.dictionary:
            current_screen.edited = True
            current_screen.dictionary = current_screen.dictionary - character
            current_screen.set_list_items(update_images=False)
            
    # = ––––––––––––––––––––––––– export/save –––––––––––––––––––––––– = #
            
    def export_character(self):
        from main import ChD
        app = ChD.get_running_app()
        if hasattr(self,'template'):
            current_screen = app.wm.current_screen
            file=current_screen.character.unicode_unique_string
            d=Dictionary(name=file,characters=[current_screen.character])
            dict_directory = app.get_setting('dict_directory')
            directory=dict_directory/f'{current_screen.parent_dictionary.name}'
            print(self.template,d)
            d.write(directory=directory,filename=file,file_format='pleco',template=self.template)
            # AttentionMsg(attention='File was created',msg=f'The character {current_screen.character} was stored in {directory}{file}.txt').open()
    
    # = –––––––––––––––––––––––––– save_edit ––––––––––––––––––––––––– = #
    
    def save_gram_changes(self):
        from main import ChD
        app = ChD.get_running_app()
        app.wm.current_screen.save_grammar()
        self.continue_to_next_screen()
        
    def save_dict_changes(self):
        from main import ChD
        app = ChD.get_running_app()
        app.wm.current_screen.save_dictionary(make_msg=False)
        self.continue_to_next_screen()
        
    def continue_to_next_screen(self):
        from main import ChD
        app = ChD.get_running_app()
        app.wm.current_screen.edited=False
        app.switch_screen(screen_name=self.screen_name, direction=self.direction, remember=self.remember,force=True)

    # = ––––––––––––––––––––––––––– access ––––––––––––––––––––––––––– = #

    def permissions_external_storage(self):  
        from main import ChD
        msg=grant_permissions_external_storage()
        app=ChD.get_running_app()
        app._MyApp__decide_on_app_directory()
        # print(msg)
    
    def permission_denied(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        app.change_app_directory(app.root_folder)
        app.wm.get_screen('settings').update_settings()

class ConfirmExport(ConfirmDecision):
    pass
class ConfirmDelete(ConfirmDecision):
    pass
class ConfirmUnsaved(ConfirmDecision):
    pass
class GrantAccess(ConfirmDecision):
    pass

class ChooseAppDirectory(CustomDialog):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from packages.screens.settings import Setting
        content=Setting(setting='app_directory',hint='App Directory',icon='folder-open',padding=[0,0,0,40])
        content.press_button=content.select_directory
        content.text = ""
        decision=MakeSimpleDecision(deny_func=self.deny_func,accept_func=self.accept_func)
        self.content.ids['app_directory']=content
        self.content.add_widget(content)
        self.decision.add_widget(decision)

    def save_app_dir(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        app_directory = self.content.ids.app_directory.text
        if os.path.exists(app_directory):
            app.change_app_directory(app_directory)
            app.wm.get_screen('settings').update_settings()
            self.dismiss()
    
    def save_default_app_dir(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        app.change_app_directory(app.root_folder)
        app.wm.get_screen('settings').update_settings()
        self.dismiss()
        
class ShowPaletteOptions(CustomDialog):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args)
        content=PaletteOptions(**kwargs)
        self.content.add_widget(content)    
        self.add_decision = True

class ShowOptions(CustomDialog):
    
    def __init__(self,title="",support_text="",allow_add=False,*args,**kwargs):
        self.title=title
        self.support_text=support_text
        super().__init__(title=title,support_text=support_text)
        content=LazyOptions(**kwargs)
        self.content.add_widget(content)    
        self.content.ids['options']=content
        if allow_add: self.content.add_widget(AddOption(add_option=self.add_option))
        self.add_decision = True
        
    def add_option(self,text):
        options = self.content.ids['options']
        if text!="" and text not in options.options: 
            options.set_options(options.options+[text])
            options.set_list_items()
            
    def list_options(self,options=[],itemclass=None,title=None,support_text=None,**kwargs):
        self.title = title if title!=None else self.title
        self.support_text = support_text if support_text!=None else self.support_text
        self.content.ids['options'].set_attrs(options=options,itemclass=itemclass)
        self.content.ids['options'].set_list_items(**kwargs)

class ConfirmFileChoice(CustomDialog):
    def __init__(self,deny_func=None,accept_func=None,*args,**kwargs):
        super().__init__(*args)
        content=FileContent(**kwargs)
        self.content.add_widget(content)    
        self.choose_action(deny_func=deny_func,accept_func=accept_func)   
        
    def choose_action(self,deny_func=None,accept_func=None):
        if len(self.decision.children)>0: self.decision.clear_widgets()
        decision=MakeSimpleDecision(deny_func=deny_func,accept_func=accept_func)
        self.decision.add_widget(decision)
        
    def load_file(self,file=None,name=None):
        self.content.children[0].load_file(file=file,name=name)
        
class ShowImage(CustomDialog):
    
    def __init__(self,source="",title="",image_size=[100,100],*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.choose_image(source=source,title=title,image_size=image_size)
        
    def choose_image(self,source:str="",title:str="",image_size:list=[100,100]):
        self.title = title.replace('_',' ').title()
        delete_source = lambda: self.delete_image(source)
        decision=DoAction(button_width=365,icon='delete',text='Delete',action=delete_source)
        content=CenterImage(source=source,image_size=image_size)
        if len(self.content.children)>0: self.content.clear_widgets()
        if len(self.decision.children)>0: self.decision.clear_widgets()
        self.content.add_widget(content)    
        self.decision.add_widget(decision)
        
    def delete_image(self,source):
        from main import ChD
        app:ChD=ChD.get_running_app()
        app.remove_file(source)
        
    def do_sth(self):
        print('do_sth')
        
class EditElement(CustomDialog):
    allow_multiple=BooleanProperty()
    dtype=ObjectProperty()
    original=ObjectProperty()
    style=StringProperty()
    
    def __init__(self,style='',options=[],**kwargs):
        super().__init__(**kwargs)
        
        self.content_options = {
            'normal' : ElementInput(),
            # 'list' : ElementInput(),
            'custom' : ToggleOptions(max_h=1210),
            'dict' : DictOptions(mode='element')
        }
        if style != '': self.choose_content(style=style,options=options)
        decision=MakeSimpleDecision(deny_func=None,accept_func=self.confirm_edit)
        self.decision.add_widget(decision)
    
    def choose_content(self,style="",mode=None,options=[],**kwargs):
        self.set_attrs(**kwargs)
        self.style=style
        if style in ['normal','custom','dict']:
            if len(self.content.children)>0: self.content.clear_widgets()
            if style=="normal": 
                content = self.content_options[style]
                if mode!=None: content.mode = mode
                self.content.ids['input']=content
                self.content.add_widget(content)
            elif style=="custom":
                self.options=options if options!=None else []
                content = self.content_options[style]
                content.set_attrs(data=options)
                content.clear_selection()
                self.content.ids['custom']=content
                self.content.add_widget(content)
            elif style=="dict":
                content = self.content_options[style]
                if mode!=None: content.mode = mode
                self.content.ids['options']=content
                self.content.add_widget(content)
    
    def set_entry(self,entry):
        if self.style=="custom" and not isinstance(entry,str): 
            options = self.content.ids.custom
            missing_entry = [e for e in entry if e not in options.scroll.ids]
            for e in options.scroll.ids:
                if e in entry: options.scroll.ids[e].toggle_on()
                else: options.scroll.ids[e].toggle_off()
            if missing_entry!=[]:
                # options.add_head('Uncategorized')
                for e in missing_entry:
                    options.add_item(e,state='on')
            # print('\n\nset_entry',
            #     options.scroll.include,
            #     )
        elif isinstance(entry,list): self.content.ids.input.text='- '+'\n- '.join(entry)
        elif isinstance(entry,dict): self.content.ids['options'].set_attrs(data=entry)
        elif isinstance(entry,str): self.content.ids.input.text = re.sub(r'[■|●|□|○|◼]','■',entry)
        else: self.content.ids.input.text=str(entry) if entry!=None else ""
        
    def get_dict(self):
        entry = {k:element.input.text.strip(" ") for k,element in self.content.ids['options'].scroll.ids.items()}
        entry = {k:v for k,v in entry.items() if v!=""}
        entry = "" if entry == {} else entry
        entry = None if entry == {} else entry
        return entry
    
    def get_custom(self):
        active = self.content.ids.custom.scroll.include
        # print('get_custom',active)
        return active
    
    def get_input(self,category, convert_pronunciation=True,new_line=True):
        from main import ChD
        app=ChD.get_running_app()
        dict_categories = app.get_setting('categories')
                
        text = self.content.ids.input.text
        if convert_pronunciation: text = convert_pronunciations(text)
        
        def allows_multiple():
            if category == 'new_character': return True
            elif category in dict_categories.keys():
                if dict_categories[category]==list: return True
                else: return False
            elif self.allow_multiple: return True
            else: return False
            
        def get_default_dtype():
            if category == 'new_character': return list
            elif category in dict_categories: return dict_categories[category]
            elif self.dtype != None: return self.dtype
            else: return str
        
        if allows_multiple():
            # only new point when new line
            # relevant if text contains '-'
            if new_line==True: 
                text = text.lstrip('-').split('\n-')
                new_entry = [e.replace('\n',' ').strip(' ') for e in text]
                new_entry = [e for e in text if e != '' and not e.isspace()]
            elif new_line==False:
                text = text.replace('\n',' ').lstrip('-').split('-')
                new_entry = [e.strip(' ') for e in text]
                new_entry = [e for e in text if e != '' and not e.isspace()]

        else:
            new_entry = text.lstrip('-').strip(' ')
            if new_line==False:
                new_line.replace('\n',' ')
            new_entry=convert_to_dtype(new_entry)
            
        if new_entry not in ["",[""],[]]:
            dt = get_default_dtype()
            if type(new_entry) != dt:
                try:
                    new_entry=dt(new_entry)
                except:
                    new_entry=None
            return new_entry
        else:
            return ''
    
    def confirm_edit(self):
        from main import ChD
        app=ChD.get_running_app()
        self.screen=app.wm.current_screen #possible: ViewDict, ShowCharacter
        
        if self.title != 'Character': self.__category_edit()
        elif self.title == 'Character': self.__character_edit()
                    
    def __character_edit(self):
        new_entry = self.get_dict()
        if new_entry!=None:
            category='new_character'
            character = {k:'' for k in Character().to_dict()}
            character.update(new_entry)

            if self.screen.name == 'view_dict':
                self.screen.add_character(entries=character)
            elif self.screen.name.startswith('C'):
                self.screen.update_character(entries=character)
                
    def __category_edit(self):
        category=self.title.lower().replace(' ','_')
        if self.style=="custom": new_entry = self.get_custom()
        elif 'input' in self.content.ids: new_entry = self.get_input(category,convert_pronunciation=True,new_line=True)
        else: new_entry=self.get_dict()
        
        if category == 'dictionary_name': self.screen.rename_dict(new_entry)
        else:
            if new_entry == None:
                pass
            elif new_entry != None: 
                if new_entry == "": new_entry = None
                self.screen.update_category(category=category,entry=new_entry,original=self.original)
        