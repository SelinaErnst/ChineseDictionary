import os
from kivy.properties import StringProperty

from packages.kivymd_modules import (
    MyScreen,   
)


class DictionaryNew(MyScreen):
    dict_name=StringProperty('')

    def check_name(self):
        entry=(self.ids.name_entry.text)
        non_valid_names=set(["",None," "])
        if entry not in non_valid_names:
            self.dict_name=entry
            return True
        else:
            return False
    def confirm(self):
        is_name=self.check_name()
        if is_name: self.continue_on()
    
    def continue_on(self):
        from main import ChD
        app=ChD.get_running_app()
        next_screen=app.switch_screen("view_dict",'left')
        next_screen.set_up_screen(dict_name=self.dict_name)
        