from packages.kivymd_templates.snackbars import ErrorMsg, AttentionMsg
from packages.kivymd_templates.screens import MyScreen

import os

class Settings(MyScreen):
    
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        
    
        
    def update_settings(self):
        updater = {
            'theme_style': self.get_theme_style,
            'palette': self.get_palette,
            'app_directory': self.get_app_directory,
            'import_directory': self.get_import_directory,
        }
        for setting in self.ids.keys():
            # do the updating
            key = updater[setting]()
            self.ids[setting].ids.label.text = key
            self.settings[setting] = key

    def get_theme_style(self):
        return self.theme_cls.theme_style
    
    def get_palette(self):
        return self.theme_cls.primary_palette
    
    def get_app_directory(self):
        from main import ChD
        return ChD.get_running_app().get_setting('app_directory',default=True)
    
    def set_directory(self,setting,directory):
        if os.path.isdir(directory):
            self.ids[setting].ids.label.text = directory
            
    
    def get_import_directory(self):
        from main import ChD
        return ChD.get_running_app().get_setting('import_directory')
    
    def save_settings(self):
        from main import ChD, dump_json
        new_settings=self.settings
        correctness={}
        i=0
        for setting,obj in self.ids.items():
            if setting in self.settings.keys():
                is_correct=self.ids[setting].is_correct()
                if is_correct:
                    new_settings[setting] = self.ids[setting].ids.label.text
                correctness[self.ids[setting].hint]=is_correct
        all_true=all(correctness.values())
        if all_true:
            # make user config file 
            self.settings = new_settings
            app_directory = new_settings['app_directory'] # should only be defined initially
            config_directory=app_directory+'.config/'
            os.makedirs(config_directory, exist_ok=True)
            # save user settings (without app_directory)
            app = ChD.get_running_app()
            app.theme_cls.theme_style = new_settings['theme_style']
            app.theme_cls.primary_palette = new_settings['palette']
            
            try:
                dump_json(self.settings,config_directory+"settings.json")
                default_settings = app.load_default_settings()
                default_settings['app_directory'] = app_directory
                app.save_default_settings(default_settings=default_settings,update=False)
                app.dict_dir =  app.get_setting('import_directory')
                AttentionMsg(
                    attention='File was created',
                    msg=f'User settings were stored in {config_directory}settings.json'
                    ).open()
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
        else:
            incorrect=[k for k,v in correctness.items() if not v]
            incorrect_entries=', '.join(incorrect)
            ErrorMsg(
                error="Invalid settings",
                msg=f'Cannot save, check settings: {incorrect_entries}'
                ).open()
