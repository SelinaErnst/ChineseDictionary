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
    
# what to do in case smth goes wrong:
# try:
# #     ....
# except Exception as err:
#     error=f"{type(err).__name__}"
#     ErrorMsg(error=error,msg=str(err)).open()
        # import traceback
        # print(traceback.format_exc())        
        
class AttentionMsg(MDSnackbar):
    msg=StringProperty()
    attention=StringProperty("ATTENTION")