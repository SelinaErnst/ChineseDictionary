import os
from plyer import filechooser
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog.dialog import MDDialog
from templates import MyScreen, ErrorMsg, EntryFieldWithIcon, ShowOptions, MyFlexTextButton


class MyAccessDialog(MDDialog):
    error_msg=StringProperty('text')
    radius=[20,20,20,20]


    
class ConfirmChoice(MDDialog):
    title=StringProperty()
    msg=StringProperty()
    count=StringProperty()
    first_line=StringProperty()
    file_name=StringProperty()
    dict_name=StringProperty()
    file_format=StringProperty()
    radius=[20,20,20,20]
    
class DialogLines(MDBoxLayout):
    head=StringProperty()

class FileOpener(EntryFieldWithIcon):
    text=StringProperty()
    hint=StringProperty()
    selection = ListProperty([])
    role=StringProperty("medium")
    file_format=StringProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def choose(self):
        from main import ChD
        if self.selection != []: self.text = str(self.selection[0])
        if self.file_format == "pleco":
            directory = ChD.get_running_app().dict_dir
        elif self.file_format == 'jsonl':
            directory = ChD.get_running_app().get_setting('app_directory')+'dictionaries/'
        try:
            print(directory)
            sc = ChD.get_running_app().switch_screen('filechooser','right')
            sc.directory = directory
            sc.set_files()
        except:
            ErrorMsg(error='No directory',msg='Cannot open directory. Please choose a file format first.').open()
        # elif platform == "android": 
        #     filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        if selection != None:
            self.selection = selection
    def on_selection(self, *a, **k):
        self.update()
    def update(self):
        self.text = str(self.selection[0])
    def is_correct(self):
        if 'file' in self.hint.lower():
            return self.parent.parent.parent.check_file()
        
class SelectFile(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty()
    file_name=StringProperty()
    file_format=StringProperty()

    def __init__(self,default=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default=default
            
        if self.default:
            from main import ChD
            self.dict_file= ChD.get_running_app().dict_dir+"test.txt"
            self.dict_name="Test"
            self.file_format='pleco'
            
    def check_file(self):
        from main import ChD
        entry=(self.ids.file_entry.ids.label.text)
        is_file=os.path.isfile(entry)
        if self.file_format == "pleco":
            directory = ChD.get_running_app().dict_dir
        elif self.file_format == 'jsonl':
            directory = ChD.get_running_app().get_setting('app_directory')+'dictionaries/'

        if is_file and directory in entry:
            self.dict_file=str(entry)
            self.file_name=os.path.basename(entry)
            return True
        else:
            return False

    def check_name(self):
        from main import ChD
        app_directory =  ChD.get_running_app().get_setting('app_directory')
        directory = app_directory+'dictionaries/'
        if os.path.isdir(app_directory): os.makedirs(directory, exist_ok=True) 
        files = set([f[:f.index('.')] for f in os.listdir(directory) if os.path.isfile(directory+f)])
        non_valid_names=set(["",None," "])
        entry=(self.ids.name_entry.text)
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
        ShowOptions(
            title='File Format',
            options=['pleco','jsonl'],
            itemclass='FileFormatItem',
            list_height=300,
            icons=['',''],
            ).open()
    
    def select_file_format(self, file_format):
        self.file_format = file_format
        self.ids.file_format.ids.label.text = file_format
        self.ids.file_entry.children[1]._check_text()
        
    def count_and_first_line(self,filepath=""):
        count=None
        if filepath=="": filepath=self.dict_file
        if os.path.isfile(filepath):
            count=0
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
                ConfirmChoice(
                        dict_name=self.dict_name,
                        file_name=self.file_name,
                        file_format=self.file_format,
                        title=title,
                        msg=msg,
                        count=str(count),
                        first_line=first_line
                ).open()
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
                
        else: 
            ErrorMsg(error="Wrong entry",msg='Cannot continue. There is an invalid entry.').open()
        
    def continue_on(self):
        from main import ChD
        next_screen=ChD.get_running_app().switch_screen("newdict",'left')
        next_screen.dict_file=self.dict_file
        next_screen.dict_name=self.dict_name
        can_read = next_screen.read_dict_file(self.file_format)
        if not can_read:
            ChD.get_running_app().previous_screen()
            ErrorMsg(error='Incompatible file',msg='Cannot read file as dictionary.').open()

class FileChooser(MyScreen):
    filelist=ListProperty()
    directory=StringProperty()
        
    def create_dataitem(self,name,other=None):
        dataitem={'text':name,'callback':lambda x:x}
        return dataitem 
    
    def add_list_item(self,name,dataitem,text="",search=False):
        if search:
            if text.lower() in name.lower() or text=="":
                self.rv_scroll.data.append(dataitem)
                
        else: self.rv_scroll.data.append(dataitem)
        
    def set_files(self,directory=None,text="",search=False):
        self.directory = self.directory if directory == None else directory
        self.rv_scroll.data = []
        self.filelist=[f for f in os.listdir(self.directory) if os.path.isfile(self.directory+f)]
        for name in self.filelist:
            dataitem=self.create_dataitem(name)
            self.add_list_item(name, dataitem,text=text,search=search)
            
    def select(self,file):
        path_file=self.directory+file
        if os.path.isfile(path_file):
            from main import ChD
            next_screen=ChD.get_running_app().switch_screen("selectfile","left",remember=False)
            next_screen.dict_file=path_file
            next_screen.dict_name=os.path.basename(path_file).split('.')[0]
