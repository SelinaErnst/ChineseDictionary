from kivymd.uix.screen import MDScreen
from .app import Helper
from kivy.lang import Builder
import os
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'screens.kv'))
class MyScreen(MDScreen,Helper):
    
    @property
    def my_app(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        return app

    def get_app_file(self,file:str):
        return self.my_app.get_app_file(file)
    def get_app_data(self,file:str,typ:str):
        return self.my_app.get_app_data(file,typ)
    
    def get_setting(self,*args,**kwargs):
        return self.my_app.get_setting(*args,**kwargs)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # return app.get_setting(*args,**kwargs)
    
    def get_screen(self,name):
        return self.my_app.wm.get_screen(name)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # return app.wm.get_screen(name)
    
    def switch_screen(self,*args,**kwargs):
        return self.my_app.switch_screen(*args,**kwargs)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # return app.switch_screen(*args,**kwargs)
    
    def dismiss_all(self):
        return self.my_app.dismiss_all()
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # return app.dismiss_all()
        
    def add_screen(self,screen,*args,**kwargs):
        return self.my_app.add_screen(screen,*args,**kwargs)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # app.add_screen(screen=screen,*args,**kwargs)
        
    def open_widget(self,widget):
        return self.my_app.open_widget(widget)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # app.open_widget(*args,**kwargs)
        
    # def get_screen(self,name):
    #     return self.my_app.get_screen(name)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # return app.wm.get_screen(name)
        
    def count_character(self,character):
        repeat,repeat_exact = self.my_app.check_character_for_multiple(character)
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        # repeat,repeat_exact = app.check_character_for_multiple(character)
        return len(repeat)
    
    def save_current_state(self):
        # from main import ChD
        # app:ChD=ChD.get_running_app()
        data_file = self.my_app.get_app_file('backup')
        if 'backup' in str(data_file.parent.stem).lower() and os.path.isdir(data_file.parent.parent):
            os.makedirs(data_file.parent,exist_ok=True)
        self.my_app.backup(directory=data_file.parent,filename=data_file.name)