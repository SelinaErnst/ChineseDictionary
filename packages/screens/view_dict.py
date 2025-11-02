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
    MyFileManager,
    ConfirmChoice,
)

class ViewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty('Dictionary Name')
    entry_count=NumericProperty()
    dictionary=ObjectProperty()
    file_format=StringProperty()
    
    def __init__(self, default=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default=default
        if platform=="linux" and self.default:
            dict_dir="/media/selina/SHARE/MyProjects/Pleco/dictionaries/MCD/"
            self.set_up_screen(dict_name="MCD",dict_file=dict_dir+"MCD.jsonl",file_format='jsonl')
            
    def set_up_screen(self,dict_name,dict_file="",file_format=""):
        self.dict_name = dict_name
        self.dict_file = dict_file
        self.search_entry.text = ""
        self.file_format = file_format
        if dict_file != "":
            return self.__read_dict_file(file_format, add=False)
        else:
            self.__empty_dict()
            self.set_list_items()
            
    def __read_dict_file(self,file_format, dict_file=None, add=False):
        if not add: self.__empty_dict()
        dict_file = dict_file if dict_file!=None else self.dict_file
        exists=os.path.exists(dict_file)
        can_read = self.dictionary.read(dict_file,file_format=file_format,add=add)
        if can_read:
            self.entry_count = len(self.dictionary.characters)
            self.set_list_items()
        else:
            self.set_list_items()
            if exists: ErrorMsg(error='Cannot read dictionary file',msg=f'File {dict_file} exists').open()
            else: ErrorMsg(error='Cannot read dictionary file',msg=f'File {dict_file} does not exist').open()
        return can_read
    
    def __empty_dict(self):
        self.dictionary=dictionary(self.dict_name)
        self.entry_count=0


    def __convert_image(self, url, file_name,directory):
        
        if url.endswith('svg') and platform != 'android':
            import cairosvg
            cairosvg.svg2png(url=url, write_to=directory+file_name, dpi=300, scale=1)
            return directory+file_name
        else:
            return "None"
    
    def __get_image_urls(self,character):
        if str(character) in self.image_urls.keys(): 
            character.entry.add_to('image_urls',self.image_urls[str(character)])
        
    def __get_character_image(self,character,directory,key):
        file_name = f'{character.unicode_unique_string()}.png'
        image_dict = character.get_property('images')
        is_dict = isinstance(image_dict,dict)
        needs_update = (is_dict and key not in image_dict) or (not is_dict)
        file_exists = os.path.isfile(directory/file_name)
        if file_exists and needs_update:
            source=(directory/file_name).as_posix()
            kwargs={key:source}
            character.update_images(kwargs)
        elif not file_exists and platform=='linux':
            if str(character) in self.image_urls.keys() \
                and self.image_urls[str(character)] != None:
                    url=self.image_urls[str(character)][0]
                    source=self.__convert_image(url=url,file_name=file_name,directory=directory.as_posix()+'/')   
                    kwargs={key:source}
                    character.update_images(kwargs)
           
    def __create_dataitem(self,character):
        char_simp, char_trad = character.uniq[:2]
        char_pron = character.show_pinyin()
        translation = character.entry.english[0] if character.has_translation() else ""
        from main import load_json, SCRIPT_DIR
        self.image_urls=load_json('image_urls.json')
        self.__get_character_image(character=character,directory=SCRIPT_DIR/'character_images'/'ancient_characters',key='ancient_image')
        self.__get_character_image(character=character,directory=SCRIPT_DIR/'character_images'/'shuowen_jiezi',key='shuowen_jiezi')
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
    
    def __add_list_item(self,dataitem,text="",search=False):
        # if search:
            # text = text.lower()
            # text = text.replace('ü','v')
            # text = dataitem["character"].remove_pinyin(text=text)
            # search_for = dataitem["char_simp"],dataitem["char_trad"],dataitem["character"].remove_pinyin()
            # if  any([text.lower() in c.lower() for c in search_for]) or text=="":
                # self.rv_scroll.data.append(dataitem)
        # else: 
        self.rv_scroll.data.append(dataitem)
    
    def set_list_items(self,text="",search=False):
        self.rv_scroll.data = []
        if self.search_entry.text != "": 
            search = True
            text = self.search_entry.text
        if search:
            search_dictionary = self.dictionary.search(text=text,exact=False,search_prompt=False)
        else:
            search_dictionary = self.dictionary
            
        for character in search_dictionary.sort():
            dataitem=self.__create_dataitem(character)
            self.__add_list_item(dataitem,text=text,search=search)

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
            "title":"Add a new character",
            "support_text": "There are two ways to add a new character to the dictionary. Either load a file containing one or more characters or add an entirely new one.",
            "options":['Load character file','Add new character'],
            "itemclass":"AddCharItem",
            "list_height":300
        }
        
        self.dialog = ShowOptions(**kwargs) 
        self.dialog.open()

    def add_new_character(self, mode):
        if mode == "new":
            kwargs={
                "title":'Character',
                "support_text":f"'-' separates these categories: simple, traditional, pronunciation",
            }
            self.dialog = AddElement(**kwargs)
            self.dialog.open()
        elif mode == "load":
            self.file_manager = MyFileManager(
                select_path=self.add_char_to_dict,
                ext=[".jsonl",'.txt'], 
            )
            self.file_manager.show()
        
    def add_char_to_dict(self,path):
        try:
            self.dialog = ConfirmChoice(
                    dict_name=self.dict_name,
                    file_name=os.path.basename(path),
                    # file_format=self.file_format,
            )
            self.dialog.load_file(path)
            self.dialog.open()
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
    
    def load_dictionary(self):
        if hasattr(self.dialog,'file_path'):
            self.__read_dict_file(file_format=self.dialog.file_format, dict_file=self.dialog.file_path, add=True)

    def rename_dict(self,name):
        self.dictionary.rename(name)
        self.dict_name = name
        
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
            
    def toggle_search_bar(self):
        from main import ChD
        app = ChD.get_running_app()
        if not hasattr(self.search_entry,'hidden') or not self.search_entry.hidden:
            app.hide_widget(self.filter,do_hide=True)
            self.search_entry.hidden = True
        else:
            app.hide_widget(self.filter,do_hide=False)
            self.search_entry.hidden = False            
            
            