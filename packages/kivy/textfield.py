from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout

from kivy.clock import Clock
from kivy.properties import (
    StringProperty, 
    NumericProperty, 
    ObjectProperty,
    ListProperty,
    BooleanProperty,
    ColorProperty,
    OptionProperty
    )

from kivy.lang import Builder
from pathlib import Path
current_dir = Path(__file__).resolve().parent
Builder.load_file(str(current_dir/'textfield.kv'))

# = ============================================================== = #
# =                      TEXTFIELD OVERWRITTEN                     = #
# = ============================================================== = #
import re
from datetime import date
from kivymd.font_definitions import theme_font_styles
from kivymd.theming import ThemableBehavior, ThemeManager
from kivymd.uix.behaviors import BackgroundColorBehavior, DeclarativeBehavior
from kivymd.uix.behaviors.state_layer_behavior import StateLayerBehavior
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
    VariableListProperty,
)
from kivy.uix.textinput import TextInput
from kivymd.uix.textfield import (
    # Validator, 
    # AutoFormatTelephoneNumber, 
    MDTextFieldHelperText,
    MDTextFieldHintText,
    MDTextFieldLeadingIcon,
    MDTextFieldMaxLengthText,
    MDTextFieldTrailingIcon,
    )

class AutoFormatTelephoneNumber:
    def __init__(self):
        self._backspace = False
    def isnumeric(self, value) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False
    def do_backspace(self, *args) -> None:
        if self.validator and self.validator == "phone":
            self._backspace = True
            text = self.text
            text = text[:-1]
            self.text = text
            self._backspace = False
    def field_filter(self, value, boolean) -> None:
        if self.validator and self.validator == "phone":
            if len(self.text) == 14:
                return
            if self.isnumeric(value):
                return value
        return value
    def format(self, value) -> None:
        if value != "" and not value.isspace() and not self._backspace:
            if len(value) <= 1 and self.focus:
                self.text = value
                self._check_cursor()
            elif len(value) == 4:
                start = self.text[:-1]
                end = self.text[-1]
                self.text = "%s) %s" % (start, end)
                self._check_cursor()
            elif len(value) == 8:
                self.text += "-"
                self._check_cursor()
            elif len(value) in [12, 16]:
                start = self.text[:-1]
                end = self.text[-1]
                self.text = "%s-%s" % (start, end)
                self._check_cursor()
    def _check_cursor(self):
        def set_pos_cursor(pos_corsor, interval=0.5):
            self.cursor = (pos_corsor, 0)
        if self.focus:
            Clock.schedule_once(lambda x: set_pos_cursor(len(self.text)), 0.1)
class Validator:
    datetime_date = ObjectProperty()
    date_interval = ListProperty([None, None])
    date_format = OptionProperty(
        None,
        options=[
            "dd/mm/yyyy",
            "mm/dd/yyyy",
            "yyyy/mm/dd",
        ],
    )

    def is_email_valid(self, text: str) -> bool:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", text):
            return True
        return False

    def is_time_valid(self, text: str) -> bool:
        if re.match(r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9])$", text) or re.match(
            r"^(2[0-3]|[01]?[0-9]):([0-5]?[0-9]):([0-5]?[0-9])$", text
        ):
            return False

        return True

    def is_date_valid(self, text: str) -> bool:
        if not self.date_format:
            raise Exception("TextInput date_format was not defined.")
        dd = "[0][1-9]|[1-2][0-9]|[3][0-1]"
        mm = "[0][1-9]|[1][0-2]"
        yyyy = "[0-9][0-9][0-9][0-9]"
        fmt = self.date_format.split("/")
        args = locals()
        if re.match(
            f"^({args[fmt[0]]})/({args[fmt[1]]})/({args[fmt[2]]})$", text
        ):
            input_split = text.split("/")
            args[fmt[0]] = input_split[0]
            args[fmt[1]] = input_split[1]
            args[fmt[2]] = input_split[2]
            try:
                datetime = date(
                    int(args["yyyy"]), int(args["mm"]), int(args["dd"])
                )
            except ValueError:
                return True

            if self.date_interval:
                if (
                    self.date_interval[0]
                    and not self.date_interval[0] <= datetime
                    or self.date_interval[1]
                    and not datetime <= self.date_interval[1]
                ):
                    return True

            self.datetime_date = datetime
            return False
        return True

    def on_date_interval(self, *args) -> None:
        def on_date_interval():
            if not self.date_format:
                raise Exception("TextInput date_format was not defined.")

            fmt = self.date_format.split("/")
            args = {}
            try:
                if self.date_interval[0] and not isinstance(
                    self.date_interval[0], date
                ):
                    split = self.date_interval[0].split("/")
                    args[fmt[0]] = split[0]
                    args[fmt[1]] = split[1]
                    args[fmt[2]] = split[2]
                    self.date_interval[0] = date(
                        int(args["yyyy"]), int(args["mm"]), int(args["dd"])
                    )
                if self.date_interval[1] and not isinstance(
                    self.date_interval[1], date
                ):
                    split = self.date_interval[1].split("/")
                    args[fmt[0]] = split[0]
                    args[fmt[1]] = split[1]
                    args[fmt[2]] = split[2]
                    self.date_interval[1] = date(
                        int(args["yyyy"]), int(args["mm"]), int(args["dd"])
                    )

            except Exception:
                raise Exception(
                    r"TextInput date_interval was defined incorrectly, "
                    r"it must be composed of <class 'datetime.date'> objects "
                    r"or strings following current date_format."
                )

            if isinstance(self.date_interval[0], date) and isinstance(
                self.date_interval[1], date
            ):
                if self.date_interval[0] >= self.date_interval[1]:
                    raise Exception(
                        "TextInput date_interval last date must be greater "
                        "than the first date or set to None."
                    )

        Clock.schedule_once(lambda x: on_date_interval())

class MyTextField(
    DeclarativeBehavior,
    StateLayerBehavior,
    ThemableBehavior,
    TextInput,
    Validator,
    AutoFormatTelephoneNumber,
    BackgroundColorBehavior,
):
    font_style = StringProperty("Body")
    role = StringProperty("large")
    mode = OptionProperty("outlined", options=["outlined", "filled"])
    error_color = ColorProperty(None)
    error = BooleanProperty(False)
    text_color_normal = ColorProperty(None)
    text_color_focus = ColorProperty(None)
    radius = VariableListProperty([dp(4), dp(4), dp(4), dp(4)])
    required = BooleanProperty(False)
    cursor_color = ColorProperty(None)
    line_color_normal = ColorProperty(None)
    line_color_focus = ColorProperty(None)
    fill_color_normal = ColorProperty(None)
    fill_color_focus = ColorProperty(None)
    max_height = NumericProperty(0)
    min_height = NumericProperty(0)
    phone_mask = StringProperty("")
    validator = OptionProperty(None, options=["date", "email", "time", "phone"])
    _helper_text_label = ObjectProperty()
    _hint_text_label = ObjectProperty()
    _hint_text_label_small_font = sp(10)
    _hint_text_label_large_font = sp(12)
    _leading_icon = ObjectProperty()
    _trailing_icon = ObjectProperty()
    _max_length_label = ObjectProperty()
    _max_length = "0"
    _indicator_height = NumericProperty(dp(1))
    _outline_height = NumericProperty(dp(1))
    _hint_x = NumericProperty(0)
    _hint_y = NumericProperty(0)
    _left_x_axis_pos = NumericProperty(dp(32))
    _right_x_axis_pos = NumericProperty(dp(32))
    
    hint_animation = False
    allow_empty=BooleanProperty(False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind(text=self.set_text)
        self.bind(_lines=self.adjust_height)
        self.theme_cls.bind(
            primary_palette=self.update_colors,
            theme_style=self.update_colors,
        )
        Clock.schedule_once(self._check_text)
        Clock.schedule_once(self._move_hint)

    def _move_hint(self,*args):
        if self.hint == "": 
            self.hint_animation=True
        if self._hint_text_label and not self.hint_animation: 
            self._hint_text_label.font_size = theme_font_styles[self._hint_text_label.font_style]["small"]["font-size"]
            self._hint_text_label.texture_update()
            h = (self.height / 2) - (self._hint_text_label.texture_size[1] / 2)
            p = (dp(8) if self.multiline and self.height != self.min_height else dp(8))
            h = h-53
            self.set_pos_hint_text(h,0,)
            self.set_hint_text_font_size()
            if self.mode == "outlined":
                self.set_space_in_line(dp(14), self._hint_text_label.texture_size[0] + dp(18),)

    def update_colors(
        self, theme_manager: ThemeManager, theme_color: str
    ) -> None:
        def update_colors(*args):
            if not self.disabled:
                self.on_focus(self, self.focus)
            else:
                self.on_disabled(self, self.disabled)

        Clock.schedule_once(update_colors, 1)

    def add_widget(self, widget, index=0, canvas=None):
        if isinstance(widget, MDTextFieldHelperText):
            self._helper_text_label = widget
            self._set_texture_helper_text_color(text_color_focus=False)
        if isinstance(widget, MDTextFieldHintText):
            self._hint_text_label = widget
            self._set_texture_hint_text_color(text_color_focus=False)
        if isinstance(widget, MDTextFieldLeadingIcon):
            self._leading_icon = widget
            widget._text_field = self
            self._set_texture_leading_icons_color(icon_color_focus=False)
        if isinstance(widget, MDTextFieldTrailingIcon):
            self._trailing_icon = widget
            widget._text_field = self
            self._set_texture_trailing_icons_color(icon_color_focus=False)
        if isinstance(widget, MDTextFieldMaxLengthText):
            self._max_length_label = widget
            self._set_texture_max_length_color(text_color_focus=False)
        else:
            return super().add_widget(widget)

    def set_texture_color(
        self, texture, canvas_group, color: list, error: bool = False
    ) -> None:
        def update_texture(grop_name, instance):
            rectangle = self.canvas.before.get_group(grop_name)[0]
            rectangle.texture = instance.texture
            rectangle.size = instance.texture_size
            if instance is self._helper_text_label:
                rectangle.pos = self.get_adjusted_pos_helper_text_label()
            elif instance is self._leading_icon:
                if self._hint_text_label:
                    rectangle_hint = self.canvas.after.get_group(
                        "hint-text-rectangle"
                    )[0]
                    rectangle_hint.texture = self._hint_text_label.texture
                    rectangle_hint.size = self._hint_text_label.texture_size
                    rectangle_hint.pos = self.get_adjusted_pos_hint_text_label()
                    self._hint_text_label.texture_update()
                rectangle.pos = self.get_adjusted_pos_leading_icon()
            elif instance is self._trailing_icon:
                rectangle.pos = self.get_adjusted_pos_trailing_icon()
            elif instance is self._max_length_label:
                rectangle.pos = self.get_adjusted_pos_max_length_label()
            instance.texture_update()

        def update_hint_text_rectangle(*args):
            hint_text_rectangle = self.canvas.after.get_group(
                "hint-text-rectangle"
            )[0]
            hint_text_rectangle.texture = None
            texture.texture_update()
            hint_text_rectangle.texture = texture.texture

        if texture:
            Animation(rgba=color, d=0).start(canvas_group)
            a = Animation(color=color, d=0)

            if texture is self._hint_text_label:
                a.bind(on_complete=update_hint_text_rectangle)
            elif texture is self._helper_text_label:
                update_texture("helper-text-rectangle", self._helper_text_label)
            elif texture is self._leading_icon:
                update_texture("leading-icon-rectangle", self._leading_icon)
            elif texture is self._trailing_icon:
                update_texture("trailing-icon-rectangle", self._trailing_icon)
            elif texture is self._max_length_label:
                update_texture("max-length-rect", self._max_length_label)

            a.start(texture)

    def get_adjusted_pos_max_length_label(self) -> tuple:
        return ((self.x + self.width) - (self._max_length_label.texture_size[0] + dp(16)),self.y - dp(18),)

    def get_adjusted_pos_helper_text_label(self) -> tuple:
        return (self.x + (dp(16) if self.mode == "filled" else (0 if self.mode == "filled" else dp(12))), self.y + dp(-18),)

    def get_adjusted_pos_trailing_icon(self) -> tuple:
        return ((self.width + self.x) - (self._trailing_icon.texture_size[1]) - dp(14),self.center_y - self._trailing_icon.texture_size[1] / 2,)

    def get_adjusted_pos_leading_icon(self) -> tuple:
        return (self.x + (dp(12) if self.mode != "outlined" else (dp(12) if self.mode != "filled" else (dp(4) if not self._leading_icon else dp(16)))), self.center_y - self._leading_icon.texture_size[1] / 2,)

    def get_adjusted_pos_hint_text_label(self) -> tuple:
        return (
            self.x
            + (
                dp(16)
                if not self._leading_icon
                else self._leading_icon.texture_size[0] + dp(28) + self._hint_x
            ),
            (
                (
                    self.y
                    + self.height
                    + (self._hint_text_label.texture_size[1] / 2)
                    - (self.height / 2)
                    - self._hint_y
                )
                if not self.multiline
                else (
                    self.top - self._hint_text_label.texture_size[1] + dp(8)
                    if self.text
                    else (
                        self.y
                        + self.height
                        + (self._hint_text_label.texture_size[1] / 2)
                        - (self.height / 2)
                        - self._hint_y
                    )
                )
            ),
        )

    def set_pos_hint_text(self, y: float, x: float) -> None:
        Animation(_hint_y=y, _hint_x=x, d=0.2, t="out_quad").start(self)
    
    def set_hint_text_font_size(self) -> None:
        Animation(
            size=self._hint_text_label.texture_size, d=0.2, t="out_quad"
        ).start(self.canvas.after.get_group("hint-text-rectangle")[0])

    def set_space_in_line(
        self, left_width: float | int, right_width: float | int
    ) -> None:
        Animation(_left_x_axis_pos=left_width, d=0.2, t="out_quad").start(self)
        Animation(_right_x_axis_pos=right_width, d=0.2, t="out_quad").start(
            self
        )

    def set_max_text_length(self) -> None:
        if self._max_length_label:
            self._max_length_label.text = ""
            self._max_length_label.text = (
                f"{len(self.text)}/{self._max_length_label.max_text_length}"
            )
            self._max_length_label.texture_update()
            max_length_rect = self.canvas.before.get_group("max-length-rect")[0]
            max_length_rect.texture = None
            max_length_rect.texture = self._max_length_label.texture
            max_length_rect.size = self._max_length_label.texture_size
            max_length_rect.pos = (
                (self.x + self.width)
                - (self._max_length_label.texture_size[0] + dp(16)),
                self.y - dp(18),
            )

    def adjust_height(self, *args) -> None:
        padding_top, padding_bottom = (
            self.padding[1] + dp(9),
            self.padding[3],
        )

        line_height = self.line_height
        line_count = max(1, len(self._lines))
        new_height = line_height * line_count + padding_top + padding_bottom

        if self.multiline:
            if self.min_height == 0: self.min_height = self.height
            # print(new_height, self.min_height)
            self.height = max(new_height, self.min_height)
        else:
            self.height = max(new_height, self.height)

    def set_text(self, instance, text):

        def is_incorrect():
            if self.text=="": is_empty=True
            else: is_empty=False
            if not is_empty: return self._get_has_error()
            elif not self.allow_empty: return True
            else: return False
            
        def set_text(*args):
            self.text = re.sub("\n", " ", text) if not self.multiline else text
            self.set_max_text_length()
            self.error=is_incorrect()
            if len(self.text) and not self.focus:
                if self._hint_text_label and self.hint_animation:
                    self._hint_text_label.font_size = theme_font_styles[
                        self._hint_text_label.font_style
                    ]["small"]["font-size"]
                    self._hint_text_label.texture_update()
                    self.set_hint_text_font_size()

            if (not self.text and not self.focus) or (
                self.text and not self.focus
            ):
                self.on_focus(instance, False)

        set_text()
        self._set_texture_hint_text_color(text_color_focus=True)
        
    def on_focus(self, instance, focus: bool) -> None:
        
        if focus:
            if self.mode == "filled":
                Animation(_indicator_height=dp(1.25), d=0).start(self)
            else:
                Animation(_outline_height=dp(1.25), d=0).start(self)

            if self._trailing_icon:
                self._set_texture_trailing_icons_color(icon_color_focus=True)
            if self._leading_icon:
                self._set_texture_leading_icons_color(icon_color_focus=True)
            if self._max_length_label and not self.error:
                self._set_texture_max_length_color(text_color_focus=True)

            if self._helper_text_label and self._helper_text_label.mode in (
                "on_focus",
                "persistent",
            ):
                self._set_texture_helper_text_color(text_color_focus=True)
            if (
                self._helper_text_label
                and self._helper_text_label.mode == "on_error"
                and not self.error
            ):
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        self._helper_text_label,
                        self.canvas.before.get_group("helper-text-color")[0],
                        self.theme_cls.transparentColor,
                    )
                )
            if self._hint_text_label and self.hint_animation:
                self._set_texture_hint_text_color(text_color_focus=True)
                self.set_pos_hint_text(
                    0 if self.mode != "outlined" else dp(-14),
                    (
                        (
                            -(
                                (
                                    self._leading_icon.texture_size[0]
                                    if self._leading_icon
                                    else 0
                                )
                                + dp(12)
                            )
                            if self._leading_icon
                            else 0
                        )
                        if self.mode == "outlined"
                        else -(
                            (
                                self._leading_icon.texture_size[0]
                                if self._leading_icon
                                else 0
                            )
                            - dp(24)
                        )
                    ),
                )
                self._hint_text_label.font_size = theme_font_styles[
                    self._hint_text_label.font_style
                ]["small"]["font-size"]
                # self._hint_text_label.font_size = self._hint_text_label_small_font
                self._hint_text_label.texture_update()
                # self.set_hint_text_font_size()
                if self.mode == "outlined":
                    self.set_space_in_line(
                        dp(14), self._hint_text_label.texture_size[0] + dp(18)
                    )
        else:
            if self.mode == "filled":
                Animation(_indicator_height=dp(1), d=0).start(self)
            else:
                Animation(_outline_height=dp(1), d=0).start(self)

            if self._leading_icon:
                self._set_texture_leading_icons_color(icon_color_focus=False)
            if self._trailing_icon:
                self._set_texture_trailing_icons_color(icon_color_focus=False)
            if self._max_length_label and not self.error:
                self._set_texture_max_length_color(text_color_focus=False)
            if (
                self._helper_text_label
                and self._helper_text_label.mode in ["on_focus", "on_error"]
                and (
                    self._helper_text_label.mode == "on_focus" or not self.error
                )
            ):
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        self._helper_text_label,
                        self.canvas.before.get_group("helper-text-color")[0],
                        self.theme_cls.transparentColor,
                    )
                )
            elif (
                self._helper_text_label
                and self._helper_text_label.mode == "persistent"
            ):
                self._set_texture_helper_text_color(text_color_focus=False)

            if not self.text:
                if self._hint_text_label and self.hint_animation:
                    if self.mode == "outlined":
                        self.set_space_in_line(dp(32), dp(32))
                    self._hint_text_label.font_size = theme_font_styles[
                        self._hint_text_label.font_style
                    ]["large"]["font-size"]
                    # self._hint_text_label.font_size = self._hint_text_label_small_font 
                    self._hint_text_label.texture_update()
                    self.set_hint_text_font_size()
                    
                    self.set_pos_hint_text(
                        (self.height / 2)
                        - (self._hint_text_label.texture_size[1] / 2)
                        - (
                            dp(8)
                            if self.multiline and self.height != self.min_height
                            else 0
                        ),
                        0,
                    )
            else:
                if self._hint_text_label and self.hint_animation:
                    if self.mode == "outlined":
                        self.set_space_in_line(
                            dp(14),
                            self._hint_text_label.texture_size[0] + dp(18),
                        )
                    Clock.schedule_once(
                        lambda x: self.set_pos_hint_text(
                            0 if self.mode != "outlined" else dp(-14),
                            (
                                (
                                    -(
                                        (
                                            self._leading_icon.texture_size[0]
                                            if self._leading_icon
                                            else 0
                                        )
                                        + dp(12)
                                    )
                                    if self._leading_icon
                                    else 0
                                )
                                if self.mode == "outlined"
                                else -(
                                    (
                                        self._leading_icon.texture_size[0]
                                        if self._leading_icon
                                        else 0
                                    )
                                    - dp(24)
                                )
                            ),
                        )
                    )

            if self._hint_text_label:
                self._set_texture_hint_text_color(text_color_focus=False)


    def on_disabled(self, instance, disabled: bool) -> None:
        super().on_disabled(instance, disabled)

        def on_disabled(*args):
            if disabled:
                self._set_disabled_colors()
            else:
                self._set_enabled_colors()

        Clock.schedule_once(on_disabled, 0.2)

    def on_error(self, instance, error: bool) -> None:
        if error:
            if self._max_length_label:
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        self._max_length_label,
                        self.canvas.before.get_group("max-length-color")[0],
                        self._get_error_color(),
                    )
                )
            if self._hint_text_label:
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        self._hint_text_label,
                        self.canvas.after.get_group("hint-text-color")[0],
                        self._get_error_color(),
                    ),
                )
            if self._helper_text_label and self._helper_text_label.mode in (
                "persistent",
                "on_error",
            ):
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        self._helper_text_label,
                        self.canvas.before.get_group("helper-text-color")[0],
                        self._get_error_color(),
                    )
                )
            if self._trailing_icon:
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        self._trailing_icon,
                        self.canvas.before.get_group("trailing-icons-color")[0],
                        self._get_error_color(),
                    )
                )
        else:
            self.on_focus(self, self.focus)

    def on_height(self, instance, value_height: float) -> None:
        if value_height >= self.max_height and self.max_height:
            self.height = self.max_height

    def _set_texture_max_length_color(self, text_color_focus=False):
        label = self._max_length_label
        color = (
            label.text_color_focus
            if text_color_focus
            else label.text_color_normal
        ) or self.theme_cls.onSurfaceVariantColor

        Clock.schedule_once(
            lambda x: self.set_texture_color(
                label,
                self.canvas.before.get_group("max-length-color")[0],
                color,
            )
        )

    def _set_texture_hint_text_color(self, text_color_focus=False):
        label = self._hint_text_label
        if self.error:
            color = self._get_error_color()
        else:
            base_color = (
                label.text_color_focus
                if text_color_focus
                else label.text_color_normal
            )
            color = base_color or self.theme_cls.primaryColor

        Clock.schedule_once(
            lambda dt: self.set_texture_color(
                label,
                self.canvas.after.get_group("hint-text-color")[0],
                color,
            )
        )

    def _set_texture_helper_text_color(self, text_color_focus=False):
        label = self._helper_text_label

        if self.error:
            color = self._get_error_color()
        else:
            color = (
                label.text_color_focus
                if text_color_focus
                else label.text_color_normal
            ) or self.theme_cls.onSurfaceVariantColor

        Clock.schedule_once(
            lambda x: self.set_texture_color(
                label,
                self.canvas.before.get_group("helper-text-color")[0],
                color,
            )
        )

    def _set_texture_leading_icons_color(self, icon_color_focus=False):
        icon = self._leading_icon

        if icon.theme_icon_color == "Primary":
            color = self.theme_cls.onSurfaceVariantColor
        else:
            color = (
                icon.icon_color_focus
                if icon_color_focus
                else icon.icon_color_normal
            ) or self.theme_cls.onSurfaceVariantColor

        Clock.schedule_once(
            lambda x: self.set_texture_color(
                icon,
                self.canvas.before.get_group("leading-icons-color")[0],
                color,
            )
        )

    def _set_texture_trailing_icons_color(self, icon_color_focus=False):
        icon = self._trailing_icon

        if self.error:
            color = self._get_error_color()
        elif icon.theme_icon_color == "Primary":
            color = self.theme_cls.onSurfaceVariantColor
        else:
            color = (
                icon.icon_color_focus
                if icon_color_focus
                else icon.icon_color_normal
            )
            if not color:
                color = self.theme_cls.onSurfaceVariantColor

        Clock.schedule_once(
            lambda x: self.set_texture_color(
                icon,
                self.canvas.before.get_group("trailing-icons-color")[0],
                color,
            )
        )

    def _set_enabled_colors(self):
        def schedule_set_texture_color(widget, group_name, color):
            Clock.schedule_once(
                lambda x: self.set_texture_color(widget, group_name, color)
            )

        max_length_label_group = self.canvas.before.get_group(
            "max-length-color"
        )
        helper_text_label_group = self.canvas.before.get_group(
            "helper-text-color"
        )
        hint_text_label_group = self.canvas.after.get_group("hint-text-color")
        leading_icon_group = self.canvas.before.get_group("leading-icons-color")
        trailing_icon_group = self.canvas.before.get_group(
            "trailing-icons-color"
        )

        error_color = self._get_error_color()
        on_surface_variant_color = self.theme_cls.onSurfaceVariantColor

        if self._max_length_label:
            schedule_set_texture_color(
                self._max_length_label,
                max_length_label_group[0],
                (
                    self._max_length_label.color[:-1] + [1]
                    if not self.error
                    else error_color
                ),
            )
        if self._helper_text_label:
            schedule_set_texture_color(
                self._helper_text_label,
                helper_text_label_group[0],
                (
                    on_surface_variant_color
                    if not self._helper_text_label.text_color_focus
                    else (
                        self._helper_text_label.text_color_focus
                        if not self.error
                        else error_color
                    )
                ),
            )
        if self._hint_text_label:
            schedule_set_texture_color(
                self._hint_text_label,
                hint_text_label_group[0],
                (
                    on_surface_variant_color
                    if not self._hint_text_label.text_color_normal
                    else (
                        self._hint_text_label.text_color_normal
                        if not self.error
                        else error_color
                    )
                ),
            )
        if self._leading_icon:
            schedule_set_texture_color(
                self._leading_icon,
                leading_icon_group[0],
                (
                    on_surface_variant_color
                    if self._leading_icon.theme_icon_color == "Primary"
                    or not self._leading_icon.icon_color_normal
                    else self._leading_icon.icon_color_normal
                ),
            )
        if self._trailing_icon:
            schedule_set_texture_color(
                self._trailing_icon,
                trailing_icon_group[0],
                (
                    on_surface_variant_color
                    if self._trailing_icon.theme_icon_color == "Primary"
                    or not self._trailing_icon.icon_color_normal
                    else (
                        self._trailing_icon.icon_color_normal
                        if not self.error
                        else error_color
                    )
                ),
            )

    def _set_disabled_colors(self):
        def schedule_set_texture_color(widget, group, opacity):
            if widget and group:
                color = (
                    widget.icon_color_disabled[:-1]
                    if hasattr(widget, "icon_color_disabled")
                    and widget.icon_color_disabled
                    else self.theme_cls.disabledTextColor[:-1]
                )
                Clock.schedule_once(
                    lambda x: self.set_texture_color(
                        widget, group[0], color + [opacity]
                    )
                )

        groups = {
            "_max_length_label": (
                self.canvas.before.get_group("max-length-color"),
                self.text_field_opacity_value_disabled_max_length_label,
            ),
            "_helper_text_label": (
                self.canvas.before.get_group("helper-text-color"),
                self.text_field_opacity_value_disabled_helper_text_label,
            ),
            "_hint_text_label": (
                self.canvas.after.get_group("hint-text-color"),
                self.text_field_opacity_value_disabled_hint_text_label,
            ),
            "_leading_icon": (
                self.canvas.before.get_group("leading-icons-color"),
                self.text_field_opacity_value_disabled_leading_icon,
            ),
            "_trailing_icon": (
                self.canvas.before.get_group("trailing-icons-color"),
                self.text_field_opacity_value_disabled_trailing_icon,
            ),
        }

        for attr, (group, opacity) in groups.items():
            widget = getattr(self, attr, None)
            schedule_set_texture_color(widget, group, opacity)

    def _get_has_error(self) -> bool:
        if self.validator and self.validator != "phone":
            has_error = {
                "date": self.is_date_valid,
                "email": self.is_email_valid,
                "time": self.is_time_valid,
            }[self.validator](self.text)
            return has_error
        if (
            self._max_length_label
            and self._max_length_label.max_text_length is not None
            and len(self.text) > self._max_length_label.max_text_length
        ):
            has_error = True
        else:
            if all((self.required, len(self.text) == 0)):
                has_error = True
            else:
                has_error = False
        return has_error

    def _get_error_color(self):
        return (
            self.theme_cls.errorColor
            if not self.error_color
            else self.error_color
        )

    def _check_text(self, *args) -> None:
        self.set_text(self, self.text)

    def _refresh_hint_text(self):
        """Method override to avoid duplicate hint text texture."""


# = ============================================================== = #
# =                         ONLY TEXTFIELD                         = #
# = ============================================================== = #
from kivy.graphics import Color, Rectangle
class EntryField(MyTextField):
    hint=StringProperty()
    is_correct=ObjectProperty()
    
    def _get_has_error(self) -> bool:
        has_error = super()._get_has_error()
        if self.is_correct!=None: has_error = (has_error or not self.is_correct())
        return has_error
    
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
    
