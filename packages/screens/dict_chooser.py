
import os
from kivy.properties import StringProperty, ListProperty, ObjectProperty

from packages.kivy import (
    MyScreen,   
    ErrorMsg,
    AttentionMsg,
)
class DictionaryChooser(MyScreen):
    filelist=ListProperty()
    # directory=ObjectProperty()
    file_format=StringProperty()
    
    def __init__(self,*args,**kwargs):
        self.next_screen = "view_dict"
        super().__init__(file_format='jsonl',*args,**kwargs)
    
    def set_up_screen(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        self.directory=app.get_setting('dict_directory')
        self.set_files(directory=self.directory)
        
    def set_next(self,screen_name):
        self.next_screen = screen_name
        
    def set_files(self,directory=None,valid_ext=None,is_file=None):
        if directory != None and os.path.isdir(directory): self.directory = directory
        if os.path.isdir(self.directory):
            if is_file==True: 
                self.filelist=[f for f in os.listdir(self.directory) if os.path.isfile(self.directory/f)]
            elif is_file==False:
                self.filelist=[f for f in os.listdir(self.directory) if os.path.isdir(self.directory/f)]
            else:
                self.filelist=[f for f in os.listdir(self.directory)]
        else:
            self.filelist=[]
        
        if valid_ext != None and self.file_format in valid_ext.keys():
            self.filelist=[f for f in self.filelist if f.endswith(valid_ext[self.file_format])]
            
        self.options.set_options(self.filelist)
        self.options.set_list_items(func=self.select_dictionary)
        return self.filelist
    
    def select_dictionary(self, dict_dir):
        dict_path=self.directory/dict_dir

        file = [f for f in os.listdir(dict_path) if f==dict_dir+'.'+self.file_format]
        file = file[0]
        dict_file = dict_path/f'{dict_dir}.{self.file_format}'
        if os.path.isfile(dict_file):
            if self.next_screen == "view_dict": 
                self.get_screen('view_dict').set_attr(dict_name=dict_dir,dict_file=dict_file,file_format=self.file_format)
            self.switch_screen(self.next_screen,"left")
        else:
            ErrorMsg(error='File missing',msg=f'Dictionary file ({self.file_format}) does not exist.').open()