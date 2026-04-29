import os
from functools import partial
from packages.chd import Dictionary, Character
from kivy.properties import ObjectProperty, ListProperty, StringProperty
from packages.kivy import (
    MyScreen,
    AddElement,
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
    ImageDisplay
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
    default_height=dp(81/float(Metrics.density)) #based on font size
    
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
                
        if self.dict_screen != None:
            self.dict_screen.set_list_items()
            
    def update_image_display(self,image_type,path):
        self.dict_screen.edited = True
        kwargs={image_type:path}
        self.character.update_images(kwargs)
        if 'image_display' in self.ids.scroll.ids.keys():
            self.ids.scroll.ids['image_display'].display_image(image_type=image_type,file=path)
        else:
            self.clean_scroll()
            self.build_scroll()
            
    def update_category(self,category,entry):
        # update categories from scroll list
        self.dict_screen.edited = True
        if entry != None:
            self.character.update({category:entry},get_dtype_warning=False)
            if category not in self.categories:
                self.list_translations(category)
            
            entry=entry if isinstance(entry,list) else [entry]
            self.ids.scroll.ids[category].bullets.remove_bullets()
            self.ids.scroll.ids[category].bullets.create_bullets(results=entry)
        else:
            self.character.remove(category)
            self.remove_translations(category)
    
    # = –––––––––––––––––––––––– category list ––––––––––––––––––––––– = #
    
    def build_scroll(self):
        self.list_images(image_files=self.character.image_files)
        for category in self.character.filled:
            if category not in self.not_listed_categories \
                and category not in self.head_categories:
                    self.list_translations(category)
        
    def clean_scroll(self):
        for c in [c for c in self.ids.scroll.children]:
            c.clear_widgets()
    
    def list_images(self,image_files):
        l=ImageDisplay(image_files=image_files)
        self.ids.scroll.add_widget(l)
        self.ids.scroll.ids['image_display']=l
                
    def list_translations(self,cat,translations=None):
        translations=self.get_category(cat) if translations==None else translations
        if  translations != None and cat not in self.categories:
            self.categories.append(cat)
            translations=translations if isinstance(translations,list) else [translations]
            l=MyList(category=cat,translations=translations)
            self.ids.scroll.add_widget(l)
            self.ids.scroll.ids[cat]=l
        else:
            pass
        
    def remove_translations(self,cat):
        if cat in self.ids.scroll.ids:
            self.categories.remove(cat)
            self.ids.scroll.remove_widget(self.ids.scroll.ids[cat])
    
    # = ––––––––––––––––––––––––––– switch ––––––––––––––––––––––––––– = #
            
    def show_next(self):
        i = self.parent_dictionary.index(self.character)+1
        if i == len(self.parent_dictionary): i=0
        self.__show_other(i,direction='left')
    
    def show_previous(self):
        i = self.parent_dictionary.index(self.character)-1
        self.__show_other(i,direction='right')
        
    def __show_other(self,i,direction):
        self.bottom_nav.set_state('toggle')
        screen = ShowCharacter(character=self.parent_dictionary[i], dict_screen=self.dict_screen, parent_dictionary=self.parent_dictionary)
        self.add_screen(screen=screen,direction=direction)
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
        dialog = ConfirmExport(name=name,support_text=support_text,what='character')
        dialog.open()

    def del_character(self):
        name = str(self.character)
        dialog = ConfirmDelete(name=name,what='character')
        dialog.open()
    
    # = ============================================================== = #
    # =                       EDIT CHARACTER INFO                      = #
    # = ============================================================== = #

    def replace_character(self):
        
        def read_replacement_file(path):
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
        kwargs={
            "title":'Character',
            "support_text":f"Edit the chinese characters (simplified & traditional language) amd pronunciation in pinyin.",
        }
        entries=[]
        for category in self.head_categories:
            entries += [self.character[category]]
        dialog = AddElement(**kwargs)
        dialog.content.ids.input.text='- '+'\n- '.join([e if e!=None else "" for e in entries])
        dialog.open()
    
    # = –––––––––––––––––––––––––– category –––––––––––––––––––––––––– = #
    
    def edit_category(self,category):
        title=category.replace('_',' ').title()
        category=category.lower().replace(' ','_')
        
        support_text="Information about the character can be edited here."
        kwargs={
            "title":title,
            "support_text":support_text,
        }
        entry = self.character[category]
        if hasattr(self,'dialog'): self.dialog.dismiss()
        dialog = AddElement(**kwargs)
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
        
        def import_file(src_path, dest_dir, new_name):
            dest_path = os.path.join(str(dest_dir), new_name)
            try:
                import shutil
                shutil.copyfile(src_path, dest_path)
                # AttentionMsg(attention='File was imported',msg=f'Copied from {src_path} to {dest_path}').open()
                return True
            except Exception as err:
                ErrorMsg(error='File was not imported',msg=str(err)).open()
                return False
        
        def select_image_path(path,image_type):
            self.file_manager.close()
            image_directory = self.get_setting('image_directory')
            image_type=image_type.replace(' ',"_")
            do_import = False if 'other' in image_type else True
            use_og_file_name = True if 'other' in image_type else False
            file_name = os.path.basename(path)
            if use_og_file_name and do_import: file_name = f'{self.character.entry.pronunciation}_{file_name}'
            elif do_import: file_name = f'{self.character.unicode_unique_string}_{image_type}.png'
            if do_import:
                os.makedirs(image_directory, exist_ok=True)
                imported = import_file(src_path=path,dest_dir=image_directory,new_name=file_name)
                filepath = os.path.join(str(image_directory), file_name)
                if imported: self.update_image_display(image_type=image_type,path=filepath)
            elif os.path.isfile(path): 
                self.update_image_display(image_type=image_type,path=path)
            
        def choose_png_file(image_type):
            self.file_manager = MyFileManager(
                description='Decide which png image should be uploaded.',
                select_path=partial(select_image_path,image_type=image_type),
                preview=True,
                ext=[".png"])
            self.file_manager.show(path=None,use_root_folder=True)
            
        def choose_image_type():
            kwargs={
                "title":"Image Type",
                'support_text':"The categories shown here will contain information about the character. By selecting one of them, a new entry can be given.",
                "options":['ancient character','shuowen jiezi','other image'],
                "itemclass":"MyListItem",
                "func":choose_png_file,
            }
            dialog = ShowOptions(**kwargs) 
            dialog.open()
        
        choose_image_type()
        
class ListElement(MultiLineLabel):
    pass
class Head(ButtonBehavior, MultiLineLabel):
    pass

class Bullets(MDStackLayout):

    def create_bullets(self,results,font_name='CH',use_both_directions=False):
        if use_both_directions: 
            size_hint = [None,None]
        else:
            size_hint = [1,None]
        for r in results:
            label=ListElement(text=str(r), font_name=font_name, size_hint=size_hint)
            self.add_widget(label)
    
    def remove_bullets(self):
        self.clear_widgets()

class MyList(MDBoxLayout):
    category=StringProperty()
    translations=ListProperty()
    bullets=ObjectProperty()
    # small_bullets=ListProperty()
    small_bullets=['variants','relatives','words','others']
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        head_text=self.category.replace('_',' ').capitalize()
        head_label=Head(text=head_text)
        head = MDAnchorLayout(anchor_y='top', anchor_x="left", size_hint_x=None, width=330)
        head.add_widget(head_label)
        self.add_widget(head)
        
        self.bullets=Bullets()
        use_both_directions = True if self.category.lower() in self.small_bullets else False
        self.bullets.create_bullets(results=self.translations,use_both_directions=use_both_directions)
        self.add_widget(self.bullets)