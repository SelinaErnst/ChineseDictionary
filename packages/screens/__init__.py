from .new_dict import DictionaryNew
from .upload_dict import DictionaryUpload
from .dict_chooser import DictionaryChooser
from .view_dict import ViewDict
from .settings import Settings
from .show_character import ShowCharacter

import os
from kivy.lang import Builder
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/home.kv')
Builder.load_file(current_dir+'/interface.kv')
Builder.load_file(current_dir+'/settings.kv')
Builder.load_file(current_dir+'/new_dict.kv')
Builder.load_file(current_dir+'/upload_dict.kv')
Builder.load_file(current_dir+'/dict_chooser.kv')
Builder.load_file(current_dir+'/view_dict.kv')
Builder.load_file(current_dir+'/show_character.kv')
