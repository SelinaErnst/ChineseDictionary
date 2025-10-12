from kivy.utils import platform
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.metrics import Metrics, NUMERIC_FORMATS, dp, sp, inch, dpi2px
from pathlib import Path
from packages.kivymd_templates.dialogs import GrantAccess

class MyApp(MDApp):
    platform=platform
    metrics=Metrics
    settings=None
    root_folder='./'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        root_folder = Path(self.directory)
        self.root_folder = str(root_folder.resolve())+'/'
        
    def test(self,msg="TEST"):
        print(msg)
    
    def apply_palette(self,palette):
        self.theme_cls.primary_palette = palette
    
    def apply_styles(self,style:str=None):
        self.theme_cls.theme_style = style
        
    def dismiss_dialog(self):
        if hasattr(self.wm.current_screen,'dialog') \
            and self.wm.current_screen.dialog._is_open:
                self.wm.current_screen.dialog.dismiss()
                return True
        else: return False

    def hide_widget(self,widget,do_hide=True):
        if hasattr(widget, 'saved_attrs'):
            if not do_hide:
                widget.height, widget.size_hint_y, widget.width, widget.size_hint_x, widget.opacity, widget.disabled = widget.saved_attrs
                del widget.saved_attrs
        elif do_hide:
            widget.saved_attrs = widget.height, widget.size_hint_y, widget.width, widget.size_hint_x, widget.opacity, widget.disabled
            widget.height, widget.size_hint_y, widget.width, widget.size_hint_x, widget.opacity, widget.disabled = 0, None, 0, None, 0, True


        
    def add_window_manager(self,wm):
        self.wm = wm
        
    def hook_keyboard(self,window,key,*largs):
        if key == 27:
            if self.dismiss_dialog():
                return True
            return self.previous_screen()
        return False
        
    def switch_screen(self,screen_name,direction,remember=True):
        current_screen_name = self.wm.current
        current_direction = self.wm.transition.direction
        current_screen = self.wm.current_screen
        if screen_name != current_screen_name \
            and screen_name in self.wm.screen_names:
                if self.wm.previous_screen_names != []\
                    and self.wm.previous_screen_names[-1] == screen_name:
                    self.wm.previous_screen_names = self.wm.previous_screen_names[:-1]
                    self.wm.previous_transition_directions = self.wm.previous_transition_directions[:-1]
                if remember: 
                    self.wm.previous_screen_names.append(current_screen_name)
                    self.wm.previous_transition_directions.append(direction)
                if screen_name=='home': 
                    self.wm.previous_screen_names=[]
                    self.wm.previous_transition_directions=[]
                self.wm.current = screen_name
                self.wm.transition.direction = direction
                if current_screen_name.startswith('C'):
                    self.wm.remove_widget(current_screen)
                return self.wm.current_screen
    
    def previous_screen(self):
        if self.wm.previous_screen_names != []:
            previous_screen_name=self.wm.previous_screen_names[-1]
            previous_direction=self.wm.previous_transition_directions[-1]
            self.wm.previous_screen_names=self.wm.previous_screen_names[:-1]
            self.wm.previous_transition_directions=self.wm.previous_transition_directions[:-1]
            if previous_direction in ['right','left']:
                direction = 'right' if previous_direction == 'left' else 'left'
            elif previous_direction in ['up','down']:
                direction = 'up' if previous_direction == 'down' else 'up'
            self.switch_screen(previous_screen_name,direction,remember=False)
            return True
        else:
            return False
        
    def get_diag_inch(self):
        xpix = Window.size[0]
        ypix = Window.size[1]
        xinch = xpix/dpi2px(1,'in')
        yinch = ypix/dpi2px(1,'in')
        diag_inch = (xinch*xinch+yinch*yinch)**.5
        return diag_inch
        
    def get_metrics(self):
        window_metrics = f"\nwindow size = {Window.size}\ndiagonal = {self.get_diag_inch()}"
        metrics = f"\ndensity = {self.metrics.density} \ndpi = {self.metrics.dpi} \nfontscale = {self.metrics.fontscale}"
        more_metrics = f"\ndp(1) = {dp(1)} \nsp(1) = {sp(1)} \ninch(1) = {inch(1)}"
        return f"{self.platform}: {window_metrics} {metrics}"
    
    def get_window_size(self):
        return Window.size
    
    def _show_validation_dialog(self):
        if self.platform == "android":
            from jnius import autoclass
            done=False
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                support_text="To access files on the phone it is required to grant the app access to the storage."
                deny_text='No'
            else:
                done=True
                support_text="Storage access was already granted."
                deny_text='Return'
        elif self.platform == "linux":
            done=True
            support_text=f"For {self.platform} no further storage access needs to be granted."
            deny_text='Return'

        self.show_permission_popup = GrantAccess(
            support_text=support_text, deny_text=deny_text, done=done)
        self.show_permission_popup.open()