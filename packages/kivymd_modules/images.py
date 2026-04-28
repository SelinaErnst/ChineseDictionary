from kivy.properties import StringProperty,ObjectProperty,BooleanProperty
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.boxlayout import MDBoxLayout

from .layouts import ClickableBoxLayout
from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/images.kv')

class ImageDisplay(MDStackLayout):
    images = ObjectProperty({})
    def __init__(self,image_files,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.display_images(image_files=image_files)

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
    
    @property
    def imagefile(self):
        default_file="./appdata/images/app_icon_fg.png"
        if (not os.path.isfile(self.source) or self.use_default):
            image_file=default_file
        else:
            image_file=self.source
        return image_file
    #     source: "./appdata/images/app_icon_fg.png" if not os.path.isfile(root.preview_image) else root.preview_image
        # source: "./appdata/images/app_icon_fg.png" if (not os.path.isfile(root.source) or root.use_default) else root.source
        