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
    background_color: int
    discontinuities_size: str
    break_type: str
    break_size: int
    grow_arrow_weight: float

    def __init__(self, style=None):
        if style is not None:
            for key, value in style.items():
                setattr(self, key.replace('-','_'), style.get(key, value))

    def override_properties_from(self, style):
        '''
        Modify self by adding additional members available at the provided style

        :param style: Style whose members wants to be added
        :return: New merged styl
        '''
        members = [attr for attr in dir(style) if
                   not callable(getattr(style, attr)) and not attr.startswith("__") and getattr(
                       style, attr) is not None]

        for member in members:
            value = getattr(style, member)
            setattr(self, member, value)

        return self

    @staticmethod
    def get_default():
        default_style = Style()
        default_style.section_fill_color = '#CCE5FF'
        default_style.section_stroke_color = '#3399FF'
        default_style.section_stroke_width = 2
        default_style.label_color = 'blue'
        default_style.label_size = '16'
        default_style.label_stroke_width = 1
        default_style.link_stroke_width = 1
        default_style.link_stroke_color = 'grey'
        default_style.map_background_color = '#CCCCFF'
        default_style.background_color = 'white'
        default_style.discontinuities_size = 20
        default_style.break_type = '≈'
        default_style.break_size = 20
        default_style.grow_arrow_weight = 1
        return default_style
