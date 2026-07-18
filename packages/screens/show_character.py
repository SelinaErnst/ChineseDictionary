import os
from functools import partial
from packages.chd import Dictionary, Character
from kivy.properties import NumericProperty, ObjectProperty, ListProperty, StringProperty,BooleanProperty
from packages.kivy import (
    MyScreen,
    EditElement,
    ConfirmDelete,
    ConfirmExport,
    ShowOptions,
    AttentionMsg,
    ErrorMsg,
    MyFileManager,
    MDBoxLayout,
    MDStackLayout,
    MDAnchorLayout,
    MultiLineLabel,
    ButtonBehavior,
    ImageDisplay,
    CategoryItem
)

from kivy.metrics import Metrics, dp

def create_char_string(character:Character):
    char_string = f'C_{character.entry.simple}_{character.entry.traditional}_{character.entry.pronunciation}'
    return char_string


                
class ShowCharacter(MyScreen):
    parent_dictionary=ObjectProperty(Dictionary())
    character=ObjectProperty()
    dict_screen=ObjectProperty(None)
    categories=ListProperty()
    head_categories=['simple','traditional','pronunciation']
    # default_height=dp(81/float(Metrics.density)) #based on font size
    default_height=0
    editable=BooleanProperty(True)
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.name = create_char_string(self.character)
        self.build_scroll()
        
    # = ============================================================== = #
    # =                           CATEGORIES                           = #
    # = ============================================================== = #
        
    @property
    def not_listed_categories(self) -> list:
        return self.get_setting('hidden_categories') 
    
    @property
    def possible_categories(self) -> dict:
        return self.get_setting('categories')
    
    @property
    def unused_categories(self) -> list:
        # categories in specified default categories (not yet existent or without values)
        categories = self.possible_categories
        # without values
        missing_categories = self.character.missing
        # not yet existent
        new_categories = [cat for cat in categories if cat not in self.character.entry.to_dict()]
        # categories with values but not shown (part of not_listed_categories)
        hidden_categories=[cat for cat in self.character.filled if cat in self.not_listed_categories]

        return [cat for cat in missing_categories+new_categories+hidden_categories if cat not in self.categories]
    
    def get_category(self,cat):
        if self.character != None:
            if cat in self.character.filled:
                return self.character[cat]
            
    # = ============================================================== = #
    # =                             SCREEN                             = #
    # = ============================================================== = #
    
    # = ––––––––––––––––––––––––––– update ––––––––––––––––––––––––––– = #
    
    def update_character(self, entries={}):
        # updates head categories only
        self.dict_screen.edited = True
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
            kwargs={image_type:path}
            self.character.update_images(kwargs)
        if 'images' in self.categories:
            self.update_category(category='images',entry=self.character.image_files)
        if 'image_display' in self.ids.scroll.ids.keys():
            self.ids.scroll.ids['image_display'].display_image(image_type=image_type,file=path)
        else:
            self.clean_scroll()
            self.build_scroll()
            
    def update_category(self,category,entry,original=None):
        # update categories from scroll list
        self.dict_screen.edited = True
        if entry != None:
            # new_entry = new_entry.replace('/n',' ')
            self.character.update({category:entry},get_dtype_warning=False)
            if category not in self.categories:
                self.list_category_content(category,entry)
            
            # entry=entry if isinstance(entry,list) else [entry]
            self.ids.scroll.ids[category].remove_content()
            self.ids.scroll.ids[category].list_category(values=entry)
        else:
            self.character.remove(category)
            self.remove_translations(category)
    
    # = –––––––––––––––––––––––– category list ––––––––––––––––––––––– = #
    
    def build_scroll(self):
        self.list_images(image_files=self.character.image_files)
        def is_info_category(cat):
            listed = cat not in self.not_listed_categories
            not_header = cat not in self.head_categories
            return (not_header and listed)
        categories = [cat for cat in self.character.filled if is_info_category(cat)]
        for category in categories:
            values = self.get_category(category)
            self.list_category_content(category,values)
        
    def clean_scroll(self):
        for c in [c for c in self.ids.scroll.children]:
            c.clear_widgets()
    
    def list_images(self,image_files):
        
        l=ImageDisplay(image_files=image_files)
        self.ids.scroll.add_widget(l)
        self.ids.scroll.ids['image_display']=l
                
    def list_category_content(self,category,content):
        small_bullets=['variants','relatives','words','others','dict_entries']
        long_text=['origin','components','english','german','mnemonics','usage','images','link']
    #     translations=self.get_category(cat) if translations==None else translations
        if  content != None and category not in self.categories:
            self.categories.append(category)
            if category in small_bullets:
                l=CategoryItem(
                    category=category,values=content,
                    cols=2,small=True,line_width=330,head_width=325)
            elif category in long_text:
                l=CategoryItem(
                    category=category,values=content,
                    cols=1,small=False,head_width=None)
            else:
                l=CategoryItem(
                    category=category,values=content,
                    cols=2,small=False,head_width=325)
                
            self.ids.scroll.add_widget(l)
            self.scroll.ids[category]=l
        
    def remove_translations(self,cat):
        if cat in self.ids.scroll.ids:
            self.categories.remove(cat)
            self.ids.scroll.remove_widget(self.ids.scroll.ids[cat])
    
    # = ––––––––––––––––––––––––––– switch ––––––––––––––––––––––––––– = #
            
    def show_next(self):
        if self.character in self.parent_dictionary:
            i = self.parent_dictionary.index(self.character)+1
            if i == len(self.parent_dictionary): i=0
            self.__show_other(i,direction='left')
    
    def show_previous(self):
        if self.character in self.parent_dictionary:
            i = self.parent_dictionary.index(self.character)-1
            self.__show_other(i,direction='right')
        
    def __show_other(self,i,direction):
        self.bottom_nav.set_state('toggle')
        screen = ShowCharacter(character=self.parent_dictionary[i], dict_screen=self.dict_screen, parent_dictionary=self.parent_dictionary)
        self.add_screen(screen=screen,direction=direction,remember=False)
        screen.bottom_nav.set_state('toggle')
        
        
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
        dialog = ConfirmExport(name=name,support_text=support_text,what='export_character')
        dialog.open()

    def del_character(self):
        if self.editable:
            name = str(self.character)
            dialog = ConfirmDelete(name=name,what='delete_character')
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
        
        self.file_manager = MyFileManager(
            description='Decide which character file should be used to replace current character.',
            select_path=read_replacement_file,
            ext=[".jsonl"])
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
            dialog = EditElement(**kwargs)
            dialog.content.ids.input.text='- '+'\n- '.join([e if e!=None else "" for e in entries])
            dialog.open()
    
    # = –––––––––––––––––––––––––– category –––––––––––––––––––––––––– = #
    
    def edit_category(self,category):
        if self.editable:
            title=category.replace('_',' ').title()
            category=category.lower().replace(' ','_')
            
            support_text="Information about the character can be edited here."
            kwargs={
                "title":title,
                "support_text":support_text,
            }
            entry = self.character[category]
            if isinstance(entry,dict): dialog = EditElement(style="dict",**kwargs)
            else: dialog = EditElement(style="normal",**kwargs)
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
            "func":self.edit_category,
        }
        dialog = ShowOptions(**kwargs)
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
            
            self.remove_file(image_directory/file_name)
            
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
            return matches
        
        def choose_png_file(image_type):
            self.file_manager = MyFileManager(
                description=f'Decide which png image should be uploaded. \nType of image: {image_type.replace("_"," ").title()}',
                select_path=partial(select_image_path,image_type=image_type),
                preview=True,
                ext=[".png"])

            matches = find_images(image_type)
            if matches != []:  path = matches[0].parent
            else: path = None
            self.file_manager.show(path=path,use_root_folder=True)
            
        def choose_image_type():
            # options=list(set(['ancient_character','shuowen_jiezi']) | set(self.character.image_files.keys()))
            options = list(dict.fromkeys(['ancient_character','shuowen_jiezi'] + list(self.character.image_files.keys())))
            matches = find_images()
            if matches!=[]: match_options = [p.stem.replace(f'{self.character.unicode_unique_string}_',"") for p in matches if p.is_file()]
            options = set(options+match_options)

            options=[o.replace('_',' ').title() for o in options]
            kwargs={
                "title":"Image Type",
                'support_text':"Images in relation to the character can be selected here. There are some predefined options which give a general description of the image content.",    
                "options":options,
                "itemclass":"MyListItem",
                "func":choose_png_file,
            }
            dialog = ShowOptions(allow_add=True,**kwargs) 
            dialog.open()
        
        if self.editable:
            choose_image_type()