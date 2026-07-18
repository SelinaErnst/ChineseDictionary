from .new_dict import DictionaryNew
from .upload_dict import DictionaryUpload
from .dict_chooser import DictionaryChooser
from .view_dict import ViewDict
from .settings import Settings
from .show_character import ShowCharacter
from .gram_list import GrammarList
from .show_gram import ShowGrammar

from pathlib import Path
from kivy.lang import Builder

current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'home.kv'))
Builder.load_file(str(current_dir/'interface.kv'))
Builder.load_file(str(current_dir/'settings.kv'))
Builder.load_file(str(current_dir/'new_dict.kv'))
Builder.load_file(str(current_dir/'upload_dict.kv'))
Builder.load_file(str(current_dir/'dict_chooser.kv'))
Builder.load_file(str(current_dir/'view_dict.kv'))
Builder.load_file(str(current_dir/'show_character.kv'))
Builder.load_file(str(current_dir/'gram_list.kv'))
Builder.load_file(str(current_dir/'show_gram.kv'))

from packages.kivy import (
    MyScreen,
    MDBoxLayout,
    ScreenManager,
    ListProperty
    )
class Home(MyScreen):
    
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
class Interface(MDBoxLayout):
    pass
class WindowManager(ScreenManager):
    previous_screen_names=ListProperty()
    previous_transition_directions=ListProperty()