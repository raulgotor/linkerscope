import copy


class Style:
    section_fill_color: str
    section_stroke_color: str
    section_stroke_width: int
    link_stroke_width: int
    link_stroke_color: str
    label_font: str
    label_color: int
    label_size: int
    label_stroke_width: int
    map_background_color: int

    def __init__(self, style=None):
        if style is not None:
            for key, value in style.items():
                setattr(self, key, style.get(key, value))

    def extend_style(self, style):
        '''
        Create a copy of a provided current style with additional members available at the provided style

        :param style: Style whose members wants to be added
        :return: New merged styl
        '''
        members = [attr for attr in dir(style) if
                   not callable(getattr(style, attr)) and not attr.startswith("__") and getattr(
                       style, attr) is not None]

        new_style = copy.deepcopy(self)
        for member in members:
            value = getattr(style, member)
            print(value)
            setattr(new_style, member, value)
        return new_style