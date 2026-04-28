
import os
from kivy.properties import StringProperty, ListProperty

from packages.kivymd_modules import (
    MyScreen,   
    ErrorMsg,
    AttentionMsg,
)

class DictionaryChooser(MyScreen):
    filelist=ListProperty()
    directory=StringProperty()
    file_format=StringProperty()
    itemclass=StringProperty('MyMultiLineItem')
    
    def __init__(self,*args,**kwargs):
        super().__init__(file_format='jsonl',*args,**kwargs)
        self.set_files()
        
    def set_files(self,directory=None,valid_ext=None,is_file=None,text="",search=False):
        if directory != None and os.path.isdir(directory): self.directory = directory
        if os.path.isdir(self.directory):
            if is_file: 
                self.filelist=[f for f in os.listdir(self.directory) if os.path.isfile(self.directory+f)]
            elif not is_file:
                self.filelist=[f for f in os.listdir(self.directory) if os.path.isdir(self.directory+f)]
            else:
                self.filelist=[f for f in os.listdir(self.directory)]
        else:
            self.filelist=[]
        
        if valid_ext != None and self.file_format in valid_ext.keys():
            self.filelist=[f for f in self.filelist if f.endswith(valid_ext[self.file_format])]
            
        self.options.set_options(self.filelist)
        self.options.set_list_items(func=self.select)
        return self.filelist
    
    def select(self, dict_dir):
        dict_path=self.directory+dict_dir+'/'

        try:
            file = [f for f in os.listdir(dict_path) if f==dict_dir+'.'+self.file_format]
            file=file[0]            
            from main import ChD
            app=ChD.get_running_app()
            next_screen=app.switch_screen("view_dict","left")
            next_screen.set_up_screen(dict_name=dict_dir,dict_file=dict_path+dict_dir+f'.{self.file_format}',file_format=self.file_format)
        
        
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
            import traceback
            print(traceback.format_exc())