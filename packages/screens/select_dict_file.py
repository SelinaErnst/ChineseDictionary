import os
from plyer import filechooser
# from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty

from packages.kivymd_templates import (
    MyScreen,   
    ErrorMsg, # snackbar
    ShowOptions, # dialog
    ConfirmChoice, # dialog
    # GrantAccess, # dialog
)


class SelectFile(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty()
    file_name=StringProperty()
    file_format=StringProperty()
    # dialog=ObjectProperty()

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
            title="Confirm choice"
            msg=f"Check if this looks like a proper choice. Especially whether this fits the wanted format."
            try:
                count,first_line=self.count_and_first_line()
                self.dialog = ConfirmChoice(
                        title=title,
                        support_text=msg,
                        dict_name=self.dict_name,
                        file_name=self.file_name,
                        file_format=self.file_format,
                        count=str(count),
                        first_line=first_line
                )
                self.dialog.open()
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
        else: 
            ErrorMsg(
                error="Wrong entry",
                msg='Cannot continue. There is an invalid entry.'
                ).open()
        
    def continue_on(self):
        from main import ChD
        app=ChD.get_running_app()
        next_screen=app.switch_screen("viewdict",'left')
        # app.hide_widget(next_screen.ids.save_button,do_hide=False)
        next_screen.dict_file=self.dict_file
        next_screen.dict_name=self.dict_name
        can_read = next_screen.read_dict_file(self.file_format)
        if not can_read:
            app.previous_screen()
            ErrorMsg(
                error='Incompatible file',
                msg='Cannot read file as dictionary.'
                ).open()

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
        next_screen.dict_name=self.dict_name
        next_screen.dict_file=""
        next_screen.empty_dict()
        next_screen.set_list_items()