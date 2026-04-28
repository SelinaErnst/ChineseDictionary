import os
from functools import partial
from kivy.utils import platform
from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    ListProperty,
    NumericProperty, 
    BooleanProperty,
    ColorProperty)
from packages.chd import Dictionary, Character, encode_pinyin
from packages.kivymd_modules import (
    MyScreen,
    AttentionMsg, # snackbar
    ErrorMsg,
    AddElement,
    ConfirmDelete,
    ShowOptions,
    MyFileManager,
    ConfirmFileChoice,
    FlexTextButton,
    MyIconTextButton,
    MDStackLayout,
    MDTextField
)

class ViewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty('Dictionary Name')
    entry_count=NumericProperty()
    dictionary=ObjectProperty()
    file_format=StringProperty()
    filtered_characters=ListProperty()
    edited=BooleanProperty(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
            
    def set_up_screen(self,dict_name,dict_file="",file_format=""):
        self.toggle_search_bar(toggle=False,turn_off=True)
        self.toggle_filter(self.filter_box,self.filter,toggle=False,turn_off=True)
        self.toggle_filter(self.sorter_box,self.sorter,toggle=False,turn_off=True)
        self.dict_name = dict_name
        self.dict_file = dict_file
        # self.search_entry.text = ""
        self.file_format = file_format
        
        if dict_file != "":
            return self.__read_dict_file(file_format=self.file_format,dict_file=self.dict_file,add=False)
        else:
            self.__empty_dict()
            self.set_list_items()
            return False

    def __read_dict_file(self,dict_file,file_format=None,add=False):
        from main import ChD
        app = ChD.get_running_app()
        if not add: self.__empty_dict()

        categories=app.get_setting('categories')
        template=app.get_setting('pleco_template')
        
        can_read = self.dictionary.read(
            dict_file,file_format=file_format,add=add,categories=categories,template=template)
        if can_read:
            self.set_list_items()
            return True
        else:
            self.set_list_items()
            ErrorMsg(error='Cannot read dictionary file',msg='Possible causes: dictionary file, template, file format').open()
            return False
        
    def __empty_dict(self):
        # dictionary is created
        # method used upon first creation of dictionary
        from main import ChD
        app = ChD.get_running_app()
        self.dictionary=Dictionary(self.dict_name)
        self.entry_count=0

        
    def __get_character_image(self,character:Character,directory,image_type):
        # this method is there to get image paths from certain predetermined directories
        # basically if the image is there, I want to know 
        # if another image is already given, this method should not overwrite the path
        image_type = image_type.replace(' ','_')
        possible_image_types = ['ancient character', 'shuowen jiezi','other image']
        possible_image_types = [s.replace(' ','_') for s in possible_image_types]
        
        if image_type in possible_image_types:
            test1 = f'{image_type}/{character.unicode_unique_string}.png'
            test2 = f'{character.unicode_unique_string}_{image_type}.png'
            test3 = f'{character.unicode_unique_string}/{image_type}.png'
            file_exists = False
            if os.path.isfile(directory+test1):
                file = directory+test1
                file_exists = True
            if os.path.isfile(directory+test2):
                file = directory+test2
                file_exists = True
            if os.path.isfile(directory+test3):
                file = directory+test3
                file_exists = True
            
            image_dict = character['images']
            is_dict = isinstance(image_dict,dict)
            
            if is_dict:
                image_dict = {k:v for k,v in image_dict.items() if os.path.isfile(v)}
                if image_dict=={}: image_dict, is_dict = None, False

            # image_type only in image_dict if path leads to file
            path_correct = image_type in image_dict if is_dict else False
            
            # only change when image file exists and path is incorrect
            # incorrect: no path given or file behind path not existent
            if file_exists and not path_correct:
                kwargs={image_type:file}
                character.update_images(kwargs)
        
           
    def __create_dataitem(self,character:Character):
        char_simp, char_trad = character.uniq[:2]
        char_pron = character.pinyin
        translation = character.entry.english[0] if character.has_translation() else ""
        from main import ChD
        app = ChD.get_running_app()
        image_directory = app.get_setting('image_directory')
        self.__get_character_image(character=character,directory=image_directory,image_type='ancient character')
        self.__get_character_image(character=character,directory=image_directory,image_type='shuowen jiezi')
        images=character['images']
        preview_image = 'ancient_character'
        preview_image = images[preview_image] if images!=None and preview_image in images.keys() else None

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
            'preview_image': "" if preview_image==None else preview_image,
            }
        return dataitem 
    
    def __add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)
    
    def set_list_items(self,search_text="",search=False):
        self.rv_scroll.data = []
        
        def apply_search(search_text,search):
            if not search: search_text=""
            search_text = self.search_entry.text if search_text=="" else search_text
            if search_text!="": 
                search_dictionary = self.dictionary.search(text=search_text,exact=True,search_prompt=False)
                search_dictionary.name = search_dictionary.name + '_filtered'
                self.search_button.style = "filled"
            else:
                search_dictionary = self.dictionary
                self.search_button.style = "elevated"
            return search_dictionary
        
        def apply_sorting_key():
            if len(self.ids.sorter.include)==1:
                self.dictionary.sorting_key=self.ids.sorter.include[0]
            else:
                self.ids.sorter.include=[]
                self.ids.sorter.ids[self.dictionary.sorting_key].toggle_on()
                
        def apply_filter(dataitem):
            include,exclude = self.ids.filter.include,self.ids.filter.exclude
            fit=[]
            if 'radical' in include and dataitem['is_radical']: fit.append(True)
            elif 'radical' in exclude and not dataitem['is_radical']: fit.append(True)
            if 'measure word' in include and dataitem['is_measure_word']: fit.append(True)
            elif 'measure word' in exclude and not dataitem['is_measure_word']: fit.append(True)
            if 'grammatical' in include and dataitem['is_grammatical']: fit.append(True)
            elif 'grammatical' in exclude and not dataitem['is_grammatical']: fit.append(True)
            if 'translated' in include and dataitem['has_translation']: fit.append(True)
            elif 'translated' in exclude and not dataitem['has_translation']: fit.append(True)
            if len(fit) == len(include+exclude): return True
            else: return False

        search_dictionary=apply_search(search_text=search_text,search=search)
        apply_sorting_key()
        counter = 0
        self.filtered_characters = []
        for character in search_dictionary.sort():
            dataitem=self.__create_dataitem(character)
            if apply_filter(dataitem):
                self.filtered_characters.append(dataitem['character'].uniq)
                self.__add_list_item(dataitem)
                counter += 1
        self.entry_count = counter

    def choose_export_method(self):
        export_option = [
            f'pleco txt ({len(self.dictionary)})',
            f'jsonl ({len(self.dictionary)})',
            f'pleco txt (filter applied: {self.entry_count})',
            f'jsonl (filter applied: {self.entry_count})'
        ]
        
        kwargs={
            "title":"Export Dictionary",
            'support_text':"How do you want to export the dictionary? Depending on what you choose you can either export the entire thing or the part that is filtered.",
            "options":export_option,
            "itemclass":"MyListItem",
            "func": self.export
        }
                   
        dialog = ShowOptions(**kwargs) 
        dialog.open()

    def export(self,mode):
        self.file_manager = MyFileManager(
            # selector='folder',
            description="Decide on directory for export of dictionary",
            select_path=partial(self.__export_to_dir,mode=mode),
            ext=['.____nothing____']
        )
        self.file_manager.show()
            
    def __export_to_dir(self,path,mode):
        use_filtered = True if 'filter' in mode else False
        if 'pleco' in mode: output = 'pleco'
        elif 'jsonl' in mode: output = 'jsonl'
        else: output='all'
        if not path.endswith('/'): path+='/'
        self.save_dictionary(directory=path,use_filtered=use_filtered, output=output,make_msg=True)
        self.file_manager.close()
        
    def save_dictionary(self, output='all',make_msg=True,directory='',use_filtered=False):
        from main import ChD
        app = ChD.get_running_app()
        # path_to_template = app._MyApp__appdata+'templates/'+app.get_setting('pleco_template') 
        path_to_template=app.get_setting('pleco_template')
        if directory == "":
            app_directory = app.get_setting('app_directory')
            dict_directory = app.get_setting('dict_directory')
            if os.path.isdir(app_directory):
                os.makedirs(dict_directory+f'{self.dict_name}/', exist_ok=True)
                directory=dict_directory+f'{self.dict_name}/'
        if os.path.isdir(directory):
            if use_filtered: dictionary = self.dictionary[self.filtered_characters].copy()
            if use_filtered: dictionary = self.dictionary[self.filtered_characters]
            else: dictionary = self.dictionary
            
            if output in ['jsonl','all']:
                dictionary.write(directory=directory,filename=f'{dictionary.name}.jsonl',file_format='jsonl')
            if output in ['pleco','all']:
                dictionary.write(directory=directory,filename=f'{dictionary.name}.txt',file_format='pleco',template=path_to_template)
            if make_msg: AttentionMsg(attention='File was created',msg=f'The dictionary {dictionary.name} was stored in {directory}').open()
            app.wm.get_screen('select_dict').set_files()
            self.edited=False
            
    def del_dictionary(self):
        name = self.dict_name
        dialog = ConfirmDelete(name=name,what='dictionary')
        dialog.open()
    
    def add_character(self, mode=None):
        
        if mode == None:
            kwargs={
                "title":"Add Character To Dictionary",
                "support_text": "There are two ways to add new character(s) to the dictionary. Either import a file containing one or more characters or create a new entry.",
                "options":['Import File','New Entry'],
                "itemclass":"MyListItem",
                "func":self.add_character,
                "min_h":300
            }
            
            dialog = ShowOptions(**kwargs) 
            dialog.open()
            
        elif 'new' in mode.lower(): # Add new character
            kwargs={
                "title":'Character',
                "support_text":f"Enter the chinese characters (simplified & traditional language) amd pronunciation in pinyin.",
            }
            dialog = AddElement(**kwargs)
            dialog.open()
            
        elif 'import' in mode.lower(): # Load character file
            self.file_manager = MyFileManager(
                description="Which dictionary file should be used to add new characters",
                select_path=self.add_char_file_to_dict,
                ext=[".jsonl",'.txt'], 
            )
            self.file_manager.show()
    
    def add_char_file_to_dict(self,path):
        try:
            dialog = ConfirmFileChoice(
                dict_name=self.dict_name,
                file_name=self.file_name,
                # file_format=self.file_format,
                file_path=path,
                )
            dialog.open()
            # self.dialog = ConfirmChoice(
                    # dict_name=self.dict_name,
                    # file_name=os.path.basename(path),
                    # file_format=self.file_format,
            # )
            # self.dialog.load_file(path)
            # self.dialog.open()
        except Exception as err:
            error=f"{type(err).__name__}"
            ErrorMsg(error=error,msg=str(err)).open()
            import traceback
            print(traceback.format_exc())
            
    def add_new_char_to_dict(self,entries={}):
        from main import ChD
        app = ChD.get_running_app()
        character=Character(needed_categories=app.get_setting('categories'))
        character.update(entries)
        self.dictionary = self.dictionary + character
        self.edited = True
        self.set_list_items()
        self.show_char(character=character)
            
    def show_char(self,character:Character):
        from main import ChD, ShowCharacter
        app = ChD.get_running_app()
        # char_string = create_char_string(character=character)
        screen = ShowCharacter(character=character, dict_screen=self, parent_dictionary=self.dictionary)
        app.wm.add_widget(screen)
        app.switch_screen(screen.name,'left')

    
    def load_dictionary(self):
        if hasattr(self.dialog,'file_path'):
            add=True
            self.__read_dict_file(file_format=self.dialog.file_format, dict_file=self.dialog.file_path, add=add)

    def rename_dict(self,name):
        self.dictionary.rename(name)
        self.dict_name = name
        self.edited = True
        
    def get_new_name(self):
        kwargs={
            "title":'Dictionary Name',
            "support_text":"Edit the name of the dictionary. This is also the name of the directory under which the files will be saved.",
        }
        
        dialog = AddElement(**kwargs)
        dialog.allow_multiple = False
        dialog.content.ids.input.text = self.dict_name
        dialog.open()
    
    def toggle_search_bar(self,toggle=True,turn_off=True):
        from main import ChD
        app = ChD.get_running_app()
        if toggle:
            if not hasattr(self.search_entry,'hidden') or not self.search_entry.hidden:
                app.hide_widget(self.search_filter,do_hide=True)
                self.search_entry.hidden = True
            else:
                app.hide_widget(self.search_filter,do_hide=False)
                self.search_entry.hidden = False            
        else: 
            if turn_off:
                app.hide_widget(self.search_filter,do_hide=True)
                self.search_entry.hidden = True
            else:
                app.hide_widget(self.search_filter,do_hide=False)
                self.search_entry.hidden = False
                
    def toggle_filter(self,box,fil,toggle=True,turn_off=True):
        if toggle:
            # hide widget when it is not hidden (never has been hidden)
            if not hasattr(box,'hidden') or not box.hidden: self.__hide_toggle(box,fil,do_hide=True)
            # unhide widget when is hidden 
            else: self.__hide_toggle(box,fil,do_hide=False)
        else: 
            # hide widget when it is turned off              
            if turn_off: self.__hide_toggle(box,fil,do_hide=True)
            # unhide widget when it is turned on              
            else: self.__hide_toggle(box,fil,do_hide=False)
                
    def __hide_toggle(self,box,fil,do_hide=True):
        if hasattr(box, 'saved_attrs'):
            if not do_hide:
                (box.size_hint_y, box.height, box.opacity, 
                    fil.size_hint_y, fil.height, fil.opacity) = box.saved_attrs
                fil.height = fil.minimum_height
                box.hidden = False
                del box.saved_attrs
        elif do_hide:
            box.saved_attrs = (box.size_hint_y, box.height, box.opacity, 
                                            fil.size_hint_y, fil.height, fil.opacity)
            fil.size_hint_y, fil.height, fil.opacity = None,0,0
            box.size_hint_y, box.height, box.opacity = None,0,0
            box.hidden = True
class Toggle(MDStackLayout):
    include = ListProperty()
    exclude = ListProperty()
    
    def switch(self,child):
        # self.include=[]
        for c in self.children:
            if c == child:
                child.toggle_on()
            else:
                c.toggle_off()
                
class FilterOption(MyIconTextButton):
    active_filter=StringProperty('ignore')
    
    def toggle_on(self):
        self.active_filter = 'include'
        self.style = 'filled'
        self.parent.include.append(self.text)
        
    def toggle_off(self):
        self.active_filter = 'ignore'
        self.style = 'tonal'
        if self.text in self.parent.include: self.parent.include.remove(self.text)
        
    def toggle_two(self,only_one=True):
        from main import ChD
        app = ChD.get_running_app()
        if only_one:
            self.parent.switch(self)
        else:
            if self.active_filter == 'ignore':
                self.toggle_on()
            elif self.active_filter == 'include':
                self.toggle_off()
        app.wm.current_screen.set_list_items()

    def toggle_three(self):
        from main import ChD
        from main import ChD
        app = ChD.get_running_app()
        
        if self.active_filter == 'ignore':
            self.active_filter = 'include'
            self.style = 'filled'
            self.parent.include.append(self.text)
        elif self.active_filter == 'include':
            self.active_filter = 'exclude'
            self.style = 'tonal'
            self.parent.include.remove(self.text)
            self.parent.exclude.append(self.text)
        elif self.active_filter == 'exclude':
            self.active_filter = 'ignore'
            self.style = 'tonal'
            self.parent.exclude.remove(self.text)

        app.wm.current_screen.set_list_items()

        if self.parent.include != [] or self.parent.exclude != []:
            app.wm.current_screen.filter_button.style = 'filled'
        elif self.parent.include == [] and self.parent.exclude == []:
            app.wm.current_screen.filter_button.style = 'elevated'
            