import os
from kivy.utils import platform
from kivy.metrics import dp

from kivy.properties import (
    StringProperty, 
    )

from kivymd.uix.filemanager import MDFileManager
from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/file_manager.kv')

class MyFileManager(MDFileManager):
    root_folder=StringProperty()
    description=StringProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if platform == 'android' and self.root_folder == "":
            from android.storage import primary_external_storage_path
            self.root_folder=primary_external_storage_path()
        elif self.root_folder == "":
            self.root_folder = os.path.expanduser("~")

        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.change_design())
        
    def change_design(self):
        self.ids.toolbar.ids.text_box.children[0].role = 'small'
        
        
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
            
        
    def select_dir_or_file(self, path, *args):
        """Override navigation to also update folder name when entering new directory."""
        super().select_dir_or_file(path, *args)
        if os.path.isdir(path):
            self.update_dir_name(path)
            
    def back(self) -> None:
        """Returning to the branch down in the directory tree."""

        path, end = os.path.split(self.current_path)
        if self.current_path and path == self.current_path:
            self.show_disks()
        else:
            if not end:
                self.close()
                self.exit_manager(1)
            else:
                self.show(path)
            
    def show(self, path: str=None, use_root_folder=False) -> None:
        # -----------------------------------------
        if  isinstance(path,str) and path!="/": path = path.rstrip('/')
        
        if path == None and use_root_folder:
            path=self.root_folder
        elif path == None and not use_root_folder:
            from main import ChD
            app = ChD.get_running_app()
            path = app.get_setting('app_directory')
            
        # -----------------------------------------
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.update_dir_name(path))
        # -----------------------------------------
        
        """
        Forms the body of a directory tree.

        :param path:
            The path to the directory that will be opened in the file manager.
        """

        self.current_path = path
        self.selection = []
        dirs, files = self.get_content()
        manager_list = []

        if dirs == [] and files == []:  # selected directory
            pass
        elif not dirs and not files:  # directory is unavailable
            return

        if self.preview:
            for name_dir in self._MDFileManager__sort_files(dirs):
                manager_list.append(
                    {
                        "viewclass": "MyFileManagerItemPreview",
                        "path": self.icon_folder,
                        "realpath": os.path.join(path),
                        "type": "folder",
                        "name": name_dir,
                        "events_callback": self.select_dir_or_file,
                        "height": dp(150),
                        "_selected": False,
                    }
                )
            for name_file in self._MDFileManager__sort_files(files):
                if (
                    os.path.splitext(os.path.join(path, name_file))[1]
                    in self.ext
                ):
                    manager_list.append(
                        {
                            "viewclass": "MyFileManagerItemPreview",
                            "path": os.path.join(path, name_file),
                    	    "realpath": os.path.join(path),
                            "name": os.path.basename(name_file),
                            "type": "files",
                            "events_callback": self.select_dir_or_file,
                            "height": dp(150),
                            "_selected": False,
                        }
                    )
        else:
            for name in self._MDFileManager__sort_files(dirs):
                _path = os.path.join(path, name)
                access_string = self.get_access_string(_path)
                if "r" not in access_string:
                    icon = "folder-lock"
                else:
                    icon = "folder"

                manager_list.append(
                    {
                        "viewclass": "MDFileManagerItem",
                        "path": _path,
                        "icon": icon,
                        "dir_or_file_name": name,
                        "events_callback": self.select_dir_or_file,
                        "icon_color": (
                            self.theme_cls.primaryColor
                            if not self.icon_color
                            else self.icon_color
                        ),
                        "_selected": False,
                    }
                )
            for name in self._MDFileManager__sort_files(files):
                if self.ext and os.path.splitext(name)[1] not in self.ext:
                    continue

                manager_list.append(
                    {
                        "viewclass": "MDFileManagerItem",
                        "path": name,
                        "icon": "file-outline",
                        "dir_or_file_name": os.path.split(name)[1],
                        "events_callback": self.select_dir_or_file,
                        "icon_color": (
                            self.theme_cls.primaryColor
                            if not self.icon_color
                            else self.icon_color
                        ),
                        "_selected": False,
                    }
                )

        self.ids.rv.data = manager_list
        self._show()

        