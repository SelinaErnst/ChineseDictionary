from kivymd.uix.snackbar import MDSnackbar
from kivy.properties import (
    StringProperty, 
    )

from kivy.lang import Builder
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'snackbars.kv'))

class MySnackbar(MDSnackbar):
    
    def open(self):
        from main import ChD
        app:ChD = ChD.get_running_app()
        app.open_snackbar(self)
        return super().open()
    
    def dismiss(self, *args):
        from main import ChD
        app:ChD = ChD.get_running_app()
        app.dismiss_snackbar()
        return super().dismiss(*args)
        
class ErrorMsg(MySnackbar):
    msg=StringProperty()
    error=StringProperty("ERROR")
    
    def open(self,msg:str=None,error:str=None):
        self.msg = msg if msg!=None else self.msg
        self.error = error if error!=None else self.error
        return super().open()
class AttentionMsg(MySnackbar):
    msg=StringProperty()
    attention=StringProperty("ATTENTION")
    
    def open(self,msg:str=None,attention:str=None):
        self.msg = msg if msg!=None else self.msg
        self.attention = attention if attention!=None else self.attention
        return super().open()