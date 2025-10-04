from kivy.utils import platform
from packages.pleco import dictionary

from templates import MyScreen, RectangularIconButtton, CustomListItem
from kivy.properties import ObjectProperty, StringProperty, ListProperty, NumericProperty, BooleanProperty
from kivymd.uix.button import MDIconButton
from kivymd.uix.anchorlayout import MDAnchorLayout

class ViewDict(MyScreen):
    dict_file=StringProperty()
    dict_name=StringProperty('Dictionary Name')
    dictionary=ObjectProperty()
    
    def __init__(self, default=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default=default
        if platform=="linux" and self.default:
            dict_dir="/media/selina/SHARE/MyProjects/Pleco/"
            self.dict_file=dict_dir+"plecoformat.txt"
            self.dict_name="Test"
            self.read_dict_file()
                
    def read_dict_file(self):
        self.empty_dict()
        can_read = self.dictionary.read(self.dict_file,add=False)
        if can_read:
            self.set_list_items(namelist=self.dictionary.get_simple_list())
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
            'callback':lambda x:x}
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
        # for name in self.namelist:
        for character in self.dictionary:
            dataitem=self.create_dataitem(character)
            self.add_list_item(dataitem,text=text,search=search)


class DictionaryEntry(CustomListItem):
    text = StringProperty()
    char_simp = StringProperty()
    char_trad = StringProperty()
    char_pron = StringProperty()
    character = ObjectProperty()
    is_radical = BooleanProperty()
    is_measure_word = BooleanProperty()
    is_grammatical = BooleanProperty()
    has_translation = BooleanProperty()
    translation = StringProperty()
    
    def get_categories(self):
        print(self.character.info(complete=False))
        
class EntryType(MDIconButton):
    the_size=NumericProperty()
    
    def choose_icon(self, is_type,icons=['alpha-a-box-outline','alpha-a-box']):
        return icons[int(is_type)]
    
    def get_size(self,is_type,sizes=[0,40]):
        return sizes[int(is_type)]
        # return sizes[1]
    
class EntryInfo(MDAnchorLayout):
    the_size=NumericProperty()
    