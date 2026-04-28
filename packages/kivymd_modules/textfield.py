from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ObjectProperty,
    ListProperty,
    BooleanProperty
    )

from kivy.lang import Builder
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
Builder.load_file(current_dir+'/textfield.kv')

# = ============================================================== = #
# =                         ONLY TEXTFIELD                         = #
# = ============================================================== = #

class EntryField(MDTextField):
    hint=StringProperty()
    is_correct=ObjectProperty()
    standard_height=NumericProperty(200)
    allow_empty=BooleanProperty(False)
    
    def _get_has_error(self) -> bool:
        has_error = super()._get_has_error()
        has_error = (has_error or not self.is_correct())
        return has_error
    
    def set_text(self, instance, text):
        
        def is_incorrect():
            if self.text=="": is_empty=True
            else: is_empty=False
            if not is_empty: return self._get_has_error()
            elif not self.allow_empty: return True
            else: return False
            
        def set_text(*args):
            import re
            self.text = re.sub("\n", " ", text) if not self.multiline else text
            self.set_max_text_length()
            
            self.error=is_incorrect()
            
            # Start the appropriate texture animations when programmatically
            # pasting text into a text field.
            from kivymd.font_definitions import theme_font_styles
            if len(self.text) and not self.focus:
                if self._hint_text_label:
                    self._hint_text_label.font_size = theme_font_styles[
                        self._hint_text_label.font_style
                    ]["small"]["font-size"]
                    self._hint_text_label.texture_update()
                    self.set_hint_text_font_size()

            if (not self.text and not self.focus) or (
                self.text and not self.focus
            ):
                self.on_focus(instance, False)

            if self.multiline:
                self.adjust_height()

        set_text()
    
class Property(EntryField):
    standard_height=NumericProperty(100)

# = ============================================================== = #
# =                       TEXTFIELD AND ICON                       = #
# = ============================================================== = #

class EntryFieldWithIcon(MDBoxLayout):
    text=StringProperty()
    hint=StringProperty()
    role=StringProperty("medium")
    icon=StringProperty()
    press_button=ObjectProperty(True)
    is_correct=ObjectProperty() # function
    allow_empty=BooleanProperty(False)
    