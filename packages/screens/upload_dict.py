import os
from kivy.properties import StringProperty

from packages.kivymd_modules import (
    MyScreen,   
    ErrorMsg, # snackbar
    ShowOptions, # dialog
    MyFileManager,
    ConfirmFileChoice
)

from packages.chd import _VALID_EXT, choose_file_ext
# _VALID_EXT.update({'all':list(_VALID_EXT.keys())})

class DictionaryUpload(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty()
    file_name=StringProperty()
    file_format=StringProperty()
    # valid_ext = _VALID_EXT

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
            
    def check_file(self):
        entry=(self.ids.file_entry.label.text)
        is_file=os.path.isfile(entry)
        if is_file:
            self.dict_file=str(entry)
            self.file_name=os.path.basename(entry)
            return True
        else:
            return False
        
    def __exists(self,dict_name:str=None):
        from main import ChD
        app=ChD.get_running_app()
        dict_name=self.dict_name if dict_name==None else dict_name
        return os.path.isdir(app.get_setting('dict_directory')+dict_name)

    def check_name(self):
        entry=(self.ids.name_entry.text)
        non_valid_names=set(["",None," "])
        if entry not in non_valid_names and not self.__exists(dict_name=entry):
            self.dict_name=entry
            return True
        else: return False
    
    def check_file_format(self):
        file_format = self.ids.file_format.label.text
        if file_format == "":
            self.file_format = ""
            return True
        elif choose_file_ext(file_format):
            self.file_format = choose_file_ext(file_format)
            return True
        else: return False
        
    def show_file_formats(self):
        # information for valid entries for file_format
        def select_file_format(text):
            self.ids.file_format.label.text=text
            if text=="all": self.ids.file_format.label.text=""

        dialog = ShowOptions(
            title='File Format',
            options=list(_VALID_EXT.keys()),
            itemclass='MyListItem', 
            func=select_file_format
            )
        dialog.open()
    
    def confirm(self):
        is_file,is_name,is_format=self.check_file(),self.check_name(),self.check_file_format()
        if all([is_file,is_name,is_format]): 
            try:
                dialog = ConfirmFileChoice(
                        dict_name=self.dict_name,
                        file_name=self.file_name,
                        file_format=self.file_format,
                        file_path=self.dict_file,
                        accept_func=self.load_dictionary
                )
                dialog.open()
                
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
                import traceback
                print(traceback.format_exc())
        else: 
            ErrorMsg(
                error="Wrong entry",
                msg='Cannot continue. There is an invalid entry.'
                ).open()
        
    def load_dictionary(self):
        from main import ChD
        app=ChD.get_running_app()
        error=""
        next_screen=app.switch_screen("view_dict",'left')
        can_read = next_screen.set_up_screen(dict_name=self.dict_name,dict_file=self.dict_file,file_format=self.file_format)
        if not can_read:
            error='Incompatible file'
            msg='Cannot read file as dictionary.'
            ErrorMsg(error=error,msg=msg).open()

    def choose(self):

        from main import ChD
        app = ChD.get_running_app()
        directory = app.get_setting('import_directory')
        if self.check_file_format() and self.file_format in _VALID_EXT:
            ext=_VALID_EXT[self.file_format]
        else:
            self.file_format=''
            ext=""
            
        self.file_manager = MyFileManager(
            description="Choose the dictionary file that you want to import.",
            select_path=self.select_path,
            ext=ext, 
        )
        if os.path.isdir(directory):
            self.file_manager.show(directory)
        else:  
            ErrorMsg(
                error="No import directory",
                msg='Through settings you can choose from which directory you want to import dictionary files.'
                ).open()
        
    def select_path(self, path):
        self.file_manager.close()
        self.dict_file = path
        self.dict_name = os.path.basename(path).split('.')[0]
        self.file_format=self.get_file_format(os.path.basename(path))
        
    def get_file_format(self,file):
        extension = os.path.splitext(file)[1]
        try:
            file_format = [f for f,e in _VALID_EXT.items() if extension in e][0]
            return file_format
        except:
            return ''
        
