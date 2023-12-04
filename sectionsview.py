import copy

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

    def split_sections_around_breaks(self) -> []:
        """
        Split a Sections object into different Sections objects having a break section as delimiter

        :return: A list of Section objects
        """
        split_sections = []
        previous_break_end_address = self.lowest_memory

        breaks = self.get_break_sections()

        for _break in breaks:

            # Section that covers from previous break till start of this break
            # If it was the first break, will cover from begining of the whole area to this break. Only append if search
            # returns more than 0 counts
            s = Sections(sections=self.sections)\
                .filter_address_max(_break.address)\
                .filter_address_min(previous_break_end_address)
            if len(s.sections) > 0:
                split_sections.append(s)

            # This section covers the break itself
            split_sections.append(Sections(sections=[_break]))
            previous_break_end_address = _break.address + _break.size

        # Section that covers from the last break end address to the end of the whole area. Only append if search returns
        # more than 0 counts
        last_group = Sections(sections=self.sections)\
            .filter_address_max(self.highest_memory)\
            .filter_address_min(previous_break_end_address)

        if len(last_group.sections) > 0:
            split_sections.append(last_group)

        return split_sections

    def get_break_sections(self):
        break_sections = []
        for section in self.sections:
            if section.is_break():
                break_sections.append(section)
        return break_sections

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
        self.processed_section_views = []
        self.config = kwargs.get('config')
        self.area = area
        self.style = Style(style=self.area.get('style'))
        self.start_address = self.area.get('start', self.lowest_memory)
        self.end_address = self.area.get('end', self.highest_memory)
        self.pos_x = self.area.get('x', 10)
        self.pos_y = self.area.get('y', 10)
        self.size_x = self.area.get('size_x', 200)
        self.size_y = self.area.get('size_y', 500)
        self.address_to_pxl = (self.end_address - self.start_address) / self.size_y
        if self.config is not None:
            self.process()

    def get_processed_section_views(self):
        return self.processed_section_views

    def _overwrite_sections_info(self):
        for section in self.sections:
            for element in self.config.get('map', None):
                if element['name'] == section.name:
                    section.address = element.get('address', section.address)
                    section.type = element.get('type', section.type)
                    section.size = element.get('size', section.size)
                    section.flags = element.get('flags', section.flags)

    def process(self):
        self._overwrite_sections_info()

        if len(self.sections) == 0:
            print("Filtered sections produced no results")
            return

        split_section_groups = self.split_sections_around_breaks()

        breaks_count = len(self.get_break_sections())
        area_has_breaks = breaks_count >= 1
        breaks_section_size_y_px = self.config.get('style').get('break_size', 20)

        if area_has_breaks:

            total_breaks_size_y_px = self.get_break_total_size_px()
            total_non_breaks_size_y_px = self.get_non_breaks_total_size_px(self.sections)
            expandable_size_px = total_breaks_size_y_px - (breaks_section_size_y_px * breaks_count)

            last_area_pos = self.pos_y + self.size_y

            for section_group in split_section_groups:

                if self.is_break_section_group(section_group):
                    corrected_size = breaks_section_size_y_px
                else:
                    split_section_size_px = self.get_non_breaks_total_size_px(section_group.get_sections())
                    corrected_size = (split_section_size_px / total_non_breaks_size_y_px) * (
                            total_non_breaks_size_y_px + expandable_size_px)

                new_area = copy.deepcopy(self.area)
                new_area['size_y'] = corrected_size
                new_area['y'] = last_area_pos - corrected_size
                last_area_pos = new_area['y']

                self.processed_section_views.append(
                    SectionsView(
                        sections=section_group.get_sections(),
                        area=new_area))

        else:
            if len(self.sections) == 0:
                print("Current view doesn't show any section")
                return
            self.processed_section_views.append(self)

    def to_pixels(self, value):
        return value / self.address_to_pxl

    def to_pixels_relative(self, value):
        a = self.size_y - ((value - self.start_address) / self.address_to_pxl)
        return a

    def get_break_total_size_px(self):
        total_breaks_size_px = 0

        for _break in self.get_break_sections():
            total_breaks_size_px += self.to_pixels(_break.size)

        return total_breaks_size_px

    @staticmethod
    def is_break_section_group(section_group):
        for section in section_group.get_sections():
            if section.is_break():
                return True
        return False

    def get_non_breaks_total_size_px(self, sections_list):
        total_no_breaks_size_px = 0

        for section in sections_list:
            if not section.is_break():
                total_no_breaks_size_px += self.to_pixels(section.size)
        return total_no_breaks_size_px

