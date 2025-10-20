
import os
from kivy.properties import StringProperty, ListProperty

from packages.kivymd_templates import (
    MyScreen,   
    ErrorMsg,
    AttentionMsg,
)



class FileChooser(MyScreen):
    filelist=ListProperty()
    directory=StringProperty()
    file_format=StringProperty()
    
    def create_dataitem(self,name,other=None):
        dataitem={'text':name,'callback':lambda x:x}
        return dataitem 
    
    def add_list_item(self,name,dataitem,text="",search=False):
        if search:
            if text.lower() in name.lower() or text=="":
                self.rv_scroll.data.append(dataitem)
                
        else: self.rv_scroll.data.append(dataitem)
        
    def set_files(self,directory=None,valid_ext=None,is_file=None,text="",search=False):
        self.directory = self.directory if directory == None else directory
        self.rv_scroll.data = []
        
        if os.path.isdir(self.directory):
            if is_file: 
                self.filelist=[f for f in os.listdir(self.directory) if os.path.isfile(self.directory+f)]
            elif not is_file:
                self.filelist=[f for f in os.listdir(self.directory) if os.path.isdir(self.directory+f)]
            else:
                self.filelist=[f for f in os.listdir(self.directory)]
        else:
            ErrorMsg(error='No directory found',msg=f'The directory {self.directory} does not exist').open()
        
        if valid_ext != None and self.file_format in valid_ext.keys():
            self.filelist=[f for f in self.filelist if f.endswith(valid_ext[self.file_format])]
            
        for name in self.filelist:
            dataitem=self.create_dataitem(name)
            self.add_list_item(name, dataitem,text=text,search=search) 

class DictDirChooser(FileChooser):
    file_format=StringProperty('jsonl')
    directory=StringProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.set_files()
        
    def set_files(
        self, 
        directory=None,
        text="", 
        search=False
        ):
        if directory != None and os.path.isdir(directory): self.directory = directory
        return super().set_files(self.directory, valid_ext=None, is_file=False, text=text, search=search)
    
    def select(self, dict_dir):
        dict_path=self.directory+dict_dir+'/'
        file = [f for f in os.listdir(dict_path) if f.endswith(self.file_format)]
        if len(file) > 1: AttentionMsg.open(attention='Multiple options',msg='There is more than one file (jsonl) that fits. Only one was selected.')
        else:
            from main import ChD
            file=file[0]            
            app=ChD.get_running_app()
            next_screen=app.switch_screen("viewdict","left")
            next_screen.dict_file=dict_path+dict_dir+f'.{self.file_format}'
            next_screen.dict_name=dict_dir
            # app.hide_widget(next_screen.ids.save_button)
            can_read = next_screen.read_dict_file(self.file_format)
        
class DictFileChooser(FileChooser):
    file_format=StringProperty('all')
    valid_ext={
        'pleco':'.txt',
        'jsonl':'.jsonl',
        'all':''
    }
    def set_files(
        self, 
        directory=None, 
        is_file=True, 
        text="", 
        search=False
        ):
        return super().set_files(directory, self.valid_ext, is_file, text, search)
            
    def update(self):
        from main import ChD
        self.directory = ChD.get_running_app().get_setting('import_directory')
        self.set_files()
                    
    def select(self,file):
        path_file=self.directory+file
        if os.path.isfile(path_file):
            from main import ChD
            next_screen=ChD.get_running_app().switch_screen("selectfile","left",remember=False)
            next_screen.dict_file=path_file
            next_screen.dict_name=os.path.basename(path_file).split('.')[0]
            next_screen.file_format=self.get_file_format(file)
        
    def get_file_format(self,file):
        extension = os.path.splitext(file)[1]
        try:
            file_format = [f for f,e in self.valid_ext.items() if e == extension][0]
            return file_format
        except:
            return ''