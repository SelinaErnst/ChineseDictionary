from kivymd.uix.snackbar import MDSnackbar
from kivy.properties import (
    StringProperty, 
    )

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/snackbars.kv')


class ErrorMsg(MDSnackbar):
    msg=StringProperty()
    error=StringProperty("ERROR")
    
class AttentionMsg(MDSnackbar):
    msg=StringProperty()
    attention=StringProperty("ATTENTION")