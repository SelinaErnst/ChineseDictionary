import os
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from packages.pleco import dictionary, encode_pinyin
from packages.kivymd_templates import (
    MyScreen,
    AttentionMsg, # snackbar
    ErrorMsg,
    AddElement,
    ConfirmDelete,
    ShowOptions,
)

class ViewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty('Dictionary Name')
    entry_count=NumericProperty()
    dictionary=ObjectProperty()
    
    def __init__(self, default=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default=default
        if platform=="linux" and self.default:
            dict_dir="/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/"
            self.dict_file=dict_dir+"MCD.jsonl"
            self.dict_name="MCD"
            self.read_dict_file('jsonl')
  
    def read_dict_file(self,file_format):
        self.empty_dict()
        exists=os.path.exists(self.dict_file)
        can_read = self.dictionary.read(self.dict_file,file_format=file_format,add=False)
        if can_read:
            self.entry_count = len(self.dictionary.characters)
            self.set_list_items()
        else:
            self.set_list_items()
            if exists: ErrorMsg(error='Cannot read dictionary file',msg=f'File {self.dict_file} exists').open()
            else: ErrorMsg(error='Cannot read dictionary file',msg=f'File {self.dict_file} does not exist').open()
        return can_read
    
    def empty_dict(self):
        # self.dictionary=None
        self.dictionary=dictionary(self.dict_name)
        self.entry_count=0
    
    def rename_dict(self,name):
        self.dictionary.rename(name)
        self.dict_name = name
        

    def convert_image(self, url, file_name,directory):
        
        if url.endswith('svg') and platform != 'android':
            import cairosvg
            cairosvg.svg2png(url=url, write_to=directory+file_name, dpi=300, scale=1)
            return directory+file_name
        else:
            return "None"
    
    def get_image_urls(self,character):
        if str(character) in self.image_urls.keys(): 
            character.entry.add_to('image_urls',self.image_urls[str(character)])
        
    def get_character_image(self,character,directory,key):
        file_name = f'{character.unicode_unique_string()}.png'
        image_dict = character.get_property('images')
        is_dict = isinstance(image_dict,dict)
        needs_update = (is_dict and key not in image_dict) or (not is_dict)
        file_exists = os.path.isfile(directory/file_name)
        if file_exists and needs_update:
            source=(directory/file_name).as_posix()
            kwargs={key:source}
            character.update_images(kwargs)
        elif not needs_update:
            pass
        elif not file_exists:
            source=None
            # source=self.convert_image(url=url,file_name=file_name,directory=directory)   
           
    def create_dataitem(self,character):
        char_simp, char_trad = character.uniq[:2]
        char_pron = character.show_pinyin()
        translation = character.entry.english[0] if character.has_translation() else ""
        from main import load_json, SCRIPT_DIR
        self.image_urls=load_json('image_urls.json')
        # character.entry.remove_category('image_urls')
        # self.get_image_urls(character=character)
        self.get_character_image(character=character,directory=SCRIPT_DIR/'character_images'/'ancient_characters',key='ancient_image')
        self.get_character_image(character=character,directory=SCRIPT_DIR/'character_images'/'shuowen_jiezi',key='shuowen_jiezi')
        images=character.get_property('images')
        ancient_image = images['ancient_image'] if images!=None and 'ancient_image' in images.keys() else None

        dataitem={
            'character': character,
            'char_simp': char_simp,
            'char_trad': char_trad,
            'char_pron': char_pron,
            'is_radical': character.is_radical(),
            'is_measure_word': character.is_measure_word(),
            'is_grammatical': character.is_grammatical(),
            'has_translation': character.has_translation(),
            'translation': translation,
            'ancient_img': "" if ancient_image==None else ancient_image,
            }
        return dataitem 
    
    def add_list_item(self,dataitem,text="",search=False):
        if search:
            pass
            # if text.lower() in name.lower() or text=="":
                # self.rv_scroll.data.append(dataitem)
        else: self.rv_scroll.data.append(dataitem)
    
    def set_list_items(self,text="",search=False):
        self.rv_scroll.data = []
        for character in self.dictionary.sort():
            dataitem=self.create_dataitem(character)
            self.add_list_item(dataitem,text=text,search=search)

    def save_dictionary(self, output='all'):
        from main import ChD
        app = ChD.get_running_app()
        app_directory = app.get_setting('app_directory')
        dict_directory = app.get_setting('dict_directory')
        if os.path.isdir(app_directory):
            os.makedirs(dict_directory+f'{self.dict_name}/', exist_ok=True)
            directory=dict_directory+f'{self.dict_name}/'
            if output in ['jsonl','all']:
                self.dictionary.write(directory=directory,filename=f'{self.dict_name}.jsonl',file_format='jsonl')
            if output in ['pleco','all']:
                self.dictionary.write(directory=directory,filename=f'{self.dict_name}.txt',file_format='pleco')
            file_path=dict_directory+f'{self.dict_name}/'
            AttentionMsg(attention='File was created',msg=f'The dictionary {self.dict_name} was stored in {file_path}').open()
            app.wm.get_screen('selectdict').set_files()
            
    def delete_dictionary(self,name=None):
        name=self.dict_name if name==None else name
        self.dialog = ConfirmDelete(file=name)
        self.dialog.accept_func = self.dialog.delete_dictionary
        self.dialog.open()
    
    def add_character(self):
        kwargs={
            "title":'Character',
            "support_text":f"'-' separates these categories: simple, traditional, pronunciation",
        }
        self.dialog = AddElement(**kwargs)
        self.dialog.open()

    def get_new_name(self):
        kwargs={
            "title":'New name',
            "support_text":"Enter whatever name you want to give this dictionary.",
        }
        
        self.dialog = AddElement(**kwargs)
        self.dialog.allow_multiple = False
        self.dialog.open()
    
    def get_sorting_key(self):
        kwargs={
            "title":"Select the category",
            'support_text':"The categories shown here will contain information about the character. By selecting one of them, a new entry can be given.",
            "options":['simple','traditional','pronunciation'],
            "itemclass":"SortingKeyItem",
            "list_height":500
        }
                   
        self.dialog = ShowOptions(**kwargs) 
        self.dialog.open()
    
    def sort_dictionary(self,key=None):
        self.dictionary.sorting_key = key
        self.set_list_items()
        print('SORTING')

        
    def del_character(self,character):
        if character in self.dictionary:
            self.dictionary = self.dictionary - character
            self.set_list_items()
            self.entry_count-=1