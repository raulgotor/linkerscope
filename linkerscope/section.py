from linkerscope.style import Style


class Section:
    """
    Holds logical and graphical information for a given section, as well as other properties such as
    style, visibility, type, etc...
    """
    size: int
    address: int
    id: str
    size_x: int
    size_y: int
    pos_x: int
    pos_y: int
    label_offset: int = 10
    style: Style

    def __init__(self, size, address, id, _type, parent, flags=[], name=None):
        self.type = _type
        self.parent = parent
        self.size = size
        self.address = address
        self.id = id
        self.name = name
        self.size_y = 0
        self.size_x = 0
        self.style = Style()
        self.flags = flags

    def is_grow_up(self):
        return 'grows-up' in self.flags

    def is_grow_down(self):
        return 'grows-down' in self.flags

    def is_break(self):
        return 'break' in self.flags

    def is_address_hidden(self):
        return self.style.hide_address

    def is_name_hidden(self):
        return self.style.hide_name

    def is_size_hidden(self):
        return self.style.hide_size

    @property
    def addr_label_pos_x(self):
        return self.size_x + self.label_offset

    @property
    def addr_label_pos_y(self):
        return self.pos_y + self.size_y

    @property
    def name_label_pos_x(self):
        return self.size_x / 2

    @property
    def size_label_pos(self):
        return self.pos_x + 2, self.pos_y + 2

    @property
    def name_label_pos_y(self):
        return self.pos_y + (self.size_y / 2)
