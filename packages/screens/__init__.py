from .new_dict import DictionaryNew
from .upload_dict import DictionaryUpload
from .dict_chooser import DictionaryChooser
from .view_dict import ViewDict
from .settings import Settings
from .show_character import ShowCharacter
from .gram_list import GrammarList
from .show_gram import ShowGrammar
from .dict_settings import *

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
Builder.load_file(str(current_dir/'dict_settings.kv'))
Builder.load_file(str(current_dir/'show_character.kv'))
Builder.load_file(str(current_dir/'gram_list.kv'))
Builder.load_file(str(current_dir/'show_gram.kv'))

from packages.kivy import (
    MyScreen,
    MDBoxLayout,
    ScreenManager,
    MDScreenManager,
    ListProperty,
    MDFadeSlideTransition,MDSharedAxisTransition,
    StringProperty,
    )
class Home(MyScreen):
    
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
class Interface(MDBoxLayout):
    pass

# class MyTransition(MDSharedAxisTransition):
#     __direction=StringProperty()
#     # direction=StringProperty()
#     transition_axis='z'
#     opposite=True
#     duration=0.5
    
#     def __int__(self,**kwargs):
#         self.__direction='left'
#         super().__init__(**kwargs)
    
#     def on_progress(self, progress):
#         try:
#             super().on_progress(progress)
#         except KeyError:
#             pass
#     def start(self, manager):
#         try:
#             super().start(manager)
#         except KeyError:
#             pass
        
#     @property
#     def direction(self):
#         return self.__direction
    
#     @direction.setter
#     def direction(self,direction):
#         self.__direction = direction
#         if direction=='right':
#             self.transition_axis='x'
#             self.opposite=False
#         elif direction=='left':
#             self.transition_axis='x'
#             self.opposite=True
#         elif direction=='down':
#             self.transition_axis='y'
#             self.opposite=False
#         elif direction=='up':
#             self.transition_axis='y'
#             self.opposite=True
#         elif direction=='in':
#             self.transition_axis='z'
#             self.opposite=False
#         elif direction=='out':
#             self.transition_axis='z'
#             self.opposite=True
            
# class WindowManager(MDScreenManager):
class WindowManager(ScreenManager):
    previous_screen_names=ListProperty()
    previous_transition_directions=ListProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.transition = MDFadeSlideTransition() 