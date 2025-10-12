import os
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from packages.pleco import dictionary
from packages.kivymd_templates import (
    MyScreen,
    AttentionMsg, # snackbar
    ErrorMsg,
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
            self.set_list_items(namelist=self.dictionary.get_simple_list())
        else:
            if exists: ErrorMsg(error='Cannot read dictionary file',msg=f'File {self.dict_file} exists').open()
            else: ErrorMsg(error='Cannot read dictionary file',msg=f'File {self.dict_file} does not exist').open()
        return can_read
    
    def empty_dict(self):
        # self.dictionary=None
        self.dictionary=dictionary(self.dict_name)

    def create_dataitem(self,character):
        char_simp, char_trad, char_pron = character.uniq
        translation = character.entry.english[0] if character.has_translation() else ""
        
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
            }
        return dataitem 
    
    def add_list_item(self,dataitem,text="",search=False):
        if search:
            pass
            # if text.lower() in name.lower() or text=="":
                # self.rv_scroll.data.append(dataitem)
        else: self.rv_scroll.data.append(dataitem)
    
    def set_list_items(self,text="",namelist=None, search=False):
        self.rv_scroll.data = []
        if namelist != None and isinstance(namelist,list): 
            self.namelist=namelist
        for character in self.dictionary:
            dataitem=self.create_dataitem(character)
            self.add_list_item(dataitem,text=text,search=search)

    def save_dictionary(self, output='all'):
        from main import ChD
        app = ChD.get_running_app()
        app_directory = app.get_setting('app_directory')
        if os.path.isdir(app_directory):
            os.makedirs(app_directory+f'dictionaries/{self.dict_name}/', exist_ok=True)
            directory=app_directory+f'dictionaries/{self.dict_name}/'
        if output in ['jsonl','all']:
            self.dictionary.write(directory=directory,filename=f'{self.dict_name}.jsonl',file_format='jsonl')
        if output in ['pleco','all']:
            self.dictionary.write(directory=directory,filename=f'{self.dict_name}.txt',file_format='pleco')
        file_path=app_directory+f'dictionaries/{self.dict_name}/'
        AttentionMsg(attention='File was created',msg=f'The dictionary {self.dict_name} was stored in {file_path}').open()

    # def on_tap_entry(self,help):
        # print('HA')

    