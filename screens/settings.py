from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    ColorProperty,
    BooleanProperty
    )
from kivymd.uix.dialog.dialog import MDDialog
from templates import (
    MyScreen, 
    EntryFieldWithIcon, 
    ErrorMsg, 
    CustomListItem,
    AttentionMsg,
    ShowOptions,
    )
from kivy.utils import hex_colormap

import os
import json


class Setting(EntryFieldWithIcon):
    icon = StringProperty()
    options = ListProperty()
    icons = ListProperty()
    itemclass = StringProperty()
    list_height = NumericProperty()
    support_text = StringProperty()
    
    def show_options(self):
        # update if any changes were made outside of app
        self.children[1]._check_text()
        # information for valid entries
        ShowOptions(
            title=self.hint,
            support_text=self.support_text,
            options=self.options,
            icons=self.icons,
            itemclass=self.itemclass,
            list_height=self.list_height
            ).open()
    
    def get_palettes(self):
        return [palette.capitalize() for palette in hex_colormap.keys()]

    # overwriting (dont change name!)
    def is_correct(self):
        if 'directory' in self.hint.lower():
            correct_syntax = self.ids.label.text.endswith('/')
            return os.path.isdir(self.ids.label.text) and correct_syntax
        else:
            return self.ids.label.text in self.options

class Settings(MyScreen):
    
    def __init__(self, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = settings
        
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
            dump_json(self.settings,config_directory+"settings.json")
            default_settings = app.load_default_settings()
            if app_directory != app.get_setting('app_directory',settings=default_settings):
                default_settings['app_directory'][app.platform] = app_directory
                dump_json(default_settings,"appdata/default_settings.json")
                
            # change variable 
            app.dict_dir =  app.get_setting('import_directory')
            AttentionMsg(attention='File was created',msg=f'User settings were stored in {config_directory}settings.json').open()
        else:
            incorrect=[k for k,v in correctness.items() if not v]
            incorrect_entries=', '.join(incorrect)
            ErrorMsg(msg=f'Cannot save, check settings: {incorrect_entries}').open()

class PaletteItem(CustomListItem):
    text = StringProperty()
    color = ColorProperty()
    color_onea = ColorProperty()
    color_oneb = ColorProperty()
    color_onec = ColorProperty()
    color_oned = ColorProperty()
    color_onee = ColorProperty()
    color_onef = ColorProperty()
    color_oneg = ColorProperty()
    color_twoa = ColorProperty()
    color_twob = ColorProperty()
    color_twoc = ColorProperty()
    color_twod = ColorProperty()
    color_twoe = ColorProperty()
    color_twof = ColorProperty()
    color_trea = ColorProperty()
    color_treb = ColorProperty()
    color_trec = ColorProperty()
    color_tred = ColorProperty()
    color_tree = ColorProperty()
    color_tref = ColorProperty()