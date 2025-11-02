import os
from plyer import filechooser
# from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty

from packages.kivymd_templates import (
    MyScreen,   
    ErrorMsg, # snackbar
    ShowOptions, # dialog
    ConfirmChoice, # dialog
    MyFileManager,
)

from packages.pleco import valid_ext
valid_ext.update({'all':[]})

class SelectFile(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty()
    file_name=StringProperty()
    file_format=StringProperty()
    valid_ext = valid_ext

    def __init__(self,default=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default=default
            
        if self.default:
            from main import ChD
            self.dict_file= ChD.get_running_app().dict_dir+"test.txt"
            self.dict_name=os.path.basename(self.dict_file).rsplit('.')[0]
            self.file_format='pleco'
            
    def check_file(self):
        entry=(self.ids.file_entry.ids.label.text)
        is_file=os.path.isfile(entry)
        if is_file:
            self.dict_file=str(entry)
            self.file_name=os.path.basename(entry)
            return True
        else:
            return False

    def check_name(self):
        entry=(self.ids.name_entry.text)
        non_valid_names=set(["",None," "])
        if entry not in non_valid_names:
            self.dict_name=entry
            return True
        else:
            return False
    
    def check_file_format(self):
        file_format = self.ids.file_format.ids.label.text
        if file_format in ['pleco','jsonl']:
            self.select_file_format(file_format)
            return True
        else:
            return False
        
    def show_file_formats(self,**kwargs):
        # information for valid entries for file_format
        self.dialog = ShowOptions(
            title='File Format',
            setting='',
            options=['pleco','jsonl','all'],
            icons=['','',''],
            itemclass='FileFormatItem', 
            list_height=500,
            )
        self.dialog.open()
    
    def select_file_format(self, file_format):
        self.file_format = file_format
        self.ids.file_format.ids.label.text = file_format
        self.ids.file_entry.children[1]._check_text()
        
    def count_and_first_line(self,filepath=""):
        count=None
        if filepath=="": filepath=self.dict_file
        if os.path.isfile(filepath):
            count,first_line=0,""
            with open(filepath, "r") as f:
                first_line = f.readline().strip()
                count = sum(1 for _ in f)+1
                
        return count,first_line
    
    def confirm(self):
        is_file,is_name,is_format=self.check_file(),self.check_name(),self.check_file_format()
        if is_file and is_name and is_format: 
            try:
                self.dialog = ConfirmChoice(
                        dict_name=self.dict_name,
                        file_name=self.file_name,
                        file_format=self.file_format,
                )
                self.dialog.load_file(self.dict_file)
                self.dialog.open()
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
        else: 
            ErrorMsg(
                error="Wrong entry",
                msg='Cannot continue. There is an invalid entry.'
                ).open()
        
    def load_dictionary(self):
        from main import ChD
        app=ChD.get_running_app()
        next_screen=app.switch_screen("viewdict",'left')
        can_read = next_screen.set_up_screen(dict_name=self.dict_name,dict_file=self.dict_file,file_format=self.file_format)
        
        if not can_read:
            app.previous_screen()
            ErrorMsg(
                error='Incompatible file',
                msg='Cannot read file as dictionary.'
                ).open()

    def choose(self):

        from main import ChD
        app = ChD.get_running_app()
        directory = app.get_setting('import_directory')
        try: 
            if not self.check_file_format():
                self.file_format='all'
            self.file_manager = MyFileManager( 
                select_path=self.select_path,
                ext=self.valid_ext[self.file_format], 
            )
            self.file_manager.show(directory)
                
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
        
    def select_path(self, path):
        self.file_manager.close()
        self.dict_file = path
        self.dict_name = os.path.basename(path).split('.')[0]
        self.file_format=self.get_file_format(os.path.basename(path))
        
    def get_file_format(self,file):
        extension = os.path.splitext(file)[1]
        try:
            file_format = [f for f,e in self.valid_ext.items() if extension in e][0]
            return file_format
        except:
            return ''
        
class NameDict(MyScreen):
    # dict_file=StringProperty()
    dict_name=StringProperty('')
    # entry_count=NumericProperty()
    # dictionary=ObjectProperty()
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
        next_screen=app.switch_screen("viewdict",'left')
        next_screen.set_up_screen(dict_name=self.dict_name)
        