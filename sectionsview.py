import yaml
from area import Section
from style import Style


class Sections:
    sections: [Section] = []

    def __init__(self, sections):
        self.sections = sections

    def get_sections(self):
        return self.sections

    @property
    def highest_section(self):
        return max(self.sections, key=lambda x: x.address)

    @property
    def highest_address(self):
        return max(self.sections, key=lambda x: x.address).address

    @property
    def highest_memory(self):
        section = max(self.sections, key=lambda x: x.address + x.size)
        return section.address + section.size

    @property
    def lowest_memory(self):
        return min(self.sections, key=lambda x: x.address).address

    @property
    def lowest_size(self):
        return min(self.sections, key=lambda x: x.size).size

    def has_address(self, address):
        for section in self.sections:
            if section.address <= address <= (section.address + section.size):
                return True
        return False

    def filter_size_min(self, size_bytes):
        return Sections(self.sections) if size_bytes is None \
            else Sections(list(filter(lambda item: item.size > size_bytes, self.sections)))

    def filter_size_max(self, size_bytes):
        return Sections(self.sections) if size_bytes is None \
            else Sections(list(filter(lambda item: item.size < size_bytes, self.sections)))

    def filter_address_max(self, address_bytes):
        return Sections(self.sections) if address_bytes is None \
            else Sections(list(filter(lambda item: (item.address + item.size) <= address_bytes, self.sections)))

    def filter_address_min(self, address_bytes):
        return Sections(self.sections) if address_bytes is None \
            else Sections(list(filter(lambda item: item.address >= address_bytes, self.sections)))

    def type(self, type):
        return Sections(self.sections) if type is None \
            else Sections(list(filter(lambda item: item.type == type, self.sections)))

    def parent(self, parent):
        return Sections(self.sections) if parent is None \
            else Sections(list(filter(lambda item: item.parent == parent, self.sections)))


class SectionsView(Sections):
    pos_y: int
    pos_x: int
    zoom: int
    address_to_pxl: int
    total_height_pxl: int
    start_address: int
    end_address: int

    def __init__(self,
                 sections,
                 area,
                 **kwargs):
        super().__init__(sections)

        self.area = area
        self.style = Style(style=self.area.get('style'))
        self.start_address = self.area.get('start', self.lowest_memory)
        self.end_address = self.area.get('end', self.highest_memory)
        self.pos_x = self.area.get('x', 10)
        self.pos_y = self.area.get('y', 10)
        self.size_x = self.area.get('size_x', 200)
        self.size_y = self.area.get('size_y', 500)

        self.address_to_pxl = (self.end_address - self.start_address) / self.size_y

    def to_pixels(self, value):
        return value / self.address_to_pxl

    def to_pixels_relative(self, value):
        a = self.size_y - ((value - self.start_address) / self.address_to_pxl)
        return a
