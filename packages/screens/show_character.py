import os
from functools import partial
from packages.chd import Dictionary, Character
from kivy.properties import (
    ObjectProperty, 
    ListProperty, 
    BooleanProperty,
    DictProperty,
    )
from packages.kivy import (
    MyScreen,
    ImageDisplay,
    CategoryItem
)

from kivy.metrics import Metrics, dp

def create_char_string(character:Character):
    char_string = f'C_{character.entry.simple}_{character.entry.traditional}_{character.entry.pronunciation}'
    return char_string

class ShowCharacter(MyScreen):
    parent_dictionary:Dictionary=ObjectProperty(Dictionary())
    character:Character=ObjectProperty()
    dict_screen=ObjectProperty(None)
    config=DictProperty()
    categories=ListProperty()
    head_categories=['simple','traditional','pronunciation']
    # default_height=dp(81/float(Metrics.density)) #based on font size
    default_height=0
    editable=BooleanProperty(True)
    links=ListProperty()
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # self.name = create_char_string(self.character)
        # self.build_scroll()
        
    def set_background(self, config, dict_screen, parent_dictionary):
        self.dict_screen = dict_screen
        self.config = config
        self.parent_dictionary = parent_dictionary if parent_dictionary!=None else self.parent_dictionary
        
    # = ============================================================== = #
    # =                           CATEGORIES                           = #
    # = ============================================================== = #
        
    @property
    def not_listed_categories(self) -> list:
        # categories that are removed from the list because they are not wanted
        return {k:v for k,v in self.get_setting('categories').items() if k not in self.config['categories'] and k not in self.head_categories}
        
    @property
    def possible_categories(self) -> dict:
        # all_categories = self.get_setting('categories')
        # if 'categories' in self.config: 
        #     return {cat: all_categories[cat] for cat in self.config['categories']}
        return self.get_setting('categories')
    
    @property
    def unused_categories(self) -> list:
        # categories in specified default categories 
        categories = self.possible_categories
        # without values
        missing_categories = self.character.missing
        # not yet existent
        new_categories = [cat for cat in categories if cat not in self.character.entry.to_dict()]
        # categories with values but not shown (part of not_listed_categories)
        hidden_categories=[cat for cat in self.character.filled if cat in self.not_listed_categories]
        # print(missing_categories,new_categories,hidden_categories)
        return [cat for cat in missing_categories+new_categories+hidden_categories if cat not in self.categories]
    
    def get_category(self,cat):
        if self.character != None:
            if cat == 'pinyin':
                return self.character.pinyin
            elif cat in self.character.filled:
                return self.character[cat]
        else: return ""
            
    # = ============================================================== = #
    # =                             SCREEN                             = #
    # = ============================================================== = #
    
    # = ––––––––––––––––––––––––––– update ––––––––––––––––––––––––––– = #
    
    def update_character(self, entries={}):
        # updates head categories only
        
        if  entries != {}: 
            self.dict_screen.edited = True
            self.links = []
            self.character.update(entries)
        
        for category in self.head_categories:
            if category in self.ids:
                if category == 'pronunciation': text=self.character.pinyin
                else: text=self.character[category]
                self.ids[category].label.text = text
                self.ids[category].size_hint_x=1 if text!="" else None
        
        # self.dict_screen.get_character_image(character=self.character)
            
    def update_image_display(self,image_type,path):
        self.dict_screen.edited = True
        if os.path.isfile(path):
            kwargs={image_type:str(path)}
            self.character.update_images(kwargs)
        image_files=self.character.image_files
        if 'images' in self.categories:
            self.update_category(category='images',entry=image_files)
        if 'image_display' in self.ids.scroll.ids.keys():
            self.ids.scroll.ids['image_display'].display_image(image_type=image_type,file=str(path))
        else:
            # self.clean_scroll()
            self.build_scroll()
            
    def update_category(self,category,entry,original=None):
        # update categories from scroll list
        self.dict_screen.edited = True
        if entry != None:
            if category == 'grammar' and isinstance(entry,list): entry = [e.replace('_','＿') for e in entry]
            self.character.update({category:entry},get_dtype_warning=False)
            if category not in self.categories:
                self.list_category_content(category,entry)
            
            self.ids.scroll.ids[category].remove_content()
            self.ids.scroll.ids[category].list_category(values=entry)
        else:
            self.character.remove(category)
            self.remove_translations(category)
    
    # = –––––––––––––––––––––––– category list ––––––––––––––––––––––– = #
    
    def set_character(self,character):
        self.character = character
        self.name = create_char_string(self.character)
        self.update_character()
        
    
    def build_scroll(self,character=None):
        self.clean_scroll()
        if character!=None: self.set_character(character)
                    
        image_files = self.character.image_files
        self.list_images(image_files=image_files)
        def is_info_category(cat):
            listed = cat not in self.not_listed_categories
            not_header = cat not in self.head_categories
            return (not_header and listed)
        categories = [cat for cat in self.character.filled if is_info_category(cat)]
        for category in categories:
            values = self.get_category(category)
            self.list_category_content(category,values)
        
    def clean_scroll(self):
        self.ids.scroll.clear_widgets()
        self.categories = []
    
    def list_images(self,image_files):
        
        l=ImageDisplay(image_files=image_files)
        self.ids.scroll.add_widget(l)
        self.ids.scroll.ids['image_display']=l
                
    def list_category_content(self,category,content):
        # if isinstance(content,dict): 
        #     content = {k:v if v!=None else "" for k,v in content.items() }
        #     if content == {}: return None
        small_bullets=['variants','relatives','words','others','grammar']
        long_text=['origin','mnemonics']
        # long_text=[]
        rest=['components','images','links','link','usage']

        if  content != None and category not in self.categories:
            self.categories.append(category)
            if category in small_bullets:
                # list of rows next to head (don't take up all the rest space)
                l=CategoryItem(
                    category=category,values=content,
                    cols=2,small=True,line_width=330,head_width=400)
            elif category in long_text:
                # list of rows below head
                l=CategoryItem(
                    category=category,values=content,
                    cols=1,small=False,head_width=None)
            else:
                # list of rows next to head (take up all the rest space)
                l=CategoryItem(
                    category=category,values=content,
                    cols=2,small=False,head_width=400)
                
            self.ids.scroll.add_widget(l)
            self.scroll.ids[category]=l
        
    def remove_translations(self,cat):
        if cat in self.ids.scroll.ids:
            self.categories.remove(cat)
            self.ids.scroll.remove_widget(self.ids.scroll.ids[cat])
    
    # = ––––––––––––––––––––––––––– switch ––––––––––––––––––––––––––– = #
            
    def show_next(self):
        if self.dict_screen == None: return None
        if self.character.uniq in self.dict_screen.filtered_characters:
            i = self.dict_screen.filtered_characters.index(self.character.uniq)
            if i+1 == len(self.dict_screen.filtered_characters): i=-1
            next_character = self.dict_screen.filtered_characters[i+1]
            i = self.parent_dictionary.index(next_character)
            self.show_other(i,direction='left')
    
    def show_previous(self):
        if self.dict_screen == None: return None
        if self.character.uniq in self.dict_screen.filtered_characters:
            i = self.dict_screen.filtered_characters.index(self.character.uniq)
            next_character = self.dict_screen.filtered_characters[i-1]
            i = self.parent_dictionary.index(next_character)
            self.show_other(i,direction='right')
        
    def show_other(self,i,direction):
        
        screen = self.my_app.pre_loaded_widgets['character']
        screen.set_background(dict_screen=self.dict_screen, parent_dictionary=self.parent_dictionary, config=self.config)
        screen.build_scroll(character=self.parent_dictionary[i])
        self.add_screen(screen=screen,direction=direction,remember=False)
        
    # = ============================================================== = #
    # =                            CHARACTER                           = #
    # = ============================================================== = #
    
    def export_character(self):
        from main import ChD
        app = ChD.get_running_app()
        repeat,repeat_exact = app.check_character_for_multiple(self.character)
        count_normal,count_exact=len(repeat),len(repeat_exact)
        support_text='This character will be exported in a format fitting of the Pleco Dictionary App (txt).'

        if count_normal == count_exact: 
            text = 'dictionaries have'
            if count_normal-1 == 1: text = 'dictionary has'
            other = ', '.join(list(set(repeat_exact) - set([self.parent_dictionary.name])))
            support_text+=f'\n\n[Note] {count_normal-1} other {text} this exact character'
        elif count_normal>count_exact:
            other = ', '.join(list(set(repeat) - set(repeat_exact)))
            support_text+=f'\n\n[Note] look at other dictionaries for different version of same character'
        if len(other)>0: support_text+=f': {other}'
        else: support_text+='.'
        
        name = str(self.character)
        template = self.get_setting('template_directory')/f'{self.config["template"]}.chd'
        dialog = self.my_app.pre_loaded_widgets['export_char']
        dialog.set_attrs(name=name,template=template,support_text=support_text)
        dialog.open()

    def del_character(self):
        if self.editable:
            name = str(self.character)
            dialog = self.my_app.pre_loaded_widgets['delete_char']
            dialog.set_attrs(name=name)
            dialog.open()
        
    # = ============================================================== = #
    # =                       EDIT CHARACTER INFO                      = #
    # = ============================================================== = #

    def replace_character(self):
        
        def read_replacement_file(path):
            self.file_manager.close()
            d = Dictionary(name='replacement')
            d.read(filename=path,file_format='jsonl',categories=self.possible_categories)
            print(d[self.character], isinstance(d[self.character],Character))
        
        kwargs = {
            'description' : 'Decide which character file should be used to replace current character.',
            'select_path' : read_replacement_file,
            'ext' : ['.jsonl'],
        }
        self.file_manager = self.my_app.pre_loaded_widgets['file_manager']
        self.file_manager.set_attrs(**kwargs)
        self.file_manager.show(path=None,use_root_folder=False)
        
    # = –––––––––––––––––––––––––––– head –––––––––––––––––––––––––––– = #
    
    def edit_character(self):
        if self.editable:
            kwargs={
                "title":'Character',
                "support_text":f"Edit the chinese characters (simplified & traditional language) amd pronunciation in pinyin.",
            }
            entries=[]
            for category in self.head_categories:
                entries += [self.character[category]]

            dialog = self.my_app.pre_loaded_widgets['edit_element']
            dialog.choose_content(style="normal",**kwargs)
            char_entry = '- '+'\n- '.join([e if e!=None else "" for e in entries])
            dialog.set_entry(char_entry)
            dialog.open()
    
    # = –––––––––––––––––––––––––– category –––––––––––––––––––––––––– = #
    
    def edit_category(self,category):
        if self.editable:
            title=category.replace('_',' ').title()
            category=category.lower().replace(' ','_')
            
            kwargs={
                "title":title,
                "support_text":"Information about the character can be edited here.",
            }
            
            entry = self.character[category]
            
            dialog = self.my_app.pre_loaded_widgets['edit_element']
            
            if isinstance(entry,dict): dialog.choose_content(style="dict",**kwargs)
            else: dialog.choose_content(style="normal",**kwargs)
            
            if hasattr(self,'dialog'): self.dialog.dismiss()
            
            dialog.set_entry(entry=entry)
            dialog.open()
        
    def new_category(self):
        categories=[cat.replace('_',' ') for cat in self.unused_categories]
        
        kwargs={
            "title":"Character Information",
            'support_text':"",
            "options":categories,
            "itemclass":"MyListItem",
            "func":self.edit_category
        }
        dialog = self.my_app.pre_loaded_widgets['options']
        dialog.list_options(**kwargs)
        dialog.open()
        
    # = –––––––––––––––––––––––––––– image ––––––––––––––––––––––––––– = #
    
    def add_image(self):
        
        def select_image_path(path,image_type):
            self.file_manager.close()
            image_directory = self.get_setting('image_directory')
            image_type=image_type.lower().replace(' ',"_")
            
            image_name = self.character.unicode_unique_string
            image_directory = image_directory/image_name
            file_name = f'{image_name}_{image_type}.png'
            
            # print(path,image_directory,path.parent==image_directory)
            # self.remove_file(image_directory/file_name)
            
            # if image_type in ['ancient_character','shuowen_jiezi'] and 
            
            do_import = True if image_type in ['ancient_character','shuowen_jiezi'] else False
            if do_import:
                os.makedirs(image_directory, exist_ok=True)
                imported = self.import_file(src_path=path,dest_dir=image_directory,new_name=file_name,inform=False)
                filepath = image_directory/file_name
                self.update_image_display(image_type=image_type,path=filepath)
            elif os.path.isfile(path):
                self.update_image_display(image_type=image_type,path=path)
        
        def find_images(image_type=""):
            from pathlib import Path
            directory = self.get_setting('image_directory')
            matches = []

            if image_type!="": image_type=f'_{image_type.lower().replace(" ","_")}'
            search_pattern = f"*{self.character.unicode_unique_string}{image_type}*"
            matches.extend(directory.rglob(search_pattern))
            if matches==[]: print(search_pattern,directory)
            return matches
        
        def choose_png_file(image_type):
            
            matches = find_images(image_type)
            if matches != []:  path = matches[0].parent
            else: path = None
                        
            kwargs = {
                'description' : f'Decide which png image should be uploaded. \nType of image: {image_type.replace("_"," ").title()}',
                'select_path' : partial(select_image_path,image_type=image_type),
                'preview' : True,
                'ext' : ['.png'],
            }
            self.file_manager = self.my_app.pre_loaded_widgets['file_manager']
            self.file_manager.set_attrs(**kwargs)
            self.file_manager.show(path=path,use_root_folder=True)
            
        def choose_image_type():
            # options=list(set(['ancient_character','shuowen_jiezi']) | set(self.character.image_files.keys()))
            options = list(dict.fromkeys(['ancient_character','shuowen_jiezi'] + list(self.character.image_files.keys())))
            matches = find_images()
            if matches!=[]: matches = [p.stem.replace(f'{self.character.unicode_unique_string}_',"") for p in matches if p.is_file()]
            options = set(options+matches)

            options=[o.replace('_',' ').title() for o in options]
            
            kwargs={
                "title":"Image Type",
                'support_text':"Images in relation to the character can be selected here. There are some predefined options which give a general description of the image content.",    
                "options":options,
                "itemclass":"MyListItem",
                "func":choose_png_file,
            }
            dialog = self.my_app.pre_loaded_widgets['options_add']
            dialog.list_options(**kwargs)
            dialog.open()
        
        if self.editable:
            choose_image_type()
        
    def find_urls(self):
                
        def __check_url(url):
            import requests
            try:
                # We use a timeout so the script doesn't hang indefinitely
                response = requests.head(url, timeout=5, allow_redirects=True)
                
                # Returns True if the status code is less than 400 (e.g., 200 OK)
                return response.status_code < 400
            except requests.RequestException:
                # Catches connection errors, timeouts, or invalid URLs
                return False
    
        def open_url(url):
            import webbrowser
            webbrowser.open(url) 
            
        def list_urls(character):
            if self.links==[]:
                websites = {
                'Zdic':'https://zdic.net/hans/',
                'Zi.tools':'https://zi.tools/zi/',
                'hanzidb':'http://hanzidb.org/character/',
                }
                links = []
                characters = [char for char in character.uniq[:2] if char != ""]
                for char in characters:
                    links += [(k,v+char) for k,v in websites.items() if __check_url(v+char)]
                self.links = links
                
                if self.editable:
                    self.character.update(links=[l[1] for l in links])  
                    # links has to be category
                    self.update_category(category='links',entry=[l[1] for l in links])

            if len(self.links)>0:
                kwargs={
                    "title":"Websites",
                    'support_text':"Some web dictionaries are linked here.",    
                    "options":[l[1] for l in self.links],
                    "itemclass":"MyListItem",
                    "func":open_url,
                }
                dialog = self.my_app.pre_loaded_widgets['options']
                dialog.list_options(**kwargs)
                dialog.open()
            
        list_urls(self.character)