class Style:
    box_fill_color: str
    box_stroke_color: str
    box_stroke_width: int
    link_stroke_width: int
    link_stroke_color: str
    label_font: str
    label_color: int
    label_size: int
    label_stroke_width: int
    area_fill_color: int

    def __init__(self, style=None):
        if style is not None:
            for key, value in style.items():
                setattr(self, key, style.get(key, value))
