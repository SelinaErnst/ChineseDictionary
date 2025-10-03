import os
from plyer import filechooser
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog.dialog import MDDialog
from templates import MyScreen, ErrorMsg


class MyAccessDialog(MDDialog):
    error_msg=StringProperty('text')
    

class ConfirmChoice(MDDialog):
    title=StringProperty()
    msg=StringProperty()
    count=StringProperty()
    first_line=StringProperty()
    file_name=StringProperty()
    dict_name=StringProperty()
    

class FileOpener(MDBoxLayout):
    text=StringProperty()
    hint=StringProperty()
    selection = ListProperty([])
    role=StringProperty("medium")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def choose(self):
        from main import ChD
        if self.selection != []: self.text = str(self.selection[0])
        if platform in ["linux","android"]: 
            defaultp = ChD.get_running_app().wm.current_screen.dict_dir
            sc = ChD.get_running_app().switch_screen('filechooser')
            # print(defaultp,'\n\n',os.listdir(defaultp))
            sc.namelist = os.listdir(defaultp)
            sc.directory = defaultp
            sc.set_list_items()
        elif platform == "android": 
            filechooser.open_file(on_selection=self.handle_selection)

    def handle_selection(self, selection):
        if selection != None:
            self.selection = selection
    def on_selection(self, *a, **k):
        self.update()
    def update(self):
        self.text = str(self.selection[0])
        
class SelectFile(MyScreen):
    dict_dir=StringProperty()
    dict_file=StringProperty()
    dict_name=StringProperty()
    default=True
    file_name=""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if platform=="linux":
            self.dict_dir="/media/selina/SHARE/MyProjects/Pleco/"
        elif platform=="android":
            self.dict_dir="/storage/emulated/0/Documents/Dictionaries/"
            
        if self.default:
            self.dict_file=self.dict_dir+"test.txt"
            self.dict_name="test"
            
    def check_file(self):
        entry=(self.ids.file_entry.ids.label.text)
        # print(entry)
        if os.path.isfile(entry):
            self.dict_file=str(entry)
            self.file_name=os.path.basename(entry)
            return True
        else:
            return False

    def check_name(self):
        non_valid_names=["",None," "]
        entry=(self.ids.name_entry.ids.label.text)
        # print(entry)
        if entry not in non_valid_names:
            self.dict_name=entry
            return True
        else:
            return False
        
        
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
        is_file,is_name=self.check_file(),self.check_name()
        if is_file and is_name: 
            title="Confirm choice"
            msg=f"Check if this looks like a proper choice. Especially whether this fits the wanted format."
            try:
                count,first_line=self.count_and_first_line()
                print('First Line:\n',first_line)
                ConfirmChoice(
                        dict_name=self.dict_name,
                        file_name=self.file_name,
                        title=title,
                        msg=msg,
                        count=str(count),
                        first_line=first_line
                ).open()
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
                
        else: 
            if not is_file and not is_name: msg="change the filepath and the name"
            elif not is_file: msg="change the filepath"
            elif not is_name: msg="change the name"
            ErrorMsg(error="ERROR: Not valid",msg=msg).open()
        
    def continue_on(self):
        from main import ChD
        next_screen=ChD.get_running_app().switch_screen("newdict","left")
        next_screen.dict_file=self.dict_file
        next_screen.dict_name=self.dict_name
        can_read = next_screen.read_dict_file()
        if not can_read:
            ChD.get_running_app().switch_screen('selectfile','right')
            ErrorMsg(error='ERROR: incompatible file',msg='cannot read file as dictionary').open()

class FileChooser(MyScreen):
    namelist=ListProperty()
    directory=StringProperty()
        
    def create_dataitem(self,name,other=None):
        dataitem={'text':name,'callback':lambda x:x}
        return dataitem 
    def add_list_item(self,name,dataitem,text="",search=False):
        if search:
            if text.lower() in name.lower() or text=="":
                self.rv_scroll.data.append(dataitem)
        else: self.rv_scroll.data.append(dataitem)
    def set_list_items(self,text="",namelist=None, search=False):
        self.rv_scroll.data = []
        if namelist != None and isinstance(namelist,list): 
            self.namelist=namelist
            # print(namelist)
        for name in self.namelist:
            dataitem=self.create_dataitem(name)
            self.add_list_item(name, dataitem,text=text,search=search)
    def select(self,file):
        path_file=self.directory+file
        # print(path_file)
        if os.path.isfile(path_file):
            from main import ChD
            next_screen=ChD.get_running_app().switch_screen("selectfile","right",remember=False)
            next_screen.dict_file=path_file
