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
}

class CustomColors(EventDispatcher):    
    colors = DictProperty({})
    
    def update_colors(self, theme_style):
        self.colors = {k: get_color_from_hex(colors[theme_style]) for k,colors in THEME_MAP.items()}
    