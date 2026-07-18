from kivymd.uix.screen import MDScreen

from kivy.lang import Builder
import os
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'screens.kv'))
class MyScreen(MDScreen):
    def __init__(self,**kwargs):
        super(MyScreen,self).__init__(**kwargs)
    
    @property
    def root_folder(self):
        from main import ChD
        app = ChD.get_running_app()
        return app.root_folder
        
    def get_setting(self,*args,**kwargs):
        from main import ChD
        app = ChD.get_running_app()
        return app.get_setting(*args,**kwargs)
    
    def get_screen(self,name):
        from main import ChD
        app = ChD.get_running_app()
        return app.wm.get_screen(name)
    
    def switch_screen(self,*args,**kwargs):
        from main import ChD
        app=ChD.get_running_app()
        return app.switch_screen(*args,**kwargs)
    
    def dismiss_all(self):
        from main import ChD
        app=ChD.get_running_app()
        if app.dismiss_dialog():
            return True
        elif app.file_manager_back():
            return True
        elif app.dismiss_widget():
            return True
        else:
            return False
        
    def add_screen(self,screen,*args,**kwargs):
        from main import ChD
        app=ChD.get_running_app()
        app.add_screen(screen=screen,*args,**kwargs)
        
    def open_widget(self,*args,**kwargs):
        from main import ChD
        app=ChD.get_running_app()
        app.open_widget(*args,**kwargs)
        
    def get_screen(self,name):
        from main import ChD
        app=ChD.get_running_app()
        return app.wm.get_screen(name)
        
    def hide_widget(self,*args,**kwargs):
        from main import ChD
        app=ChD.get_running_app()
        app.hide_widget(*args,**kwargs)
        
    def import_file(self,src_path, dest_dir, new_name:str="",inform=False):
        if new_name=="": new_name=src_path.name
        dest_path = dest_dir/new_name
        try:
            import shutil
            shutil.copyfile(src_path, dest_path)
            if inform: 
                from packages.kivy import AttentionMsg
                AttentionMsg(attention='File was imported',msg=f'Copied from {src_path} to {dest_path}').open()
            return True
        except Exception as err:
            import traceback
            print(traceback.format_exc())   
            return False
        
    def remove_file(self,src_path):
        if os.path.isfile(src_path): os.remove(src_path)
    
    def count_character(self,character):
        from main import ChD
        app=ChD.get_running_app()
        repeat,repeat_exact = app.check_character_for_multiple(character)
        return len(repeat)