class Section:
    size: int
    address: int
    name: str
    size_x: int
    size_y: int
    pos_x: int
    pos_y: int
    label_offset = 10

    def __init__(self, size, address, name, type, parent):
        self.type = type
        self.parent = parent
        self.size = size
        self.address = address
        self.name = name
        self.size_y = 0
        self.size_x = 0

    @property
    def addr_label_pos_x(self):
        return self.size_x + self.label_offset

    @property
    def addr_label_pos_y(self):
        return (self.pos_y + self.size_y)

    @property
    def name_label_pos_x(self):
        return self.size_x / 2

    @property
    def size_label_pos(self):
        return self.pos_x + 2, self.pos_y + 2

    @property
    def name_label_pos_y(self):
        return self.pos_y + (self.size_y / 2)



