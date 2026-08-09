import os
from pathlib import Path
from functools import partial
from kivy.utils import platform
from kivy.properties import (
    ObjectProperty, 
    StringProperty, 
    DictProperty,
    ListProperty,
    NumericProperty, 
    BooleanProperty,
    )
from packages.chd import Dictionary, Character, encode_pinyin
from packages.kivy import (
    MyScreen,
    AttentionMsg, # snackbar
    ErrorMsg,
    Toggle,
    IconTextToggleButton,
    TextToggleButton,
    IconToggleButton,
)

class ViewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty('Dictionary Name')
    entry_count=NumericProperty()
    dictionary:Dictionary=ObjectProperty(Dictionary())
    file_format=StringProperty()
    filtered_characters=ListProperty()
    edited=BooleanProperty(False)
    config=DictProperty()
    
    def __init__(self, *args, **kwargs):
        
        self.__update_filter()
        super().__init__(*args, **kwargs)
        self.toggle_search_bar(toggle=False,turn_off=True)
        self.toggle_filter(self.filter_box,self.filter,toggle=False,turn_off=True)
        self.toggle_filter(self.sorter_box,self.sorter,toggle=False,turn_off=True)
        
    def __update_filter(self):
        
        filter_cat = self.get_app_data('filter_categories.json','defaults')
        preview_categories = filter_cat['filter']
        filter_icons = filter_cat['preview']
        
        preview_categories = {k:v for k,v in preview_categories.items() 
                              if k in filter_icons or any([cat in self.get_setting('categories') for cat in v])}
        
        self.filter_icons = {k:filter_icons[k] if k in filter_icons else "" for k in preview_categories}
        self.preview_categories = preview_categories
        
        filter_number = len(self.preview_categories)
        self.__conditions = [(list(self.preview_categories)[i-1],f'cond_{i}') for i in range(1,filter_number+1)]
        self.__preview_symbols = {cond:filter_icons[call] for call,cond in self.__conditions if call in  filter_icons}
            
    # = ============================================================== = #
    # =                             SCREEN                             = #
    # = ============================================================== = #
    
    def set_attr(self,dict_name,dict_file,file_format=None):
        self.dict_name = dict_name
        self.dict_file = str(dict_file)
        self.file_format = Path(dict_file).suffix if file_format==None else file_format
            
    def set_up_screen(self):
        if self.edited: return None
        self.__read_dict_file(file_format=self.file_format,dict_file=self.dict_file,add=False)
        
    def show_char(self,character:Character):
        screen = self.my_app.pre_loaded_widgets['character']
        screen.set_background(dict_screen=self, parent_dictionary=self.dictionary, config=self.config)
        screen.build_scroll(character=character)
        self.add_screen(screen=screen,direction='left')
        
        
    # = ============================================================== = #
    # =                           LIST ITEMS                           = #
    # = ============================================================== = #
    
    def set_list_items(self,search_text="",update_images=False,sort_key=None,sort_order=None):
        self.rv_scroll.data = []
        if sort_order == None: sort_order = self.ids.sorter.ids['switch'].switch
        if sort_key == None: sort_key = self.dictionary.sorting_key
        
        def apply_search(search_text):
            search_text = self.search_entry.text if search_text=="" else search_text
            if search_text=="": return self.dictionary
                       
            if 'translation' in self.preview_categories:
                valid = self.preview_categories['translation']
                cats = set(self.dictionary[0].filled) & set(valid)
                has_transl=bool(cats)
            
            try: 
                int(search_text)
                search_dictionary = self.dictionary.search_category(category='radical',text=search_text,exact=True)
                search_dictionary += self.dictionary.search_category(category=list(cats),text=search_text,exact=True)
            except:
                search_dictionary = self.dictionary.search(text=search_text,exact=True,search_prompt=False)
                search_dictionary.name = search_dictionary.name + '_filtered'

                if (len(search_dictionary)==0 and has_transl):
                    search_dictionary += self.dictionary.search_category(category=list(cats),text=search_text,exact=True)
            
            return search_dictionary
        
        def apply_sorting(dictionary,sort_key,sort_order):
            key_selection = self.ids.sorter.include
            if len(key_selection) != 1:
                self.ids.sorter.include=[]
                self.ids.sorter.ids[sort_key].toggle_on()
                return dictionary
            sort_key = self.ids.sorter.include[0]
            dictionary.reorder(key=sort_key,order=sort_order)
            return dictionary
        
        def apply_filter(dataitem):
            include,exclude = self.ids.filter.include,self.ids.filter.exclude
            relevant_categories = include+exclude
            for call,cond in self.__conditions:
                if call in relevant_categories:
                    if call in include and dataitem[cond]: continue
                    if call in exclude and not dataitem[cond]: continue
                    else: return False
            return True
                    
        search_dictionary=apply_search(search_text)
        sorted_dictionary=apply_sorting(search_dictionary,sort_key,sort_order)
        
        counter = 0
        self.filtered_characters = []
        for character in sorted_dictionary:
            dataitem=self.__create_dataitem(character, update_images=update_images)
            if apply_filter(dataitem):
                self.filtered_characters.append(dataitem['character'].uniq)
                self.__add_list_item(dataitem)
                counter += 1
        self.entry_count = counter 
        
    def __create_dataitem(self,character:Character, update_images=False):
        char_simp, char_trad = character.uniq[:2]
        char_pron = character.pinyin
        
        if update_images: self.get_character_image(character=character)
        images=character['images']
        image_type = self.config['preview_image']
        if images!=None:
            images={k:v for k,v in images.items() if v!=None}
            images=images if images!={} else None
            character.update({'images':images})
        if images!=None and image_type in images.keys():
            if os.path.isfile(images[image_type]):
                preview_image = str(images[image_type])
            elif not os.path.isfile(images[image_type]):
                preview_image = str(self.get_app_data('app_icon_fg.png','images'))
            else:
                preview_image = ""
        else: preview_image = ""

        def is_valid(character,category):
            if category in self.preview_categories:
                valid=self.preview_categories[category]
                return bool(set(character.filled) & set(valid))
            else: return False
            
        def get_example(character,category):
            if is_valid(character,category):
                example = ""
                for cat in self.preview_categories[category]:
                    if character[cat] != None:
                        example = str(character[cat][0])
                        break
            else: example = ""
            return example
        
        example_category = self.__conditions[0][0] if self.__conditions!=[] else ""
            
        dataitem={
            'character': character,
            'char_simp': char_simp,
            'char_trad': char_trad,
            'char_pron': char_pron,
            'cond_map': self.__preview_symbols,
            'example': get_example(character,example_category),
            'preview_image': preview_image,
            'image_type': image_type
            }
        dataitem.update({cond: is_valid(character,call) for call,cond in self.__conditions})
        return dataitem 
    
    def __add_list_item(self,dataitem):
        self.rv_scroll.data.append(dataitem)

    # = ============================================================== = #
    # =                           DICTIONARY                           = #
    # = ============================================================== = #
    
    # = –––––––––––––––––––––––––––– read –––––––––––––––––––––––––––– = #
    
    def __read_dict_file(self,dict_file,file_format=None,add=False):
        if not add: self.__empty_dict()
        else: self.edited = True
        
        self.get_dict_config()
        
        sort_key=self.config['sort_key']
        sort_order=self.config['sort_order']
        template=self.config['template']
        
        can_read = self.dictionary.read(dict_file,
            file_format=file_format,
            add=add,
            categories=self.get_setting('categories'),
            template=template,
            name=self.dict_name)
        
        if not can_read: self.__empty_dict()
        self.set_list_items(update_images=can_read,sort_key=sort_key,sort_order=sort_order)
    
    def get_dict_config(self):
        from main import ChD
        app:ChD = ChD.get_running_app()
        
        config_filename=f'{self.dict_name.lower().replace(" ","_")}_config.json'
        config_file = Path(self.dict_file).parent/config_filename
            
        config = {'name':self.dict_name,'categories':{},'template':"",'sort_key':'pronunciation','sort_order':'ascending','preview_image':''}
        
        if not os.path.isfile(config_file):
            categories = app.get_categories()
            updater = {'categories':list(categories)}
            config.update(updater)
        else:
            updater = app.load_json(config_file)
            if updater['name'] == self.dict_name:
                config.update(updater)
                
        self.config=config
        return config
            
    def save_dict_config(self):
        from main import ChD
        app = ChD.get_running_app()
        config_filename=f'{self.dict_name.lower().replace(" ","_")}_config.json'
        config_file = Path(self.dict_file).parent/config_filename
        self.config.update({'sort_key':self.dictionary.sorting_key,'sort_order':self.dictionary.sorting_order})
        app.dump_json(self.config,config_file)
        
    # = ––––––––––––––––––––––––––– remove ––––––––––––––––––––––––––– = #
            
    def __empty_dict(self):
        # dictionary is created
        # method used upon first creation of dictionary
        self.dictionary.empty()
        self.dictionary.rename(self.dict_name)
        self.dictionary.set_grammar(self.get_screen('gram_list').grammar_list)
        self.entry_count=0
    
    def del_dictionary(self):
        name = self.dict_name
        dialog = self.my_app.pre_loaded_widgets['delete_dict']
        dialog.set_attrs(name=name)
        dialog.open()
        
    # = –––––––––––––––––––––––––––– save –––––––––––––––––––––––––––– = #
        
        
    def save_dictionary(self, output='jsonl',make_msg=True,directory=None,use_filtered=False,use_tag=False):

        template = self.config['template']
        path_to_template = self.get_setting('template_directory')/f'{template}.chd'
            
        if directory == None:
            dict_directory = self.get_setting('dict_directory')
            if os.path.isdir(dict_directory):
                os.makedirs(dict_directory/f'{self.dict_name}', exist_ok=True)
                directory=dict_directory/f'{self.dict_name}'
            self.save_dict_config()
            # self.save_current_state()
            
        if os.path.isdir(directory):
            
            if use_filtered: dictionary = self.dictionary[self.filtered_characters]
            else: dictionary = self.dictionary
            if use_tag: name_tag = f'_{str(len(dictionary))}'
            else: name_tag = ""
            
            from packages.chd import _VALID_EXT
            if output in _VALID_EXT['.jsonl']:
                dictionary.write(directory=directory,filename=f'{dictionary.name}{name_tag}',file_format='jsonl')
            if output in _VALID_EXT['.db']:
                dictionary.write(directory=directory,filename=f'{dictionary.name}{name_tag}',file_format='db')
            if output in _VALID_EXT['.txt']:
                categories = self.config['categories']
                categories = {k:v for k,v in self.get_setting('categories').items() if k in categories}
                dictionary.copy().write(
                    directory=directory,
                    filename=f'{dictionary.name}{name_tag}',
                    file_format='pleco',
                    template=path_to_template,
                    categories=categories)
                
            if make_msg: AttentionMsg(attention='File was created',msg=f'The dictionary {dictionary.name} was stored in {directory}').open()

            self.get_screen('select_dict').set_files()
            self.edited=False
        
    def export(self):
        
        def export_to_dir(path,mode):
            use_filtered = True if 'filter' in mode else False
            if 'pleco' in mode: output = 'txt'
            elif 'jsonl' in mode: output = 'jsonl'
            elif 'backup' in mode: output = 'db'
            else: output='all'
            if os.path.isdir(path): 
                from pathlib import Path
                path = Path(path)
            self.save_dictionary(directory=path,use_filtered=use_filtered, output=output,make_msg=True,use_tag=True)
            self.file_manager.close()
        
        def export_path(mode):

            kwargs = {
                'description' : "Decide on directory for export of dictionary",
                'select_path' : partial(export_to_dir,mode=mode),
                'ext' : ['.____nothing____'],
            }
            self.file_manager = self.my_app.pre_loaded_widgets['file_manager']
            self.file_manager.set_attrs(**kwargs)
            self.file_manager.show(path=None,use_root_folder=False)
        
        export_option = [
            f'pleco txt ({len(self.dictionary)})',
            f'jsonl ({len(self.dictionary)})',
            f'backup to db ({len(self.dictionary)})',
            f'pleco txt (filter applied: {self.entry_count})',
            f'jsonl (filter applied: {self.entry_count})'
        ]
        
        kwargs={
            "title":"Export Dictionary",
            'support_text':"How do you want to export the dictionary? Depending on what you choose you can either export the entire thing or the part that is filtered.",
            "options":export_option,
            "itemclass":"MyListItem",
            "func": export_path
        }
        dialog = self.my_app.pre_loaded_widgets['options']
        dialog.list_options(**kwargs)
        dialog.open()
                
    # = ============================================================== = #
    # =                              EDIT                              = #
    # = ============================================================== = #
    
    # = ––––––––––––––––––––––––– dictionary ––––––––––––––––––––––––– = #
    
    def add_character(self, mode:str|None=None, entries:dict={}):
        
        def add_new_char(**entries):
            character=Character(needed_categories=self.get_setting('categories'))
            character.update(entries)
            self.dictionary = self.dictionary + character
            self.edited = True
            self.get_character_image(character=character)
            self.set_list_items(update_images=False)
            self.show_char(character=character)
            
        def choose_char_file(path):

            try:
                self.file_manager.close()
                add_another_dictionary = lambda: self.__read_dict_file(dict_file=path,file_format=None, add=True)
                
                dialog = self.my_app.pre_loaded_widgets['file_choice']
                dialog.choose_action(deny_func=None,accept_func=add_another_dictionary)
                dialog.load_file(file=path)
                dialog.open()
            except Exception as err:
                error=f"{type(err).__name__}"
                ErrorMsg(error=error,msg=str(err)).open()
                import traceback
                print(traceback.format_exc())
        
        if entries != {}:
            add_new_char(**entries)
        
        elif entries == {}:
            if mode == None:
                kwargs={
                    "title":"Add Character To Dictionary",
                    "support_text": "There are two ways to add new character(s) to the dictionary. Either import a file containing one or more characters or create a new entry.",
                    "options":['Import File','New Entry'],
                    "itemclass":"MyListItem",
                    "func":self.add_character,
                }
                dialog = self.my_app.pre_loaded_widgets['options']
                dialog.list_options(**kwargs)
                dialog.open()
                
            elif 'new' in mode.lower(): # Add new character
                kwargs={
                    "title":'Character',
                    "support_text":f"Enter the chinese characters (simplified & traditional language) amd pronunciation in pinyin.",
                }
                dialog = self.my_app.pre_loaded_widgets['edit_element']
                dialog.choose_content(style="normal",**kwargs)
                dialog.set_entry('- \n- \n- ')
                dialog.open()
                
            elif 'import' in mode.lower(): # Load character file
                
                kwargs = {
                    'description' : "Which dictionary file should be used to add new characters",
                    'select_path' : choose_char_file,
                    'ext' : [".jsonl"],
                }
                self.file_manager = self.my_app.pre_loaded_widgets['file_manager']
                self.file_manager.set_attrs(**kwargs)
                self.file_manager.show(path=None,use_root_folder=False)

    # = –––––––––––––––––––––––––––– name –––––––––––––––––––––––––––– = #
    
    def rename_dict(self,name):
        self.dictionary.rename(name)
        self.dict_name = name
        self.edited = True
        
    def edit_settings(self):
        screen = self.my_app.pre_loaded_widgets['dict_settings']
        screen.set_attrs(dict_name=self.dict_name,dict_file=self.dict_file,config=self.config)
        # from packages.screens import DictSettings
        # screen = DictSettings(dict_name=self.dict_name,dict_file=self.dict_file,config=self.config)
        self.open_widget(screen)
        
    # = –––––––––––––––––––––––––– character ––––––––––––––––––––––––– = #
    
    def get_character_image(self,character:Character):
        """
        This is just a terrible function but with an important GOAL:
        # this method is there to get image paths from certain predetermined directories
        # basically if the image is there, I want to know 
        # if another image is already given, this method should not overwrite the path
        # HOWEVER: images with different path are still copied to image directory 
        """
        directory = self.get_setting('image_directory')
        
        if not os.path.isdir(directory): return None
        character_string = character.unicode_unique_string
        
        def wanted_path(image_type):
            # directory = self.get_setting('image_directory')
            pos3 = Path(character_string)/f'{character_string}_{image_type}.png'
            return directory/pos3
        
        def root_path(image_type):
            return self.root_folder/'.images'/ f'{character_string}_{image_type}.png'

        def do_move(image_type):
            # directory = self.get_setting('image_directory')
            wanted = wanted_path(image_type)
            test1 = directory/f'{character_string}_{image_type}.png'
            file,move_file,file_exists,move,remove = None,None,False,False,False
            if os.path.isfile(test1):
                file,file_exists = str(test1),True
                move_file,move,remove = file,True,True
            if os.path.isfile(wanted):
                file,file_exists = str(wanted),True
                move_file = None
            return file_exists,file,move,move_file
        
        msg = False
        def nothing(image_type,msg=msg):
            # if msg: print(character,image_type,'nothing'+f'\nkeep {image_dict[image_type]}\n')
            if msg: print(character,image_type,'nothing (keep images as is)')
        def replace(src,image_type,msg=msg):
            if msg and image_dict == None: print(character,image_type,'add'+f'\nadd {src} to images')
            elif msg and image_type in image_dict: print(character,image_type,'replace'+f'\nreplace {image_dict[image_type]} with {src}\n')
            elif msg and image_type not in image_dict: print(character,image_type,'add'+f'\nadd {src} to images')
            src = str(src) if src!=None else None
            kwargs={image_type:src}
            character.update_images(kwargs)
        def copy(src,image_type,update=False,msg=msg):
            dest_path = wanted_path(image_type)
            if msg: print(character,image_type,'copy'+f'\ncopy {src} to wanted_path\n')
            dest_dir=dest_path.parent
            dest_name=dest_path.name
            os.makedirs(dest_dir,exist_ok=True)
            self.import_file(src_path=src,dest_dir=dest_dir,new_name=dest_name)
            if update: replace(dest_path,image_type,msg=False)
        def remove(src,msg=msg):
            if msg: print(character,image_type,'remove'+f'\nremove {src}\n')
            self.remove_file(src)
        def copy_and_remove(src,image_type,msg=msg):
            if msg: print(character,image_type,'copy_and_remove'+f'\ncopy {src} to wanted_path and remove source\n')
            if os.path.isfile(src): 
                remove(wanted_path(image_type),msg=False)
                copy(src,image_type,update=True,msg=False) 
                remove(src,msg=False)
            
        # Only image types that are already in image_files  
        possible_image_types = character.image_files.keys()
        image_dict = character['images']
        if isinstance(image_dict,dict): image_dict = {k:str(v) for k,v in image_dict.items() if v!=None and os.path.isfile(v)}
        if image_dict=={} or  image_dict==None: image_dict, path_correct = None, False
        
        
        for image_type in possible_image_types:
            file_exists,file,move,move_file = do_move(image_type)
            if isinstance(image_dict,dict): path_correct = image_type in image_dict
            
            # add or replace with (default) image when current path is non existing or is not a file
            if file_exists and not path_correct and not move: replace(file,image_type)
            # move image from other directory if current path is non existing or is not a file
            elif file_exists and not path_correct and move: copy_and_remove(move_file,image_type)
            # keep everything as is 
            elif file_exists and not path_correct: nothing(image_type)
            # move image from other directory if it is the same as current path 
            elif file_exists and path_correct and move and image_dict[image_type]==move_file: copy_and_remove(move_file,image_type)
            # remove image from other directory if current path points to different image
            elif file_exists and path_correct and move and image_dict[image_type]!=move_file: remove(move_file)
            # move path image if current path points to different image than (default) image
            elif file_exists and path_correct and not move and image_dict[image_type]!=file: copy_and_remove(image_dict[image_type],image_type)
            # keep everything as is if path points to (default) image
            elif file_exists and path_correct and not move and image_dict[image_type]==file: nothing(image_type)
            # keep everything as is 
            elif file_exists and path_correct: nothing(image_type)
            # move path image if (default) image does not exist 
            elif not file_exists and path_correct: copy_and_remove(image_dict[image_type],image_type)
            # copy root image if (default) image and path image do not exist
            elif not file_exists and os.path.isfile(root_path(image_type)): copy(root_path(image_type),image_type)
            # if no other image can be found, image type will be erased from images
            elif not file_exists: replace(None,image_type)

            # elif file_exists and path_correct:
            #     # i mostly don't want to overwrite path 
            #     if move and image_dict[image_type]==move_file:
            #         # image moved when image in image directory
            #         # priority has image outside of character folder
            #         copy(move_file,update_character=True) 
            #         self.remove_file(move_file)
            #     elif move and image_dict[image_type]!=move_file:
            #         # image in image directory that is not used
            #         self.remove_file(move_file)
            #     elif not move and image_dict[image_type]!=file:
            #         # don't overwrite !!! (keep path as it is)
            #         # situation: path points to image not in image directory or with different name
            #         self.remove_file(file)
            #         copy(image_dict[image_type],update_character=True) 
            #         self.remove_file(image_dict[image_type])
            #     elif not move and image_dict[image_type]==file:
            #         # not necessary to overwrite
            #         pass
                    
            # elif not file_exists:
            #     # file does not exist in image directory
            #     if path_correct:
            #         # copy from former reference to image directory 
            #         # also works for renaming images 
            #         # ! Terrible if old image has reference too (because wont work anymore after deleting) 
            #         src_path = image_dict[image_type]
            #         overwrite = True
            #         delete = True
            #     elif os.path.isfile(root_path(image_type)): 
            #         # copy from former directory to image directory
            #         src_path = root_path(image_type)
            #         overwrite = True
            #         delete = False
            #     else:
            #         # Here I could remove obsolete image types
            #         # ! Should I do this ?
            #         character.update_images({image_type:None})
            #         src_path=""
                    
            #     if os.path.isfile(src_path) and overwrite: 
            #         copy(src_path,update_character=True)
            #         if delete: self.remove_file(src_path)
                    
        images={k:v for k,v in  character.image_files.items() if v!=None}
        images=images if images!={} else None
        character.update({'images':images})
                    
    # = ============================================================== = #
    # =                             FILTER                             = #
    # = ============================================================== = #
    
    def toggle_search_bar(self,toggle=True,turn_off=True):
        if toggle:
            if not hasattr(self.search_entry,'hidden') or not self.search_entry.hidden:
                self.hide_widget(self.search_filter,do_hide=True,x=True,y=True)
                self.search_entry.hidden = True
            else:
                self.hide_widget(self.search_filter,do_hide=False,x=True,y=True)
                self.search_entry.hidden = False            
        else: 
            if turn_off:
                self.hide_widget(self.search_filter,do_hide=True,x=True,y=True)
                self.search_entry.hidden = True
            else:
                self.hide_widget(self.search_filter,do_hide=False,x=True,y=True)
                self.search_entry.hidden = False
                
    def toggle_filter(self,box,fil,toggle=True,turn_off=True):
        # print(box,fil.children)

        
        def hide_toggle(box,fil,do_hide=True):
            change_stuff = hasattr(box, 'saved_attrs') and not do_hide
            self.hide_widget(widget=box,do_hide=do_hide,x=False,y=True)
            self.hide_widget(widget=fil,do_hide=do_hide,x=False,y=True)
            if change_stuff:
                fil.height = fil.minimum_height
            
        if toggle:
            # hide widget when it is not hidden (never has been hidden)
            if not hasattr(box,'hidden') or not box.hidden: 
                hide_toggle(box,fil,do_hide=True)
                for child in fil.children: child.disabled=True
            # unhide widget when is hidden 
            else: 
                hide_toggle(box,fil,do_hide=False)
                for child in fil.children: child.disabled=False
        else: 
            # hide widget when it is turned off              
            if turn_off: 
                hide_toggle(box,fil,do_hide=True)
                for child in fil.children: child.disabled=True
            # unhide widget when it is turned on              
            else: 
                hide_toggle(box,fil,do_hide=False)
                for child in fil.children: child.disabled=False
class Filter(Toggle):
    filter_icons = DictProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def on_filter_icons(self,instance,value):
        self.list_buttons()
        
    def list_buttons(self):
        for name,icon in self.filter_icons.items():
            if icon not in ["",None]:
                button = IconTextToggleButton()
            elif name not in ["",None]:
                button = TextToggleButton()
            else:
                button = IconToggleButton()
            button.disabled = True
            button.text = name
            button.icon = icon
            button.kind = 'filter'
            self.add_widget(button)
            self.ids[name] = button
        
class Sorter(Toggle):
    sorter_icons = DictProperty()
    switch_map = DictProperty()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def on_sorter_icons(self,instance,value):
        self.list_buttons()
    
    def list_buttons(self):
        for name,icon in self.sorter_icons.items():
            
            if name == 'switch' and isinstance(icon,dict):
                button = IconToggleButton()
                button.switch_map = icon
                icon = [v for v in icon.values()][0]
                button.kind = 'switch'
            elif icon not in ["",None]:
                button = IconTextToggleButton()
                button.kind = 'select_one'
            else:
                button = TextToggleButton()
                button.kind = 'select_one'
                
            from kivy.clock import Clock            
            button.text = name
            button.icon = icon
            self.add_widget(button)
            self.ids[name] = button
            
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.abc())
        
    def abc(self):
        height = max([child.height for name,child in self.ids.items() if name!='switch'])
        if 'switch' in self.ids: self.ids['switch'].height = height