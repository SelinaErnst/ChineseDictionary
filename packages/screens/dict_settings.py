import os
from packages.kivy import (
    StringProperty,
    DictProperty,
    ObjectProperty,
    MDStackLayout,
    MDBoxLayout
)

class DictSettings(MDBoxLayout):
    dict_name=StringProperty()
    dict_file=StringProperty()
    config=DictProperty()
    
    def set_attrs(_self, **kwargs):
        for k,v in kwargs.items():
            if v!=None: setattr(_self, k, v)
    
    def get_categories(self,config):
        if 'categories' in self.config: return self.config['categories']
        else: return []
    
    def get_config(self,category,config):
        if category in self.config: return self.config[category]
        else: return ""
    
    # def get_preview_image(self):
    #     if 'preview_image' in self.config: return self.config['preview_image']

    def save(self):
        from main import ChD
        app = ChD.get_running_app()
        
        self.dict_name = self.ids['dict_name'].input.text
        screen = app.wm.current_screen
        screen.rename_dict(self.dict_name)
        self.config.update({'name':self.dict_name})
        
        preview_image = self.ids['image_type'].input.text
        self.config.update({'preview_image':preview_image.lower().replace(' ','_')})
        
        template = self.ids['dict_template'].content.text
        template_file = app.get_setting('template_directory')/f'{template}.chd'
        if os.path.isfile(template_file):
            self.config.update({'template':template})
        
        categories = self.ids['dict_cat'].content.scroll.include
        self.config.update({'categories':categories})
        
        screen.config = self.config
        screen.edited = True
        screen.set_list_items()
        app.move_tmp_files() # templates
        app.dismiss_all()

class EditDictSettings(MDStackLayout):
    dropdown = ObjectProperty()
    content = ObjectProperty()
    input = ObjectProperty()
    options = ObjectProperty()
    
    @property
    def my_app(self):
        from main import ChD
        app:ChD=ChD.get_running_app()
        return app
    
    def use_dropdown(self):
        # EditCategories, EditTemplates
        self.dropdown.close_options()
        
    def close_dropdown(self):
        self.dropdown.is_open = False
    
    def open_dropdown(self):
        self.dropdown.is_open = True
    
    
class EditTemplates(EditDictSettings):
    
    def use_dropdown(self):
        self.dropdown.update_data(self.get_all_templates())
        return super().use_dropdown()
    
    def get_all_templates(self):
        from main import ChD
        app:ChD = ChD.get_running_app()
        templates = app.get_setting('templates')
        tmp_directory = app.get_setting('tmp_directory')
        tmp_templates = [t for t in os.listdir(tmp_directory) if str(t).endswith('.chd')]
        tmp_templates = [t for t in tmp_templates if tmp_directory/t not in app.tmp_files_rm.values()]
        templates = set(templates+tmp_templates)
        return [t.strip('.chd') for t in templates]
    
    def reload(self):
        try: 
            self.dropdown.update_data(self.get_all_templates())
            self.dropdown.clear_selection()
            self.input.clear()
        except:
            pass
        
    def edit(self):
        file = self.my_app.get_setting('template_directory')/(self.input.text+'.chd')
        self.my_app.open_file(file,allow_new=False,create_tmp=True)
        
    def new(self):
        file = self.my_app.get_setting('template_directory')/(self.input.text+'.chd')
        if self.input.text.replace(" ","")!="":
            self.my_app.open_file(file,allow_new=True,create_tmp=True)
        self.close_dropdown()
        
    def delete(self):
        file = self.my_app.get_setting('template_directory')/(self.input.text+'.chd')
        self.my_app.remove_file(file,create_tmp=True)
        self.dropdown.update_data(self.get_all_templates())

class EditName(EditDictSettings):
    pass

class EditImageType(EditDictSettings):
    pass

class SelectCategories(EditDictSettings):
    
    @property
    def all_categories(self):
        return list(self.my_app.get_categories())
    
    def select_all(self):
        self.content.set_list_items(self.all_categories,'all')
    
    def select_none(self):
        self.content.set_list_items(self.all_categories,None)
        
    def select_old(self):
        self.content.set_list_items(self.all_categories,self.options)
        
class EditCategories(EditDictSettings):
    
    def __init__(self, *args, **kwargs):
        self.new_options = {}
        self.rename_map = {}
        
        from main import DTYPE_MAP
        self.dtypes = DTYPE_MAP
        super().__init__(*args, **kwargs)
    
    def category_info(self,category):
        # name, dtype, idx
        infos = [v.strip(' ') for v in category.split(':')]
        return [i.lower().replace(' ','_') for i in infos if i!=""]

    def drop_down(self,categories):
        # return [f'{k} : {v} : {n}' for n,(k,v) in enumerate(self.options.items())]
        return [f'{k} : {v} : {n}' for n,(k,v) in enumerate(categories.items())]
    
    def option_list(self):
        if self.new_options=={}: return [(k,v,n) for n,(k,v) in enumerate(self.options.items())]
        else: return [(k,v,n) for n,(k,v) in enumerate(self.new_options.items())]
        
    def incorrect(self,category):
        
        def is_valid_int(text):
            try:
                int(text)
                return True
            except ValueError:
                return False
        
        info = self.category_info(category)
        if len(info)!=3: return True
        name,dtype,idx=info
        if dtype not in self.dtypes: return True
        if not is_valid_int(idx): return True
        return False
    
    def is_correct(self):
        print('EditCategories')
    
    def add(self):
        category = self.input.text
        
        try_name = self.category_info(category)
        if len(try_name)==1 and try_name[0] in self.options: category = f'{try_name[0]} : {self.options[try_name[0]]} : 0'
        elif self.incorrect(category=category): return None
            
        name,dtype,idx = self.category_info(category)
        idx = int(idx)
        
        if self.new_options!={} and name in self.new_options: return None
        elif self.new_options=={} and name in self.options: return None
        
        unordered_options = self.option_list()
        unordered_options.append((name,dtype,idx))
        ordered_dict = self.sort(unordered_options)
        self.dropdown.update_data(self.drop_down(ordered_dict))
        self.new_options = ordered_dict
        
    def remove(self):
        category = self.input.text
        
        try_name = self.category_info(category)
        if len(try_name)==1 and (try_name[0] in self.options or try_name[0] in self.new_options): name = try_name[0]
        elif self.incorrect(category=category): return None

        name,dtype,idx = self.category_info(category)
        
        if self.new_options!={} and name not in self.new_options: return None
        elif self.new_options=={} and name not in self.options: return None
        
        unordered_options = [option for option in self.option_list() if option[0] != name]
        ordered_dict = self.sort(unordered_options)
        self.dropdown.update_data(self.drop_down(ordered_dict))
        self.new_options = ordered_dict
        
        if name in self.rename_map.values(): self.rename_map = {k:v for k,v in self.rename_map.items() if v!=name}
         
    def rename(self):
        old_name = self.dropdown.selection
        new_name = self.input.text
        if old_name=="" or self.incorrect(category=old_name): return None
        if new_name=="" or self.incorrect(category=new_name): return None
        
        old_name,old_dtype,old_idx = self.category_info(old_name)
        new_name,new_dtype,new_idx = self.category_info(new_name)
        new_idx = int(new_idx)
        ordered_options=self.option_list()
        
        # if new_name != old_name and new_name in self.options: 
        if new_name != old_name and new_name in [o[0] for o in ordered_options]: 
            old_name,old_dtype,old_idx = [(k,v,n) for k,v,n in ordered_options if new_name==k][0]
        

        if old_name != new_name:
            if self.rename_map == {}: self.rename_map[old_name] = new_name
            # elif new_name in self.options:
            elif old_name in self.options: self.rename_map[old_name] = new_name
            elif old_name in self.rename_map.values(): 
                for really_old_name, old in list(self.rename_map.items()):
                    if old == old_name and really_old_name!=new_name: 
                        if new_name not in self.options:
                            self.rename_map[really_old_name] = new_name
                        else:
                            new_name = self.rename_map[really_old_name]
                    else: self.rename_map.pop(really_old_name)

        unordered_options=[]
        for option in ordered_options:
            # self.category_info(option)
            if option[0]!=old_name: unordered_options.append(option)
            else: 
                unordered_options.append((new_name,old_dtype,new_idx))


        ordered_dict = self.sort(unordered_options)
        # [f'{k} : {v} : {n}' for n,(k,v) in enumerate(ordered_dict.items())]
        # self.dropdown.update_data([f'{k} : {v} : {n}' for n,(k,v) in enumerate(ordered_dict.items())])
        self.dropdown.update_data(self.drop_down(ordered_dict))
        self.new_options = ordered_dict
        
    def undo(self):
        self.new_options = {}
        self.rename_map = {}
        self.ids['input'].text = ""
        self.dropdown.selection = ""
        self.dropdown.update_data(self.drop_down(self.options))
    
    def sort(self,unordered_list):
        return {k: v for k, v, order in sorted(unordered_list, key=lambda x: x[2])}
    
    
