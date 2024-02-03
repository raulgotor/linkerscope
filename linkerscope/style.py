class Style:
    """
    Holds style for different rendering objects
    """
    # Non SVG
    background: str
    break_type: str
    break_size: int
    growth_arrow_size: float
    growth_arrow_stroke: str
    growth_arrow_fill: str
    stroke_dasharray: str
    hide_size: bool
    hide_name: bool
    hide_address: bool

    # SVG
    fill: str
    stroke: str
    stroke_width: int
    size: int
    font_size: int
    font_type: str
    weight: int
    opacity: int

    text_stroke: str
    text_stroke_width: int
    text_fill: str

    weight: int

    def __init__(self, style=None):
        if style is not None:
            for key, value in style.items():
                setattr(self, key.replace('-', '_'), style.get(key, value))

    def override_properties_from(self, style):
        """
        Modify self by adding additional members available at the provided style

        :param style: Style whose members wants to be added
        :return: New merged styl
        """
        members = [attr for attr in dir(style) if
                   not callable(getattr(style, attr)) and not attr.startswith("__") and getattr(
                       style, attr) is not None]

        for member in members:
            value = getattr(style, member)
            setattr(self, member, value)

        return self

    @staticmethod
    def get_default():
        """
        Get an initialized default Style instance
        :return: A default initialized Style instance
        """

        default_style = Style()
        default_style.break_type = '≈'
        default_style.break_size = 20

        default_style.growth_arrow_size = 1

        default_style.background = 'white'
        default_style.stroke = 'black'
        default_style.stroke_width = 1
        default_style.size = 2

        default_style.font_size = 16
        default_style.font_type = 'Helvetica'

        default_style.weight = 1
        default_style.opacity = 1

        default_style.text_stroke = 'black'
        default_style.text_fill = 'black'
        default_style.text_stroke_width = 0

        default_style.fill = 'lightgrey'
        default_style.growth_arrow_fill = 'white'
        default_style.growth_arrow_stroke = 'black'
        default_style.stroke_dasharray = '3,2'
        default_style.weight = 2
        default_style.hide_size = False
        default_style.hide_name = False
        default_style.hide_address = False

        return default_style
