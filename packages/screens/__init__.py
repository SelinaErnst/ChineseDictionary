from .select_dict_file import SelectFile
from .file_chooser import DictFileChooser, DictDirChooser
from .view_dict import ViewDict
from .settings import Settings

import os
from kivy.lang import Builder
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/home.kv')
Builder.load_file(current_dir+'/interface.kv')
Builder.load_file(current_dir+'/settings.kv')
Builder.load_file(current_dir+'/select_file.kv')
Builder.load_file(current_dir+'/file_chooser.kv')
Builder.load_file(current_dir+'/view_dict.kv')
