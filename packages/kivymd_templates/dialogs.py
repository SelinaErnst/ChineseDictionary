from kivymd.uix.dialog.dialog import MDDialog, MDDialogButtonContainer
from kivy.utils import platform

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


with open("appdata/colors/palette_colors.json", "r") as f:
    import json
    palette_colors = json.load(f)


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
                    msg="I don't know what happend."
        else:
            msg=f'This action is only for android api versions greater than 29. This device is at {api_version}.'
    else:
        msg=f"This action is only for android devices. This device is working with {platform}."
    return msg




class MyDialog(MDDialog):
    title = StringProperty()
    support_text = StringProperty()

class ConfirmChoice(MyDialog):
    count=StringProperty()
    first_line=StringProperty()
    file_name=StringProperty()
    dict_name=StringProperty()
    file_format=StringProperty()


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
            
class ShowOptions(MyDialog):
    list_height = NumericProperty()
    
    def __init__(self, title, setting, options, itemclass, list_height, icons, *args, **kwargs):
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
        return palette_colors[self.theme_cls.theme_style][name.capitalize()][color_name]

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
    