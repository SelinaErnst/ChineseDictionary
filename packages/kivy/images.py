from kivy.properties import (
    NumericProperty,
    ListProperty,
    DictProperty,
    StringProperty,
    ObjectProperty,
    BooleanProperty)
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from .layouts import ClickableBoxLayout
from kivy.lang import Builder
import os
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'images.kv'))

class ImageDisplay(RecycleDataViewBehavior,MDStackLayout):
    images = ObjectProperty({})
    
    def __init__(self,image_files:dict={},*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.display_images(image_files)


    def refresh_view_attrs(self, rv, index, data):
        # print('BYE',data,self.images)
        if data['images']!=self.images:
            self.display_images(data['images'])

    def display_images(self,image_files={}):
        self.clear_widgets()
        if image_files != {}:
            for k,f in image_files.items():
                b=ImageBox(source=str(f), use_default=False, image_type=k)
                self.ids[k] = b
                self.add_widget(b)
            self.images = image_files
        
    def display_image(self,image_type,file):
        if image_type in self.images and image_type in self.ids:
            self.ids[image_type].source = file
            if self.images[image_type] == file:
                self.ids[image_type].use_default = True
        else:
            b=ImageBox(source=str(file), use_default=False, image_type=image_type)
            self.ids[image_type] = b
            self.images[image_type] = file
            self.add_widget(b)
                
class ImageBox(ClickableBoxLayout):
    source=StringProperty()
    use_default=BooleanProperty(False)
    image_type=StringProperty()
    
    def imagefile(self,source):
        from main import ChD
        app:ChD = ChD.get_running_app()
        # default_file=app.root_folder/"appdata"/"images"/"app_icon_fg.png"
        default_file = app.get_app_data('app_icon_fg.png','images')
        if (not os.path.isfile(self.source) or self.use_default):
            image_file=default_file
        else:
            image_file=self.source
        return str(image_file)
    
class CenterImage(MDAnchorLayout): #MDAnchorLayout
    source=StringProperty()
    max_h = NumericProperty(1000)
    min_h = NumericProperty(300)
    image_size = ListProperty([1000,1000])
    
    def msg(self):
        from .snackbars import AttentionMsg
        AttentionMsg(attention='Image File',msg=self.source).open()