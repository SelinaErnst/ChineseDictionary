from kivymd.uix.screen import MDScreen

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/screens.kv')

class MyScreen(MDScreen):
    pass
