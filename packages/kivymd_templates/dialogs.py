from kivymd.uix.dialog.dialog import MDDialog, MDDialogButtonContainer
from kivy.utils import platform
from packages.pleco import character as pleco_character
from packages.pleco import detect_type, convert_pronunciations
import re

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
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/dialogs.kv')

def grant_permissions_external_storage():  
    if platform == "android":
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Environment = autoclass("android.os.Environment")
        Intent = autoclass("android.content.Intent")
        Settings = autoclass("android.provider.Settings")
        Uri = autoclass("android.net.Uri")
        if api_version > 29: 
            if Environment.isExternalStorageManager():
                msg="Storage access was already granted. No need to grant it again."
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
            msg=f'This action is only for android api versions greater than 29. This device is at {api_version}.'
    else:
        msg=f"This action is only for android devices. This device is working with {platform}."
    return msg




class MyDialog(MDDialog):
    title = StringProperty()
    support_text = StringProperty()

class ConfirmDelete(MyDialog):
    file=StringProperty()
    accept_func=ObjectProperty(None)
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.accept_func==None: self.accept_func=self.do_nothing
        
    def do_nothing(self):
        pass
    
    def do_something(self):
        print(self.file)
        
    def delete_dictionary(self):
        from main import ChD
        app=ChD.get_running_app()
        app.delete_dictionary(name=self.file)
        app.previous_screen()
        app.wm.current_screen.set_files()
        
    
                
class ConfirmChoice(MyDialog):
    count=StringProperty()
    first_line=StringProperty()
    file_name=StringProperty()
    dict_name=StringProperty()
    file_format=StringProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if self.file_format == "":
            from packages.pleco import valid_ext
            extension = os.path.splitext(self.file_name)[1]
            try:
                self.file_format = [f for f,e in valid_ext.items() if extension in e][0]
            except:
                self.file_format = ''
                
    def load_file(self,file_path):
        self.file_path=file_path
        if os.path.isfile(file_path):
            count,first_line=0,""
            with open(file_path, "r") as f:
                first_line = f.readline().strip()
                count = sum(1 for _ in f)+1
            self.count=str(count)
            self.first_line = first_line
            

class GrantAccess(MyDialog):
    deny_text=StringProperty('No')
    done=BooleanProperty(False)
    
    def permissions_external_storage(self):  
        from main import ChD, dump_json, load_json
        msg=grant_permissions_external_storage()
        app=ChD.get_running_app()
        app.settings['access_granted']=True
        directory=app.get_setting('app_directory')+'.config/'
        dump_json(app.settings,directory+"settings.json")
        self.dismiss()
        return msg
    
    def permission_denied(self):
        from main import ChD
        app=ChD.get_running_app()
        app.settings['app_directory']=str(app.root_folder)
        app.settings['import_directory']=str(app.root_folder)+'appdata/examples/'
        app.save_default_settings(default_settings=app.settings,update=True)
        app.wm.get_screen('settings').update_settings()
        app.wm.get_screen('filechooser').update()
        self.dismiss()
            
class AddElement(MyDialog):
    allow_multiple=BooleanProperty(False)    
    # confirm_edit=ObjectProperty()
    
    def confirm_edit(self):
        from main import ChD, ShowCharacter
        app=ChD.get_running_app()
        current_screen=app.wm.current_screen
        character=current_screen.character if hasattr(current_screen,'character') else pleco_character()
        prop=self.title.lower().replace(' ','_')

        if self.title != 'Character' and prop in character.categories:
            text =  self.ids.input.text
            text = convert_pronunciations(text)
            # print(re.sub(r'\[(?:(?![\u4e00-\u9fff])[\S]+)\]',decode_pinyin,text.lstrip('[').rstrip(']')))

            if self.allow_multiple:
                new_entry = [e.replace('\n',' ').strip(' ') for e in text.lstrip('-').split('\n-') if e != '']
            else:
                new_entry = text.lstrip('-').strip(' ').replace('\n',' ')
                new_entry=detect_type(new_entry)

            if new_entry not in ["",[""],[]]:
                if type(new_entry) != character.get_default_dtype(prop):
                    dt=character.get_default_dtype(prop)
                    try:
                        new_entry=dt(new_entry)
                    except:
                        return
                
                character.update({prop:new_entry},get_dtype_warning=False)
                if prop not in current_screen.categories:
                    current_screen.list_translations(prop)
                new_entry=new_entry if isinstance(new_entry,list) else [new_entry]
                current_screen.ids.scroll.ids[prop].bullets.remove_bullets()
                current_screen.ids.scroll.ids[prop].bullets.create_bullets(results=new_entry)
            else:
                character.remove_property(prop)
                current_screen.remove_translations(prop)

        elif self.title == 'Character':
            categories=['simple','traditional','pronunciation']
            new_entries = [e.strip(' ') for e in self.ids.input.text.replace('\n',' ').lstrip('-').split('-') if e != '']
            if len(new_entries) == 3:
                kwargs={k:v for k,v in zip(categories,new_entries)}
                # kwargs.update({'pronunciation':encode_pinyin(kwargs['pronunciation'])})
                character.update(kwargs)
                if current_screen.name == 'viewdict':
                    char_string = f'C_{character.entry.simple}_{character.entry.traditional}_{character.entry.pronunciation}'
                    current_screen.dictionary = current_screen.dictionary + character
                    current_screen.set_list_items()
                    current_screen.entry_count += 1
                    parent_dictionary = app.wm.current_screen.dictionary
                    screen = ShowCharacter(name=char_string, character=character, dict_screen=current_screen, parent_dictionary=parent_dictionary)
                    app.wm.add_widget(screen)
                    current_screen = app.switch_screen(char_string,'left')
                    self.dismiss()
                else:
                    current_screen.update_character()
                    current_screen.resize_head()

        elif prop not in character.categories:
            new_entry = self.ids.input.text.lstrip('-').strip(' ').replace('\n',' ')
            new_entry=detect_type(new_entry)
            if prop == 'new_name': current_screen.rename_dict(new_entry)
                            
class ShowOptions(MyDialog):
    list_height = NumericProperty()
    
    def __init__(self, title, options, itemclass, list_height, setting="", icons=[], *args, **kwargs):
        self.itemclass = itemclass
        self.list_height = list_height
        super().__init__(*args, **kwargs)
        self.setting = setting
        self.title = title
        self.options = options
        self.icons = icons
        if options != []:
            self.set_list_items()
        
    def create_dataitem(self,text,**kwargs):
        dataitem={
            'setting':self.setting,
            'text': text,
            'style': 'text',
            'theme_bg_color': 'Custom',
            'md_bg_color': self.theme_cls.surfaceBrightColor,
            'radius':20,
            'callback':lambda x:x}
        dataitem.update(kwargs)
        return dataitem 
    
    def add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)
        
    def set_list_items(self):
        self.rv_scroll.data = []
        if self.icons == []:
            for option in self.options: 
                dataitem=self.create_dataitem(option)
                self.add_list_item(dataitem)
        elif len(self.icons) == len(self.options):
            for option,icon in zip(self.options,self.icons):
                dataitem=self.create_dataitem(text=option,icon=icon)
                self.add_list_item(dataitem)

class ShowPaletteOptions(ShowOptions):
    
    def __init__(self,*args,**kwargs):
        from main import load_json
        self.palette_colors = load_json('appdata/colors/palette_colors.json')
        super().__init__(*args,**kwargs)
        

    
    def create_dataitem(self,text):
        kwargs=self.add_palette_colors(text)
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

# = ============================================================== = #
# =                            CONTAINER                           = #
# = ============================================================== = #
    
class MakeDecision(MDDialogButtonContainer):
    confirm_text=StringProperty('Yes')
    confirm_icon=StringProperty('check')
    deny_text=StringProperty('No')
    deny_icon=StringProperty('close')
    dismiss_func=ObjectProperty()
    accept_func=ObjectProperty()
    button_width=NumericProperty(350)
    
class MakeSimpleDecision(MDDialogButtonContainer):
    confirm_icon=StringProperty('check')
    deny_icon=StringProperty('close')
    dismiss_func=ObjectProperty()
    accept_func=ObjectProperty()
    button_width=NumericProperty(150)