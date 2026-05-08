from kivy.properties import (
    DictProperty,
    StringProperty,
    ObjectProperty,
    BooleanProperty)
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from .layouts import ClickableBoxLayout
from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/images.kv')

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
                b=ImageBox(source=f, use_default=False)
                self.ids[k] = b
                self.add_widget(b)
            self.images = image_files
        
    def display_image(self,image_type,file):
        if image_type in self.images and image_type in self.ids:
            self.ids[image_type].source = file
            if self.images[image_type] == file:
                self.ids[image_type].use_default = True
        else:
            b=ImageBox(source=file, use_default=False)
            self.ids[image_type] = b
            self.images[image_type] = file
            self.add_widget(b)
                
class ImageBox(ClickableBoxLayout):
# class ImageBox(MDBoxLayout):
    source=StringProperty()
    use_default=BooleanProperty(False)
    
    def imagefile(self,source):
        from main import ChD
        default_file=ChD.get_running_app().root_folder+"appdata/images/app_icon_fg.png"
        if (not os.path.isfile(self.source) or self.use_default):
            image_file=default_file
        else:
            image_file=self.source
        return image_file        