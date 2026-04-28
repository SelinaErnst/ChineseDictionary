from kivymd.uix.screen import MDScreen

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/screens.kv')

from kivy.graphics.svg import Svg

        
class MyScreen(MDScreen):
    def __init__(self,**kwargs):
        super(MyScreen,self).__init__(**kwargs)