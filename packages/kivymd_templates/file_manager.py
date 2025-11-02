import os
from kivy.utils import platform

from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    BooleanProperty, 
    DictProperty,
    ColorProperty,
    )

from kivymd.uix.filemanager import MDFileManager

class MyFileManager(MDFileManager):
    root_folder=StringProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if platform == 'android' and self.root_folder == "":
            from android.storage import primary_external_storage_path
            self.root_folder=primary_external_storage_path()
        elif self.root_folder == "":
            self.root_folder = os.path.expanduser("~")
        
    def exit_manager(self,*args):
        self.close()
        
    def update_dir_name(self, directory):
        """
        Override to show only the current folder name instead of full path.
        """
        # Extract only the folder name, not the full path
        current_folder_name = os.path.basename(directory.rstrip(os.sep))
        if not current_folder_name:  # Root folder case
            current_folder_name = directory

        if self.ids.toolbar.ids.text_box.children != []:
            self.ids.toolbar.ids.text_box.children[0].text = current_folder_name
        
    def show(self,path=None, use_root_folder=False):
        if path == None and use_root_folder:
            path=self.root_folder
        elif path == None and not use_root_folder:
            from main import ChD
            app = ChD.get_running_app()
            path = app.get_setting('app_directory')
        super().show(path)
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.update_dir_name(path))

    def select_dir_or_file(self, path, *args):
        """Override navigation to also update folder name when entering new directory."""
        super().select_dir_or_file(path, *args)
        if os.path.isdir(path):
            self.update_dir_name(path)