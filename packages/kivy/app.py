import sys
import os
import json
from urllib.parse import urlparse
from pathlib import Path
from kivy.utils import platform
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.metrics import Metrics, dp, sp, inch, dpi2px
from kivy.resources import resource_add_path
from pathlib import Path
from .colors import CustomColors
    
def get_project_root():
    root_directory=Path(os.path.abspath(__file__)).parent.parent.parent
    return Path(root_directory)

APP_DIR = get_project_root()
Window.softinput_mode = "below_target"


class Helper:
    platform=platform
    metrics=Metrics
    custom = CustomColors()
    radius = 30
    tmp_files = {}
    tmp_files_rm = {}
    
    
    def pre_load_widgets(self):
        from .snackbars import AttentionMsg, ErrorMsg
        from .layouts import ShowFileContent
        from .dialogs import (
            CustomDialog,
            ShowOptions,
            ConfirmUnsaved,
            ConfirmExport,
            ConfirmDelete,
            ConfirmFileChoice,
            ConfirmDecision, 
            ShowImage, 
            ShowPaletteOptions, 
            GrantAccess, 
            ChooseAppDirectory,
            EditElement,
            )
        from .file_manager import MyFileManager
        
        self.pre_loaded_widgets = {
            'palette' : ShowPaletteOptions(itemclass='PaletteItem',max_h=1300),
            'show_file' : ShowFileContent(),
            'attention' : AttentionMsg(),
            'error' : ErrorMsg(),
            'image' : ShowImage(),
            'app_dir' : ChooseAppDirectory(),
            'dialog' : CustomDialog(),
            'decision' : ConfirmDecision(),
            'access' : GrantAccess(),
            'save_dict' : ConfirmUnsaved(what='save_dict_edit',do_choice=True),
            'save_gram' : ConfirmUnsaved(what='save_gram_edit',do_choice=True),
            'delete_char' : ConfirmDelete(what='delete_character',do_choice=True),
            'delete_dict' : ConfirmDelete(what='delete_dictionary',do_choice=True),
            'export_char' : ConfirmExport(what='export_character',do_choice=True),
            'file_choice' : ConfirmFileChoice(),
            'options' : ShowOptions(),
            'options_add' : ShowOptions(allow_add=True),
            'file_manager' : MyFileManager(),
            'edit_element' : EditElement(),
        }

    @property
    def root_folder(self):
        return get_project_root()
    
    def get_color(self,color):
        return self.custom.colors[color]

    def test(self,msg="TEST"):
        print(msg)
        
    def tmp_file(self,file,tmp_directory):
        file_dir = Path(file).parent
        tmp_file = tmp_directory/Path(file).name
        if file_dir != tmp_directory:
            os.makedirs(tmp_directory,exist_ok=True)
            self.tmp_files[str(file)] = tmp_file
        return tmp_file
    
    def tmp_file_rm(self,file,tmp_directory):
        file_dir = Path(file).parent
        tmp_file = tmp_directory/Path(file).name
        if file_dir != tmp_directory:
            os.makedirs(tmp_directory,exist_ok=True)
            self.tmp_files_rm[str(file)] = tmp_file
        return tmp_file
    
    def move_tmp_files(self,file=None):
        import shutil
        
        def copy(file:str):
            file = str(file)
            tmp_file = self.tmp_files[file]
            if tmp_file not in self.tmp_files_rm.values(): 
                shutil.copyfile(tmp_file, file)
            
        def remove(file:str):
            file = str(file)
            tmp_file = self.tmp_files_rm[file]
            self.remove_file(file,create_tmp=False)
            self.remove_file(tmp_file,create_tmp=False)
    
        if str(file) in self.tmp_files_rm:
            remove(file)
        elif str(file) in self.tmp_files:
            copy(file)
            
        elif file==None:
            for file in self.tmp_files_rm:
                remove(file)
            for file in self.tmp_files:
                copy(file)
                
        self.clean_tmp_files()
        
    def clean_tmp_files(self):
        for file in self.tmp_files.values():
            self.remove_file(file,create_tmp=False)
        for tmp_file in self.tmp_files_rm.values():
            self.remove_file(tmp_file,create_tmp=False)
        self.tmp_files={}
        self.tmp_files_rm={}
        
    def remove_file(self,file,create_tmp=False,tmp_directory=None):
        if create_tmp and tmp_directory!=None: 
            import shutil
            src_path = file
            dest_path = self.tmp_file_rm(file=file,tmp_directory=tmp_directory)
            if os.path.isfile(src_path):
                shutil.copyfile(src_path, dest_path)
        # # elif str(file) in self.tmp_files: file = self.tmp_files.pop(str(file))
        if os.path.isfile(file): os.remove(file)
    
    def open_file(self,file,allow_new=False,create_tmp=False):
        filename = Path(file).name
        
        # choose tmp file instead 
        tmp_directory = self.get_setting('tmp_directory')
        tmp_file = tmp_directory/filename
        if create_tmp: 
            # removed -> edited -> unremoved
            if str(file) in self.tmp_files_rm: 
                self.tmp_files[str(file)] = tmp_file
                # file,allow_new = tmp_file,False
                file = tmp_file
            # edit tmp file 
            elif str(file) in self.tmp_files: 
                file = self.tmp_files[str(file)]
            # forgotten tmp files 
            elif not os.path.isfile(file) and os.path.isfile(tmp_file): 
                self.tmp_files[str(file)] = tmp_file
                file = tmp_file
        
        # don't open file when not editable or should be created new
        if not os.path.isfile(file) and not allow_new: return None
        elif os.path.isfile(file) and allow_new: return None
        # overwrite
        elif not allow_new and os.path.isfile(file): pass
        # create new
        elif allow_new and not os.path.isfile(file): pass

        # open and edit files
        dialog = self.pre_loaded_widgets['show_file']
        dialog.read_file(file=str(file),allow_new=allow_new,create_tmp=create_tmp)
    
    def import_file(self,src_path, dest_dir, new_name:str="",inform=False):
        if new_name=="": new_name=src_path.name
        dest_path = dest_dir/new_name
        try:
            import shutil
            shutil.copyfile(src_path, dest_path)
            if inform: 
                msg = self.pre_loaded_widgets['attention']
                msg.open(attention='File was imported',msg=f'Copied from {src_path} to {dest_path}')
            return True
        except Exception as err:
            import traceback
            print(traceback.format_exc())   
            return False
        
    def load_json(self,file,directory=APP_DIR):
        
        def extract(value, key=None):
            if isinstance(value,str) and 'directory' in key:
                return Path(value)
            else:
                return value
        
        path=file if directory==None else Path(directory)/file
        with open(path, "r") as f:
            settings = json.load(f)
        return {k:extract(value=v,key=k) for k,v in settings.items()}
    
    def dump_json(self,data,file, directory=APP_DIR, indent=4):
        
        def convert(value):
            if isinstance(value, Path):
                value = str(value)
            return value
                
        path=file if directory==None else Path(directory)/file
        with open(path, "w") as f:
            json.dump({k:convert(v) for k,v in data.items()}, f,indent=indent,ensure_ascii=False)
        return True
    
    def save_list(self,data,file,directory=APP_DIR):
        path=file if directory==None else Path(directory)/file
        with open(path,'w') as f:
            for list_item in data:
                f.write(str(list_item)+'\n')
    
    def load_list(self,file,directory=APP_DIR):
        
        path=file if directory==None else Path(directory)/file
        with open(path,'r') as f:
            data = f.read().splitlines()
        return [line.strip() for line in data if line.strip() != ""]
    
    
    def is_url(self,url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
        

    def open_url(self,url):
        import webbrowser
        go_to_url=lambda: webbrowser.open(url)
        if self.is_url(url):
            dialog = self.pre_loaded_widgets['decision']
            dialog.set_attrs(title="Open Browser",support_text=f"\n{url}")
            dialog.choose_action(do_choice=True,accept_func=go_to_url)
            dialog.open()
    
    def show_info(self,title:str="Information",text:str=''):
        dialog = self.pre_loaded_widgets['dialog']
        dialog.set_attrs(title=title,support_text=text,add_decision=True)
        dialog.open()
        
    def show_image(self,image_type,file,size=[700,700]):
        if image_type!="":
            dialog = self.pre_loaded_widgets['image']
            dialog.choose_image(source=file,title=image_type,image_size=size)
            dialog.open()
            
    def hide_widget(self,widget,do_hide=True,x:bool=True,y:bool=True):
        if hasattr(widget, 'saved_attrs'):
            if not do_hide:
                if x and not y: 
                    widget.size_hint_x, widget.width, widget.opacity = widget.saved_attrs
                elif not x and y: 
                    widget.size_hint_y, widget.height, widget.opacity = widget.saved_attrs
                elif x and y: 
                    widget.size_hint_y, widget.height, widget.size_hint_x, widget.width, widget.opacity = widget.saved_attrs
                widget.hidden = False
                del widget.saved_attrs
        elif do_hide:
            if x and not y: 
                widget.saved_attrs = (widget.size_hint_x, widget.width, widget.opacity)
                widget.size_hint_x, widget.width, widget.opacity = None, 0, 0
            elif not x and y: 
                widget.saved_attrs = (widget.size_hint_y, widget.height, widget.opacity)
                widget.size_hint_y, widget.height, widget.opacity = None, 0, 0
            elif x and y: 
                widget.saved_attrs = (widget.size_hint_y, widget.height, widget.size_hint_x, widget.width, widget.opacity)
                widget.size_hint_y, widget.height, widget.size_hint_x, widget.width, widget.opacity = None, 0, None, 0, 0
            widget.hidden = True
            
    @property
    def window_size(self):
        return Window.size
    
    @property
    def __diag_inch(self):
        xpix = Window.size[0]
        ypix = Window.size[1]
        xinch = xpix/dpi2px(1,'in')
        yinch = ypix/dpi2px(1,'in')
        diag_inch = (xinch*xinch+yinch*yinch)**.5
        return diag_inch
    
    def get_metrics(self):
        window_metrics = f"\nwindow size = {Window.size}\ndiagonal = {self.__diag_inch}"
        metrics = f"\ndensity = {self.metrics.density} \ndpi = {self.metrics.dpi} \nfontscale = {self.metrics.fontscale}"
        more_metrics = f"\ndp(1) = {dp(1)} \nsp(1) = {sp(1)} \ninch(1) = {inch(1)}"
        # user_data_dir = str(self.user_data_dir)
        return f"{self.platform}: \n{window_metrics} {metrics}"


class MyApp(MDApp,Helper):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_directory = self.root_folder
        self.__appdata = self.root_folder/"appdata"
        self.__config = Path(self.user_data_dir)
        self.__first_init = False
        
        os.makedirs(self.__appdata,exist_ok=True)
        os.makedirs(self.__config,exist_ok=True)
        for folder in ['defaults','colors','fonts','templates']:
            os.makedirs(self.__appdata/folder,exist_ok=True)
    
        resource_add_path(self.__appdata/'fonts')
    
        if platform == 'android':
            Window.bind(on_keyboard_height=self.on_keyboard_height)
    
    def pre_load_widgets(self):
        super().pre_load_widgets()
    
    def on_keyboard_height(self, window, height):
        print('\n'*5,window, height)
        
    def build(self):
        Window.keyboard_anim_args = {'d': .2, 't': 'in_out_quad'}
        Window.softinput_mode = 'below_target'
        self.theme_cls.bind(theme_style=self.sync_custom_colors)
        self.theme_cls.bind(primary_palette=self.sync_custom_colors)
        self.sync_custom_colors()
        # self.pre_load_widgets()
    
    def on_start(self):

        if not self.__access_granted():
            self.__show_validation_dialog()
        else:
            if self.__first_init:
                self.__decide_on_app_directory()

        from kivy.base import EventLoop
        EventLoop.window.bind(on_keyboard=self.hook_keyboard)
    
    # = ============================================================== = #
    # =                            SETTINGS                            = #
    # = ============================================================== = #
        
    @property
    def config_dir(self):
        return self.__config
    
    @property
    def app_files(self):
        # found all at self.__config
        return {
            'settings':'default_settings.json',
            'backup':'Backups/data.db'
            }
    
    def get_app_file(self,file:str,open_file=True):
        if file in self.app_files: 
            file = self.__config/self.app_files[file]
            if os.path.isfile(file):
                if not open_file: return file
                elif str(file).endswith('.json'): return self.load_json(file)
                elif str(file).endswith('.txt'): return self.load_list(file)
                elif str(file).endswith('.png'): return file
                else: return file
                
    def get_app_data(self,file,typ,open_file=True):
        if typ in os.listdir(self.__appdata):
            file = self.__appdata/typ/file
            if os.path.isfile(file):
                if not open_file: return file
                elif str(file).endswith('.json'): return self.load_json(file)
                elif str(file).endswith('.txt'): return self.load_list(file)
                elif str(file).endswith('.png'): return file
                else: return file

    def save_app_config(self,data:dict,file:str):
        if file in self.app_files: 
            file = self.__config/self.app_files[file]
            if str(file).endswith('.json') and isinstance(data,dict): self.dump_json(data,file)
            elif str(file).endswith('.txt') and isinstance(data,list): self.save_list(data,file)

    @property
    def settings(self):
        settings = self.get_app_file('settings')
        return settings

    def get_setting(self,kind,default=True,settings=None):
        if default: settings = self.get_default_settings()
        elif settings == None: settings = self.settings
        
        if kind in settings.keys():
            result = settings[kind]
        else:
            print(f'{kind} not found in settings')
            result = None
        return result

    def get_default_settings(self):
        # get DEFAULT settings    
        # getting default settings from specified default_settings_file (under .config)
        settings = self.get_app_file('settings')
        if settings != None: 
            self.app_directory = settings['app_directory']
            return settings
        
        # get default settings from appdata folder defaults (only necessary first time)
        self.__first_init = True
        settings=self.get_app_data('default_settings.json','defaults')
        settings = {} if settings==None else settings
        self.save_app_config(settings,'settings')
        return settings
           
    def __show_validation_dialog(self):
        if self.platform == "android":
            from jnius import autoclass
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                support_text="To access files on the phone it is required to grant the app access to the storage."
                do_choice=True
            else:
                support_text="Storage access was already granted."
                do_choice=False
        elif self.platform == "linux":
            support_text=f"For {self.platform} no further storage access needs to be granted."
            do_choice=False
        else:
            support_text=f'Access for {self.platform} might be necessary.'
            do_choice=True
            
        show_permission_popup = self.pre_loaded_widgets['access']
        show_permission_popup.choose_action(what='access',do_choice=do_choice)
        show_permission_popup.set_attrs(support_text=support_text)
        show_permission_popup.open()
        
    def __decide_on_app_directory(self):
        show_directory_popup = self.pre_loaded_widgets['app_dir']
        show_directory_popup.open()
        
    def __access_granted(self):
    
        if self.platform == 'android': 
            from android import api_version
            from jnius import autoclass
            if api_version > 29:
                Environment = autoclass("android.os.Environment")
                return Environment.isExternalStorageManager()
            else: return False
        
        else: return True
    
    # = ============================================================== = #
    # =                             DESIGN                             = #
    # = ============================================================== = #
    
    def apply_palette(self,palette='Lavender'):
        self.theme_cls.primary_palette = palette
    
    def apply_theme(self,style:str='Dark'):
        self.theme_cls.theme_style = style
        self.theme_cls.dynamic_scheme_contrast = 0.6
        
    def switch_theme(self):
        if self.theme_cls.theme_style == 'Dark':
            self.apply_theme('Light')
        elif self.theme_cls.theme_style == 'Light':
            self.apply_theme('Dark')
            
    def get_palette_colors(self):
        palette_colors = self.get_app_data('palette_colors.json','colors')
        return palette_colors
    
    def select_palette(self):
        dialog = self.pre_loaded_widgets['palette']
        dialog.open()
        
    # = ============================================================== = #
    # =                             COLORS                             = #
    # = ============================================================== = #
    
    def sync_custom_colors(self,*args):
        self.custom.update_colors(self.theme_cls)
    
    # = ============================================================== = #
    # =                         SCREEN MANAGER                         = #
    # = ============================================================== = #
        
    def hook_keyboard(self,window,key,*largs):
        if key == 27:
            if self.file_manager_back():
                return True
            elif self.dismiss_all():
                return True
            else:
                return self.previous_screen()
        return False    
    
    def add_window_manager(self,wm):
        self.wm = wm    
    
    def add_screen(self,screen,*args,**kwargs):
        all_screen_names = [screen.name for screen in self.wm.screens]
        if screen.name in all_screen_names:
            self.wm.remove_widget(self.wm.get_screen(screen.name))
        self.wm.add_widget(screen)
        self.switch_screen(screen_name=screen.name,*args,**kwargs)
        
    def open_widget(self,widget):
        self.dismiss_all()
        self.wm.current_screen.layout = widget
        self.wm.current_screen.add_widget(widget)
        self.wm.current_screen.ids['layout'] = widget
    
    def open_dialog(self,widget):
        self.dismiss_dialog()
        self.wm.current_screen.dialog = widget
        self.wm.current_screen.add_widget(widget)
        self.wm.current_screen.ids['dialog'] = widget
        
    def open_snackbar(self,widget):
        self.dismiss_snackbar()
        self.wm.current_screen.snackbar = widget
        # self.wm.current_screen.add_widget(widget)
        self.wm.current_screen.ids['snackbar'] = widget
        
    def dismiss_dialog(self):
        if hasattr(self.wm.current_screen,'dialog'):
            del self.wm.current_screen.dialog
            widget = self.wm.current_screen.ids.pop('dialog')
            for child in self.wm.current_screen.children:
                if child==widget: self.wm.current_screen.remove_widget(child)
            return True
        else: return False
    
    def dismiss_widget(self):
        if hasattr(self.wm.current_screen,'layout'):
            del self.wm.current_screen.layout
            widget = self.wm.current_screen.ids.pop('layout')
            for child in self.wm.current_screen.children:
                if child==widget: self.wm.current_screen.remove_widget(child)
            return True
        else: return False

    def dismiss_file_manager(self):
        if hasattr(self.wm.current_screen,'file_manager') \
            and self.wm.current_screen.file_manager._window_manager_open:
                self.wm.current_screen.file_manager.close()
    
    def dismiss_snackbar(self):
        if hasattr(self.wm.current_screen,'snackbar'):
            del self.wm.current_screen.snackbar
            widget = self.wm.current_screen.ids.pop('snackbar')
            widget.dismiss()
            return True
        else: return False
    
    def dismiss_all(self):
        
        if self.dismiss_snackbar():
            return True
        elif self.dismiss_dialog():
            return True
        elif self.dismiss_file_manager():
            return True
        elif self.dismiss_widget():
            return True
        else:
            return False

    def file_manager_back(self):
        if hasattr(self.wm.current_screen,'file_manager') \
            and self.wm.current_screen.file_manager._window_manager_open:
                self.wm.current_screen.file_manager.back()
                return True
        else: return False
        
    def switch_screen(self,screen_name,direction,remember=True,home='home'):
        if screen_name not in self.wm.screen_names: return None

        previous_screen_name = self.wm.current
        previous_direction = self.wm.transition.direction
        previous_screen = self.wm.current_screen
        if screen_name != previous_screen_name \
            and screen_name in self.wm.screen_names:
                if self.wm.previous_screen_names != []\
                    and self.wm.previous_screen_names[-1] == screen_name:
                    self.wm.previous_screen_names = self.wm.previous_screen_names[:-1]
                    self.wm.previous_transition_directions = self.wm.previous_transition_directions[:-1]
                if remember: 
                    self.wm.previous_screen_names.append(previous_screen_name)
                    self.wm.previous_transition_directions.append(direction)
                if screen_name==home: 
                    self.wm.previous_screen_names=[]
                    self.wm.previous_transition_directions=[]
                self.wm.current = screen_name
                self.wm.transition.direction = direction
                switched = {'previous': 
                    {'screen_name':previous_screen_name,
                     'screen':previous_screen,
                     'transition':previous_direction}, 
                            'current':
                    {'screen_name':screen_name,
                     'screen':self.wm.current_screen,
                     'transition':direction}}
                return switched
        else: return None
            
    def previous_screen(self):
        if self.wm.previous_screen_names != []:
            previous_screen_name=self.wm.previous_screen_names[-1]
            previous_direction=self.wm.previous_transition_directions[-1]
            self.wm.previous_screen_names=self.wm.previous_screen_names[:-1]
            self.wm.previous_transition_directions=self.wm.previous_transition_directions[:-1]
            if previous_direction in ['right','left']:
                direction = 'right' if previous_direction == 'left' else 'left'
            elif previous_direction in ['up','down']:
                direction = 'up' if previous_direction == 'down' else 'down'
            else: direction=""
            self.switch_screen(previous_screen_name,direction,remember=False)
            if self.wm.current!=previous_screen_name:
                self.wm.previous_screen_names.append(previous_screen_name)
                self.wm.previous_transition_directions.append(previous_direction)
            return True
        else:
            return False
    