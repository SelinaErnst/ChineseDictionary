from kivymd.uix.dialog.dialog import MDDialog, MDDialogButtonContainer
from kivy.utils import platform
from packages.chd import Dictionary
from packages.chd import convert_to_dtype, convert_pronunciations
from packages.chd import load_json
import re
from .snackbars import ErrorMsg, AttentionMsg
from .layouts import BlockingFloatLayout
from .buttons import MultipleToggle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.uix.textinput import TextInput
from .images import ImageBox, CenterImage

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

from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    ColorProperty,
    )



from kivy.lang import Builder
import os
from pathlib import Path
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
    file_path=StringProperty()
    file_name=StringProperty()
    
    file_format=StringProperty()
    dict_name=StringProperty()
    
    count=StringProperty()
    first_line=StringProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        

    def load_file(self):
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
    
    def __init__(self,data,**kwargs):
        super().__init__(**kwargs)
        self.set_list_items(data=data)
        
    def set_list_items(self,data):
        pass
    
class ToggleOptions(Options):

    def set_list_items(self,data):
        self.scroll.include=[]
        self.scroll.exclude=[]
        for option in data:
            element = MultipleToggle(text=option,kind='select_multiple')
            self.scroll.ids[option]=element
            self.scroll.add_widget(element)
            
class DictOptions(Options):
        
    def set_list_items(self,data):
        for k,v in data.items():
            element=DictElement(key=k,value=v)
            self.scroll.ids[k]=element
            self.scroll.add_widget(element)
            
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
    
    def create_dataitem(self,text,**kwargs):
        kwargs={k:v for k,v in kwargs.items() if v!=None}
        dataitem={'text': text,'callback':lambda x:x}
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

class DictElement(MDBoxLayout):
    key=StringProperty()
    value=StringProperty()
    
class AddOption(MDBoxLayout):

    def __init__(self, add_option=None, *args, **kwargs):
        if add_option!=None: self.add_option=add_option
        super().__init__(*args, **kwargs)
    
    def add_option(self,text):
        pass
class ElementInput(TextInput):
    max_h=NumericProperty(1000)
    min_h=NumericProperty(300)
    
# = ============================================================== = #
# =                             DIALOGS                            = #
# = ============================================================== = #

class CustomDialog(BlockingFloatLayout):
    add_decision=BooleanProperty(False)
    title=StringProperty()
    support_text=StringProperty()
    dialog_width=ObjectProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        if self.add_decision:
            decision=SimpleClose()
            self.decision.add_widget(decision)
                
    def deny_func(self):
        pass
    def accept_func(self):
        pass
       
    def open(self):
        from main import ChD
        app = ChD.get_running_app()
        app.open_widget(self)
        
    def dismiss(self):
        from main import ChD
        app = ChD.get_running_app()
        app.dismiss_widget()
        
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
        decision_map={
            'delete_dictionary':[self.delete_dictionary,self.do_nothing],
            'delete_character':[self.delete_character,self.do_nothing],
            'export_character':[self.export_character,self.do_nothing],
            'save_dict_edit':[self.save_dict_changes,self.continue_to_next_screen],
            'save_gram_edit':[self.save_gram_changes,self.continue_to_next_screen],
            'access':[self.permissions_external_storage,self.permission_denied],
        }
        
        if what!=None and what in decision_map: 
            self.accept_func=decision_map[what][0]
            self.deny_func=decision_map[what][1]
        if accept_func != None: self.accept_func = accept_func
        if deny_func != None: self.deny_func = deny_func
        
        if do_choice:
            decision=MakeDecision(button_width=365,
                confirm_text=self.confirm_text,deny_text=self.deny_text,
                deny_func=self.deny_func,accept_func=self.accept_func)
        else:
            decision=SimpleClose()
        self.decision.add_widget(decision)
    
    def set_attrs(_self, **kwargs):
        for k,v in kwargs.items():
            setattr(_self, k, v)

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
        path_to_template = app.get_setting('dictionary_template')
        
        current_screen = app.wm.current_screen
        file=current_screen.character.unicode_unique_string
        d=Dictionary(name=file,characters=[current_screen.character])
        dict_directory = app.get_setting('dict_directory')
        directory=dict_directory/f'{current_screen.parent_dictionary.name}'
        d.write(directory=directory,filename=file,file_format='pleco',template=path_to_template)
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
        print(msg)
    
    def permission_denied(self):
        from main import ChD
        app=ChD.get_running_app()
        settings = app.settings
        settings['app_directory']=app.root_folder
        settings['import_directory']=app.root_folder/'appdata'/'examples'
        app.save_default_settings(settings)
        app.wm.get_screen('settings').update_settings()

class ConfirmExport(ConfirmDecision):
    pass
class ConfirmDelete(ConfirmDecision):
    pass
class ConfirmUnsaved(ConfirmDecision):
    pass
class GrantAccess(ConfirmDecision):
    pass
    # deny_text=StringProperty('Return')
    # confirm_text=StringProperty('Accept')
    
    # def __init__(self,*args,**kwargs):
    #     super().__init__(*args,**kwargs)
    #     decision=MakeDecision(button_width=365,
    #         confirm_text=self.confirm_text,deny_text=self.deny_text,
    #         deny_func=self.deny_func,accept_func=self.accept_func)
    #     self.decision.add_widget(decision)
        


class ChooseAppDirectory(CustomDialog):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from packages.screens.settings import Setting
        content=Setting(setting='app_directory',hint='App Directory',icon='folder-open')
        content.press_button=content.select_directory
        decision=MakeSimpleDecision(deny_func=self.deny_func,accept_func=self.accept_func)
        self.content.ids['app_directory']=content
        self.content.add_widget(content)
        self.decision.add_widget(decision)

    def save_app_dir(self):
        from main import ChD
        app=ChD.get_running_app()
        default_settings = app.get_default_settings()
        app_directory = self.content.ids.app_directory.text
        if os.path.exists(app_directory):
            default_settings['app_directory']=app_directory
            default_settings['import_directory']=app.root_folder/'appdata'/'examples'
            app.save_default_settings(default_settings)
            app.wm.get_screen('settings').update_settings()
            self.dismiss()
    
    def save_default_app_dir(self):
        
        from main import ChD
        app=ChD.get_running_app()
        settings = app.settings
        settings['app_directory']=app.root_folder
        settings['import_directory']=app.root_folder/'appdata'/'examples'
        app.save_default_settings(settings)
        app.wm.get_screen('settings').update_settings()
        self.dismiss()
        
class ShowPaletteOptions(CustomDialog):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args)
        decision=SimpleClose()
        content=PaletteOptions(**kwargs)
        self.decision.add_widget(decision)
        self.content.add_widget(content)    

class ShowOptions(CustomDialog):
    
    def __init__(self,title="",support_text="",allow_add=False,*args,**kwargs):
        self.title=title
        self.support_text=support_text
        super().__init__(title=title,support_text=support_text)
        decision=SimpleClose()
        content=LazyOptions(**kwargs)
        self.decision.add_widget(decision)
        self.content.add_widget(content)    
        self.content.ids['options']=content
        if allow_add: self.content.add_widget(AddOption(add_option=self.add_option))
        
    def add_option(self,text):
        options = self.content.ids['options']
        if text!="" and text not in options.options: 
            options.set_options(options.options+[text])
            options.set_list_items()

class ConfirmFileChoice(CustomDialog):
    def __init__(self,deny_func=None,accept_func=None,*args,**kwargs):
        super().__init__(*args)
        decision=MakeSimpleDecision(deny_func=deny_func,accept_func=accept_func)
        self.decision.add_widget(decision)
        content=FileContent(**kwargs)
        content.load_file()
        self.content.add_widget(content)       
        
class ShowImage(CustomDialog):
    
    def __init__(self,source="",title="",image_size=[100,100],*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.support_text=os.path.basename(source)
        decision=SimpleClose()
        content=CenterImage(source=source,image_size=image_size)
        self.content.add_widget(content)    
        self.decision.add_widget(decision)
        self.title = title.replace('_',' ').title()
class EditElement(CustomDialog):
    allow_multiple=BooleanProperty()
    dtype=ObjectProperty()
    original=ObjectProperty()
    style=StringProperty()
    
    def __init__(self,style='normal',options=[],**kwargs):
        super().__init__(**kwargs)

        self.style=style
        if style=="normal": 
            content=ElementInput()
            self.content.ids['input']=content
            self.content.add_widget(content)
        elif style=="custom":
            self.options=options
            content=ToggleOptions(max_h=1210, data=options)
            self.content.ids['input']=content
            self.content.add_widget(content)
            
        decision=MakeSimpleDecision(deny_func=None,accept_func=self.confirm_edit)
        self.decision.add_widget(decision)
    
    def __list_dict(self,entry):
        options = DictOptions(data=entry)
        self.content.add_widget(options)
        self.content.ids['options'] = options
        
    def set_entry(self,entry):
        if self.style=="custom": 
            for e in entry:
                self.content.ids.input.scroll.ids[e].toggle_on()
        elif isinstance(entry,list): self.content.ids.input.text='- '+'\n- '.join(entry)
        elif isinstance(entry,dict): self.__list_dict(entry)
        elif isinstance(entry,str): self.content.ids.input.text = re.sub(r'[■|●|□|○|◼]','■',entry)
        else: self.content.ids.input.text=str(entry) if entry!=None else ""
        
    def get_dict(self):
        entry = {k:element.input.text.strip(" ") for k,element in self.content.ids['options'].scroll.ids.items()}
        entry = {k:v for k,v in entry.items() if v!=""}
        entry = "" if entry == {} else entry
        return entry
    
    def get_input(self,category, convert_pronunciation=True,new_line=True):
        from main import ChD
        app=ChD.get_running_app()
        dict_categories = app.get_setting('categories')
        
        if self.style=="custom":
            active = self.content.ids.input.scroll.include
            return active
        
        text = self.content.ids.input.text
        if convert_pronunciation: text = convert_pronunciations(text)
        
        def allows_multiple():
            if category in dict_categories.keys():
                if dict_categories[category]==list: return True
                else: return False
            elif category == 'new_character': return True
            elif self.allow_multiple: return True
            else: return False
            
        def get_default_dtype():
            if category in dict_categories: return dict_categories[category]
            elif category == 'new_character': return list
            elif self.dtype != None: return self.dtype
            else: return str
        
        if allows_multiple():
            # only new point when new line
            # relevant if text contains '-'
            if new_line==True: 
                text = text.lstrip('-').split('\n-')
                new_entry = [e.replace('\n',' ').strip(' ') for e in text if e != '']
            elif new_line==False:
                text = text.replace('\n',' ').lstrip('-').split('-')
                new_entry = [e.strip(' ') for e in text if e != '']
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
        categories=['simple','traditional','pronunciation']
        category='new_character'
        new_entry = self.get_input(category,convert_pronunciation=False,new_line=False)
        
        if len(new_entry) == 3:
            # entries={k:v if k!='pronunciation' else encode_pinyin(v) for k,v in zip(categories,new_entry)}
            entries={k:v for k,v in zip(categories,new_entry)}
            if self.screen.name == 'view_dict':
                self.screen.add_character(entries=entries)
            elif self.screen.name.startswith('C'):
                self.screen.update_character(entries=entries)
                
    def __category_edit(self):
        category=self.title.lower().replace(' ','_')
        if 'input' in self.content.ids: new_entry = self.get_input(category,convert_pronunciation=True,new_line=True)
        else: new_entry=self.get_dict()
        
        if category == 'dictionary_name': self.screen.rename_dict(new_entry)
        else:
            if new_entry == None:
                pass
            elif new_entry != None: 
                if new_entry == "": new_entry = None
                self.screen.update_category(category=category,entry=new_entry,original=self.original)
        