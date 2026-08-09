from kivy.event import EventDispatcher
from kivy.properties import DictProperty
from kivy.utils import get_color_from_hex

THEME_MAP = {
    "level": {"Light": "#FFFFFF", "Dark": "#111111"},
    "text_level": {"Light": "111111", "Dark": "#FFFFFF"},
    "levelA1": {"Light": "#eebc90", "Dark": "#de800d"},
    "levelA2": {"Light": "#ecee90", "Dark": "#dede0d"},
    "levelB1": {"Light": "#90ee9e", "Dark": "#829e06"},
    "levelB2": {"Light": "#90c8ee", "Dark": "#069e8f"},
    "levelC1": {"Light": "#a890ee", "Dark": "#7b30f2"},
    "levelC2": {"Light": "#ee90e3", "Dark": "#e04fd4"},
    "text_levelA1": {"Light": "#ab7444", "Dark": "#873e01"},
    "text_levelA2": {"Light": "#9c9e3f", "Dark": "#8c8803"},
    "text_levelB1": {"Light": "#418a4c", "Dark": "#475703"},
    "text_levelB2": {"Light": "#326587", "Dark": "#034d45"},
    "text_levelC1": {"Light": "#5e46a3", "Dark": "#320e6b"},
    "text_levelC2": {"Light": "#ad45a1", "Dark": "#63105d"},
    "text": {"Light": "#111111", "Dark": "#FFFFFF"},
    "inverse_text": {"Light": "#FFFFFF", "Dark": "#111111"},
    
    "app":{'Light': "#003B3B","Dark": "#003535"},
    "clear":{'Light': "#003B3B","Dark": "#003535"},
    "bottom":{'Light': "#003B3B","Dark": "#003535"},
    "bg":{'Light': "#FFFFFF","Dark": "#070a0a"},
    "head":{'Light': "#268383","Dark": "#005151"},
}

more_colors = [
    "bg_overlay","head_content","head_text",
    "list_element_bg","list_head_bg","bullet",
    'dialog_bg','dialog_button_bg','dialog_button_fg',
    'text_input_bg','text_input_fg',
    'textfield_text','textfield_error','textfield_set_normal','textfield_set_focus','textfield_search',
    "button_bg","button_fg",
    "ignore_bg","include_bg","exclude_bg","ignore_text","include_text","exclude_text",
    ]
THEME_MAP.update({color:{'Light': "#FFFFFF","Dark": "#FFFFFF"}  for color in more_colors})

def darken(color,multiplier):
    alpha = color[-1]
    color = [i*multiplier for i in color[:-1]]+[alpha]
    return color

def brighten(color,multiplier):
    alpha = color[-1]
    color = [i+(1-i)*multiplier for i in color[:-1]]+[alpha]
    return color

def to_hex(color):
    hex_color = '#' + ''.join(f'{int(round(c * 255)):02x}' for c in color[:3])
    return hex_color
    
class CustomColors(EventDispatcher):    
    colors = DictProperty({})
        
    
    def update_colors(self, theme_cls):
        
        self.colors = {k: get_color_from_hex(colors[theme_cls.theme_style]) for k,colors in THEME_MAP.items()}
        
        LIGHT_dark_bg_color = theme_cls.surfaceDimColor #grey
        LIGHT_light_bg_color = theme_cls.surfaceContainerColor
        LIGHT_super_light_bg_color = theme_cls.surfaceContainerLowColor # surfaceColor / surfaceContainerLowColor
        LIGHT_dark_primary_color=theme_cls.primaryColor
        LIGHT_slightly_dark_primary_color=theme_cls.primary_paletteKeyColorColor
        LIGHT_light_primary_color=theme_cls.inversePrimaryColor
        LIGHT_super_light_primary_color=theme_cls.onPrimaryColor # brighten(LIGHT_light_primary_color,.7) / onPrimaryColor
        
        
        DARK_super_dark_bg_color = darken(theme_cls.surfaceDimColor,.5)
        DARK_dark_bg_color = theme_cls.surfaceDimColor
        DARK_light_bg_color = theme_cls.surfaceContainerLowColor #surfaceContainerLowColor
        DARK_super_light_bg_color = brighten(theme_cls.surfaceContainerHighestColor,.8)
        # DARK_super_dark_primary_color = theme_cls.onPrimaryColor
        DARK_dark_primary_color = theme_cls.onPrimaryFixedVariantColor
        DARK_slightly_dark_primary_color = theme_cls.inversePrimaryColor
        DARK_light_primary_color = theme_cls.primary_paletteKeyColorColor
        DARK_super_light_primary_color = theme_cls.surfaceTintColor
        DARK_bright_color=brighten(theme_cls.primaryColor,.7)

        theme_cls_colors = {
            'app':{"Light":LIGHT_dark_primary_color,"Dark":DARK_dark_primary_color},
            'clear':{"Light":[0,0,0,0],"Dark":[0,0,0,0]},
            'bottom':{'Light':LIGHT_dark_primary_color,'Dark':DARK_dark_primary_color},
            'bg':{"Light":LIGHT_dark_bg_color,"Dark":DARK_super_dark_bg_color},
            'bg_overlay':{"Light":[0, 0, 0, 0.7],"Dark":[0, 0, 0, 0.9]},
            'head':{'Light':LIGHT_slightly_dark_primary_color,'Dark':DARK_slightly_dark_primary_color},
            'head_content':{'Light':LIGHT_light_primary_color,'Dark':DARK_light_primary_color},
            'head_text':{'Light':LIGHT_dark_primary_color,'Dark':DARK_bright_color},
            'list_element_bg':{'Light':LIGHT_light_bg_color,'Dark':DARK_dark_bg_color},
            'list_head_bg':{'Light':LIGHT_super_light_bg_color,'Dark':DARK_light_bg_color},
            'bullet':{'Light':LIGHT_dark_primary_color,'Dark':DARK_bright_color},
            'dialog_bg':{'Light':LIGHT_super_light_bg_color,'Dark':DARK_light_bg_color},
            'dialog_button_bg':{'Light':darken(LIGHT_super_light_bg_color,.95),'Dark':brighten(DARK_light_bg_color,.03)},
            'dialog_button_fg':{'Light':LIGHT_slightly_dark_primary_color,'Dark':DARK_bright_color},
            'text_input_bg':{'Light':LIGHT_light_bg_color,'Dark':DARK_dark_bg_color},
            'text_input_fg':{'Light':darken(theme_cls.outlineColor,.8),'Dark':brighten(theme_cls.outlineColor,.2)},
            'button_bg':{'Light':LIGHT_slightly_dark_primary_color,'Dark':DARK_slightly_dark_primary_color},
            'button_fg':{'Light':LIGHT_super_light_primary_color,'Dark':DARK_bright_color},

            'textfield_error':{'Light':theme_cls.errorContainerColor,'Dark':theme_cls.errorContainerColor},
            'textfield_search':{'Light':LIGHT_super_light_primary_color,'Dark':DARK_bright_color},
            'textfield_set_normal':{'Light':brighten(LIGHT_dark_primary_color,.3),'Dark':DARK_super_light_bg_color},
            'textfield_set_focus':{'Light':LIGHT_dark_primary_color,'Dark':DARK_bright_color},
            
            "ignore_bg":{"Light":darken(LIGHT_slightly_dark_primary_color,.8),"Dark": brighten(DARK_slightly_dark_primary_color,.2)},
            "ignore_text":{"Light":LIGHT_dark_primary_color,"Dark":DARK_dark_primary_color},
            "include_bg":{"Light":LIGHT_dark_primary_color,"Dark":DARK_super_light_primary_color},
            "include_text":{"Light":LIGHT_super_light_primary_color,"Dark":DARK_dark_primary_color},
            "exclude_bg":{"Light":theme_cls.errorColor,"Dark":theme_cls.errorColor},
            "exclude_text":{"Light":theme_cls.onErrorContainerColor,"Dark":theme_cls.onErrorContainerColor},
        }
        
        self.colors.update({k: colors[theme_cls.theme_style] for k,colors in theme_cls_colors.items()})
