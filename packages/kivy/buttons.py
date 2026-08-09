
from kivy.properties import (
    StringProperty, 
    ListProperty, 
    NumericProperty, 
    DictProperty,
    )
from kivymd.uix.button import MDButton
from kivymd.uix.stacklayout import MDStackLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
        
from kivy.lang import Builder
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'buttons.kv'))

# = ============================================================== = #
# =                             TOGGLE                             = #
# = ============================================================== = #

class Toggle(MDStackLayout):
    include = ListProperty()
    exclude = ListProperty()
    
    def switch(self,child):
        for c in self.children:
            if c == child:
                child.toggle_on()
            else:
                c.toggle_off()
    def turn_on(self):
        for c in self.children:
            c.toggle_on()
            
        from main import ChD
        app = ChD.get_running_app()
        if hasattr(app.wm.current_screen,'set_list_items'):
            app.wm.current_screen.set_list_items()
            
    def turn_off(self):
        for c in self.children:
            c.toggle_off()
        
        from main import ChD
        app = ChD.get_running_app()
        if hasattr(app.wm.current_screen,'clear_list'):
            app.wm.current_screen.clear_list()
            
class ToggleButton(MDButton):
    active_filter=StringProperty('ignore')
    switch=StringProperty()
    switch_map=DictProperty()
    padding=NumericProperty(20)
    kind=StringProperty()
    text=StringProperty()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind(on_release=self.select_action)
    
    def on_switch_map(self,instance,value):
        if self.icon in self.switch_map.values(): 
            self.switch = [(switch,icon) for switch,icon in self.switch_map.items() if icon==self.icon][0][0]
           
    def select_action(self,instance):
        if self.kind=='select_multiple':  
            self.toggle_two(only_one=False)
        elif self.kind=='select_one':
            self.toggle_two(only_one=True)
        elif self.kind=='filter':
            self.toggle_three()
        elif self.kind=='switch':
            self.switch_icons()
            
    def on_kind(self,instance,value):
        self.unbind(on_release=self.select_action) 
        self.bind(on_release=self.select_action)
        
    def switch_icons(self):
        switch,icon = [(switch,icon) for switch,icon in self.switch_map.items() if icon!=self.icon][0]
        self.icon = icon
        self.switch = switch
        
        from main import ChD
        app = ChD.get_running_app()
        if hasattr(app.wm.current_screen,'set_list_items'):
            app.wm.current_screen.set_list_items()
            
    def toggle_on(self):
        self.active_filter = 'include'
        if hasattr(self.parent,'include'): self.parent.include.append(self.text)
        
    def toggle_off(self):
        self.active_filter = 'ignore'
        if hasattr(self.parent,'include'): 
            if self.text in self.parent.include: self.parent.include.remove(self.text)
        
    def toggle_two(self,only_one=True):
        from main import ChD
        app = ChD.get_running_app()
        if only_one and hasattr(self.parent,'switch'):
            self.parent.switch(self)
        elif only_one:
            self.toggle_on()
            for c in self.parent.children:
                if c != self: c.toggle_off()
        else:
            if self.active_filter == 'ignore':
                self.toggle_on()
            elif self.active_filter == 'include':
                self.toggle_off()
                
        if hasattr(app.wm.current_screen,'set_list_items'):
            app.wm.current_screen.set_list_items()

    def toggle_three(self):

        if self.active_filter == 'ignore':
            self.active_filter = 'include'
            if hasattr(self.parent,'include'): 
                self.parent.include.append(self.text)
        elif self.active_filter == 'include':
            self.active_filter = 'exclude'
            if hasattr(self.parent,'include'): 
                self.parent.include.remove(self.text)
                self.parent.exclude.append(self.text)
        elif self.active_filter == 'exclude':
            self.active_filter = 'ignore'
            if hasattr(self.parent,'exclude'): 
                self.parent.exclude.remove(self.text)
            
        from main import ChD
        app = ChD.get_running_app()
        if hasattr(app.wm.current_screen,'set_list_items'):
            app.wm.current_screen.set_list_items()

    def get_color(self,active_color,color_focus,color_un_focus):
        if self.active_filter == 'include' and color_focus!=None:
            return color_focus
        elif self.active_filter == 'ignore' and color_un_focus!=None:
            return color_un_focus
        else:
            return active_color
            
        
class IconTextToggleButton(ToggleButton):
    _text_left_pad = 0
    _text_right_pad = 0
    _icon_left_pad = 0
    
class IconToggleButton(ToggleButton):
    pass
class TextToggleButton(ToggleButton):
    pass

class MultipleToggle(RecycleDataViewBehavior, TextToggleButton):
    
    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        self.rv = rv
        self.data = data
        return super().refresh_view_attrs(rv, index, data)
    
    def toggle_on(self):
        
        if hasattr(self,'data'):
            self.data.update({'active_filter':'include'})
            self.refresh_view_attrs(rv=self.rv,index=self.index,data=self.data)
        return super().toggle_on()
    
    def toggle_off(self):
        if hasattr(self,'data'):
            self.data.update({'active_filter':'ignore'})
            self.refresh_view_attrs(rv=self.rv,index=self.index,data=self.data)
        return super().toggle_off()

# = ============================================================== = #
# =                          ICON AND TEXT                         = #
# = ============================================================== = #

class MyIconTextButton(MDButton):
    text=StringProperty()
    icon=StringProperty()
    padding=NumericProperty(30)
    _text_left_pad = 0
    _text_right_pad = 0
    _icon_left_pad = 0
    
class RigidIconTextButton(MyIconTextButton):
    # width determines size of Button
    # used in: MakeDecision
    pass

class MultiLineIconTextButton(MyIconTextButton):
    # when text has \n
    pass

# used with Interface
class NavigationButton(MDButton):
    text=StringProperty()
    icon=StringProperty()

# = ============================================================== = #
# =                            ONLY TEXT                           = #
# = ============================================================== = #

class MyTextButton(MDButton):
    text=StringProperty()
    padding=ListProperty([30,30,30,30])
    
class RigidTextButton(MyTextButton):
    pass

class FlexTextButton(MyTextButton):
    pass


# = ============================================================== = #
# =                              ICON                              = #
# = ============================================================== = #

class MyIconButton(MDButton):
    # size=ListProperty([100,100])
    # icon=StringProperty()
    pass