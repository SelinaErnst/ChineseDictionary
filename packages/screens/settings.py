import os
import traceback
from packages.kivymd_modules import (
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
        self.settings = self.get_settings()
        
    def get_settings(self):
        from main import ChD
        app = ChD.get_running_app()
        return app.settings
        
    def update_settings(self):
        for setting in self.ids.keys():
            # do the updating
            # key = updater[setting]()
            from main import ChD
            key = ChD.get_running_app().get_setting(setting)
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
                
                # AttentionMsg(
                #     attention='User settings saved',
                #     msg=''
                #     ).open()
                
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
            
    def open_file(self,file):
        from main import ChD
        app = ChD.get_running_app()
        layout = ShowFileContent(md_bg_color='red',file=file)
        layout.read_file()
        app.open_widget(layout)

class Setting(EntryFieldWithIcon):
    icon = StringProperty()
    options = ListProperty() # determines valid entries
    icons = ListProperty()
    itemclass = StringProperty()
    # list_height = NumericProperty()
    support_text = StringProperty()
    setting= StringProperty()
    
    def show_options(self):
        from main import ChD
        root = ChD.get_running_app().wm.current_screen
        # update if any changes were made outside of app
        self.children[1]._check_text()
        
        kwargs={'itemclass':'PaletteItem','max_h':1300}
        if self.hint=='Palette':
            dialog = ShowPaletteOptions(**kwargs)
            dialog.open()
        
    def choose_directory(self):
        from main import ChD
        app = ChD.get_running_app()
        
        try: 
            app.wm.current_screen.file_manager = MyFileManager(
                description=f'Decide on {self.hint.lower()}.',
                select_path=self.select_path,
                ext=['.____nothing____'], 
            )
            app.wm.current_screen.file_manager.show(use_root_folder=True)
                
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
            import traceback
            print(traceback.format_exc())
            
    def select_path(self, path):
        self.text = path+'/'
        from main import ChD
        app = ChD.get_running_app()
        app.wm.current_screen.file_manager.close()
         
    def get_palettes(self):
        return [palette.capitalize() for palette in hex_colormap.keys()]
    
    def switch_theme(self):
        from main import ChD
        ChD.get_running_app().switch_theme()
        self.ids.label.text = self.theme_cls.theme_style

    # overwriting (dont change name!)
    def is_correct(self):
        if 'directory' in self.hint.lower():
            correct_syntax = self.ids.label.text.endswith('/')
            return os.path.isdir(self.ids.label.text) and correct_syntax
        elif 'palette' in self.hint.lower():
            correct = self.ids.label.text in self.options
            if correct: self.theme_cls.primary_palette = self.ids.label.text
            return correct
        elif 'theme' in self.hint.lower():
            correct = self.ids.label.text in ['Light','Dark']
            if correct: self.theme_cls.theme_style = self.ids.label.text
            return correct
        else:
            return self.ids.label.text in self.options
        
