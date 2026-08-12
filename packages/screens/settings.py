import os
import traceback
from packages.kivy import (
    MyScreen,
    ErrorMsg, # snackbar
    EntryFieldWithIcon,
    StringProperty, 
    ListProperty,
    )
from kivy.utils import hex_colormap
        
class Settings(MyScreen):
    
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        # settings are only initialized at the start
        self.settings = self.get_settings()
    
    def get_settings(self):
        # get all the settings (user defined settings if available, if not default settings)
        from main import ChD
        app = ChD.get_running_app()
        return app.settings
    
    def set_up_screen(self):
        self.my_app.clean_tmp_files()
    
    # = ============================================================== = #
    # =                             WIDGET                             = #
    # = ============================================================== = #
            

        
    # = ============================================================== = #
    # =                         CHANGE SETTINGS                        = #
    # = ============================================================== = #
        
    def update_settings(self):
        for setting in self.ids.keys():
            key = self.get_setting(setting)
            # print(key,self.ids[setting].ids.label.text,setting)
            if key!=None:
                self.ids[setting].ids.label.text = str(key)
                self.settings[setting] = key

    def save_settings(self):
        from main import ChD
        app:ChD = ChD.get_running_app()
                    
        # = –––––––––––––––––––––––– user settings ––––––––––––––––––––––– = #
            
        new_settings=self.settings
        correctness={}
        i=0
        # check if settings are all correctly given
        for setting,obj in self.ids.items():
            if setting in self.settings.keys():
                is_correct=self.ids[setting].is_correct()
                if is_correct:
                    new_settings[setting] = self.ids[setting].ids.label.text
                correctness[self.ids[setting].hint]=is_correct
        all_true=all(correctness.values())
        
        if all_true:
            try:
                app.save_user_settings(new_settings)
                app.update_design()
                
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()            
                import traceback
                print(traceback.format_exc())
        else:
            incorrect=[k for k,v in correctness.items() if not v]
            incorrect_entries=', '.join(incorrect)
            ErrorMsg(
                error="Invalid settings",
                msg=f'Cannot save, check settings: {incorrect_entries}'
                ).open()
            
        # = –––––––––––––––––––– dictionary categories ––––––––––––––––––– = #
        
        if self.ids['dict_cat'].new_options != {}:
            rename_map = self.ids['dict_cat'].rename_map
            new_categories = self.ids['dict_cat'].new_options
            old_categories = app.get_categories()
            renamed = [cat for cat in old_categories if cat in rename_map]
            removed = [cat for cat in old_categories if (cat not in new_categories and cat not in renamed)]
            added = [cat for cat in new_categories if (cat not in old_categories and cat not in rename_map.values())]
            
            # IMPORTANT: RENAMING
            if renamed != []: app.rename_category(rename_map=rename_map)
            # CHANGE JSON
            app.save_app_config(new_categories,'categories')
        
        # = ––––––––––––––––– templates and other configs –––––––––––––––– = #
        
        self.my_app.move_tmp_files()
        # print(self.my_app.tmp_files_rm,self.my_app.tmp_files)
        self.my_app.previous_screen()
        self.my_app.pre_load_widgets()
        
class Setting(EntryFieldWithIcon):
    icon = StringProperty()
    options = ListProperty() # determines valid entries
    icons = ListProperty()
    itemclass = StringProperty()
    support_text = StringProperty()
    setting= StringProperty()
    
    # = ============================================================== = #
    # =                         SELECT OPTIONS                         = #
    # = ============================================================== = #
    
    # = –––––––––––––––––––––––– theme  style –––––––––––––––––––––––– = #
    
    def switch_theme(self):
        from main import ChD
        ChD.get_running_app().switch_theme()
        self.ids.label.text = self.theme_cls.theme_style
        
    @property
    def themes(self):
        return ['Dark','Light']
        
    # = ––––––––––––––––––––––– primary palette –––––––––––––––––––––– = #
        
    @property
    def palettes(self):
        return [palette.capitalize() for palette in hex_colormap.keys()]
            
    # = ––––––––––––––––––––––––– directories –––––––––––––––––––––––– = #
        
    def select_directory(self):
        from main import ChD
        app:ChD = ChD.get_running_app()
        screen = app.wm.current_screen
        
        def select_path(path):
            self.text = path
            screen.file_manager.close()
            
        try: 
            kwargs = {
            'description' : f'Decide on {self.hint.lower()}.',
            'select_path' : select_path,
            'ext' : ['.____nothing____'],
            }
            file_manager = app.pre_loaded_widgets['file_manager']
            file_manager.set_attrs(**kwargs)
            file_manager.show(path=None,use_root_folder=True)
            screen.file_manager = file_manager
            
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
            import traceback
            print(traceback.format_exc())
         
    # = ============================================================== = #
    # =                              VALID                             = #
    # = ============================================================== = #
    
    def is_path(self,path:str):
        exists = os.path.isdir(path)
        return exists
    
    # overwriting (dont change name!)
    def is_correct(self):
        if 'directory' in self.hint.lower():
            return self.is_path(self.ids.label.text)
        elif 'palette' in self.hint.lower():
            correct = self.ids.label.text in self.palettes
            if correct: self.theme_cls.primary_palette = self.ids.label.text
            return correct
        elif 'theme' in self.hint.lower():
            correct = self.ids.label.text in self.themes
            if correct: self.theme_cls.theme_style = self.ids.label.text
            return correct
        else:
            return self.ids.label.text in self.options
        
