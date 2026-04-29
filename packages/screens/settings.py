import os
import traceback
from packages.kivy import (
    MyScreen,
    ErrorMsg, # snackbar
    EntryFieldWithIcon,
    ShowPaletteOptions,
    MyFileManager,
    StringProperty, 
    NumericProperty, 
    ListProperty,
    MDBoxLayout,
    MDAnchorLayout
    )
from kivy.utils import hex_colormap

class ShowFileContent(MDAnchorLayout):
    text=StringProperty()
    file=StringProperty()
    
    def read_file(self,file:str|None=None):
        if file!=None: self.file=file
        with open(self.file) as f:
            lines = f.readlines()
            text=''.join(lines)
        self.text = text+'\n'*17
        
    def change_file(self,file:str|None=None):
        if file!=None: self.file=file
        if os.path.isfile(self.file):
            with open(self.file, "w") as f:
                f.write(self.input.text.rstrip('\n'))
        from main import ChD
        app = ChD.get_running_app()
        app.dismiss_widget()
        
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
    
    # = ============================================================== = #
    # =                             WIDGET                             = #
    # = ============================================================== = #
            
    def open_file(self,file):
        layout = ShowFileContent(md_bg_color='red',file=file)
        layout.read_file()
        self.open_widget(layout)
        
    # = ============================================================== = #
    # =                         CHANGE SETTINGS                        = #
    # = ============================================================== = #
        
    def update_settings(self):
        for setting in self.ids.keys():
            key = self.get_setting(setting)
            self.ids[setting].ids.label.text = key
            self.settings[setting] = key

    def save_settings(self):
        from main import ChD
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
                app = ChD.get_running_app()
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
    
    def select_palette(self):
        # update if any changes were made outside of app
        self.children[1]._check_text()
        
        kwargs={'itemclass':'PaletteItem','max_h':1300}
        if self.hint=='Palette':
            dialog = ShowPaletteOptions(**kwargs)
            dialog.open()
        
    @property
    def palettes(self):
        return [palette.capitalize() for palette in hex_colormap.keys()]
            
    # = ––––––––––––––––––––––––– directories –––––––––––––––––––––––– = #
        
    def select_directory(self):
        from main import ChD
        app = ChD.get_running_app()
        screen = app.wm.current_screen
        
        def select_path(path):
            self.text = path+'/'
            screen.file_manager.close()
            
        try: 
            screen.file_manager = MyFileManager(
                description=f'Decide on {self.hint.lower()}.',
                select_path=select_path,
                ext=['.____nothing____'], 
            )
            screen.file_manager.show(path=None,use_root_folder=True)
            
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
            import traceback
            print(traceback.format_exc())
         
    # = ============================================================== = #
    # =                              VALID                             = #
    # = ============================================================== = #
    
    def is_path(self,path:str):
        correct_syntax = path.endswith('/')
        exists = os.path.isdir(path)
        return correct_syntax and exists
    
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
        
