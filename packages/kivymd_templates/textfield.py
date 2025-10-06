from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from .dialogs import ShowOptions, ShowPaletteOptions
from .snackbars import ErrorMsg

from kivy.utils import hex_colormap

from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ObjectProperty,
    ListProperty,
    )

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/textfield.kv')

# = ============================================================== = #
# =                         ONLY TEXTFIELD                         = #
# = ============================================================== = #

class EntryField(MDTextField):
    hint=StringProperty()
    is_correct=ObjectProperty()
    standard_height=NumericProperty(200)
    
    def _get_has_error(self) -> bool:
        has_error = super()._get_has_error()
        try:
            has_error = (has_error or not self.is_correct())
        except:
            pass
        return has_error
    
class Property(EntryField):
    standard_height=NumericProperty(100)

# = ============================================================== = #
# =                       TEXTFIELD AND ICON                       = #
# = ============================================================== = #

class EntryFieldWithIcon(MDBoxLayout):
    text=StringProperty()
    hint=StringProperty()
    role=StringProperty("medium")
    icon=StringProperty()
    press_button=ObjectProperty(True)
    is_correct=ObjectProperty()

class Setting(EntryFieldWithIcon):
    icon = StringProperty()
    options = ListProperty()
    icons = ListProperty()
    itemclass = StringProperty()
    list_height = NumericProperty()
    support_text = StringProperty()
    setting= StringProperty()
    
    def show_options(self):
        from main import ChD
        root = ChD.get_running_app().wm.current_screen
        # update if any changes were made outside of app
        self.children[1]._check_text()
        # information for valid entries
        kwargs={
            "title":self.hint,
            'setting':self.setting,
            "support_text":self.support_text,
            "options":self.options,
            "icons":self.icons,
            "itemclass":self.itemclass,
            "list_height":self.list_height
        }
        if kwargs['title']=='Palette':
            root.dialog = ShowPaletteOptions(**kwargs)
        else:
            root.dialog = ShowOptions(**kwargs)
            
        root.dialog.open()
    
    def get_palettes(self):
        return [palette.capitalize() for palette in hex_colormap.keys()]

    # overwriting (dont change name!)
    def is_correct(self):
        if 'directory' in self.hint.lower():
            correct_syntax = self.ids.label.text.endswith('/')
            return os.path.isdir(self.ids.label.text) and correct_syntax
        else:
            return self.ids.label.text in self.options

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
        app = ChD.get_running_app()
        if self.selection != []: self.text = str(self.selection[0])
        directory = app.get_setting('import_directory')
        try:
            if not app.wm.current_screen.check_file_format():
                self.file_format='all'
            else:
                self.file_format=app.wm.current_screen.file_format
            sc = app.switch_screen('filechooser','right')
            sc.directory = directory
            sc.file_format = self.file_format
            sc.set_files()
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()

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
        