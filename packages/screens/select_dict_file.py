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
        app.hide_widget(next_screen.ids.save_button,do_hide=False)
        next_screen.dict_file=self.dict_file
        next_screen.dict_name=self.dict_name
        can_read = next_screen.read_dict_file(self.file_format)
        if not can_read:
            app.previous_screen()
            ErrorMsg(
                error='Incompatible file',
                msg='Cannot read file as dictionary.'
                ).open()

# class FileChooser(MyScreen):
#     filelist=ListProperty()
#     directory=StringProperty()
#     file_format=StringProperty('all')
        
#     def create_dataitem(self,name,other=None):
#         dataitem={'text':name,'callback':lambda x:x}
#         return dataitem 
    
#     def add_list_item(self,name,dataitem,text="",search=False):
#         if search:
#             if text.lower() in name.lower() or text=="":
#                 self.rv_scroll.data.append(dataitem)
                
#         else: self.rv_scroll.data.append(dataitem)
        
#     def set_files(self,directory=None,text="",search=False):
#         self.directory = self.directory if directory == None else directory
#         self.rv_scroll.data = []
#         valid_exec={
#             'pleco':'.txt',
#             'jsonl':'.jsonl',
#             'all':''
#         }
#         filelist=[f for f in os.listdir(self.directory) if os.path.isfile(self.directory+f)]
#         self.filelist=[f for f in filelist if f.endswith(valid_exec[self.file_format])]
#         for name in self.filelist:
#             dataitem=self.create_dataitem(name)
#             self.add_list_item(name, dataitem,text=text,search=search)
            
#     def update(self):
#         from main import ChD
#         self.directory = ChD.get_running_app().get_setting('import_directory')
#         self.set_files()
                    
#     def select(self,file):
#         path_file=self.directory+file
#         if os.path.isfile(path_file):
#             from main import ChD
#             next_screen=ChD.get_running_app().switch_screen("selectfile","left",remember=False)
#             next_screen.dict_file=path_file
#             next_screen.dict_name=os.path.basename(path_file).split('.')[0]

            
#     def _show_validation_dialog(self):   
#         if platform == "android":
#             from jnius import autoclass
#             Environment = autoclass("android.os.Environment")
#             if not Environment.isExternalStorageManager():
#                 support_text="To access files on the phone it is required to grant the app access to the storage."
#                 deny_text='No'
#             else:
#                 support_text="Storage access was already granted."
#                 deny_text='Return'
#         elif platform == "linux":
#                 support_text=f"For {platform} no further storage access needs to be granted."
#                 deny_text='Return'

#         self.show_permission_popup = GrantAccess(
#             support_text=support_text, deny_text=deny_text)
#         self.show_permission_popup.open()