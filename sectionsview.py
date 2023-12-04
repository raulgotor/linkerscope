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

    def split_sections_around_gaps(self) -> []:
        """
        Split a Sections object into different Sections objects having a gap section as delimiter

        :return: A list of Section objects
        """
        split_sections = []
        previous_gap_end_address = self.lowest_memory

        gaps = self.get_gap_sections()

        for gap in gaps:

            # Section that covers from previous gap till start of this gap
            # If it was the first gap, will cover from begining of the whole area to this gap. Only append if search
            # returns more than 0 counts
            s = Sections(sections=self.sections)\
                .filter_address_max(gap.address)\
                .filter_address_min(previous_gap_end_address)
            if len(s.sections) > 0:
                split_sections.append(s)

            # This section covers the gap itself
            split_sections.append(Sections(sections=[gap]))
            previous_gap_end_address = gap.address + gap.size

        # Section that covers from the last gap end address to the end of the whole area. Only append if search returns
        # more than 0 counts
        last_group = Sections(sections=self.sections)\
            .filter_address_max(self.highest_memory)\
            .filter_address_min(previous_gap_end_address)

        if len(last_group.sections) > 0:
            split_sections.append(last_group)

        return split_sections

    def get_gap_sections(self):
        gap_sections = []
        for section in self.sections:
            if section.is_gap():
                gap_sections.append(section)
        return gap_sections

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
        self.gaps = self.config['gaps'] if self.config is not None else None
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

    def flag_gaps(self):
        for section in self.sections:
            section.is_gap = True if section.type in self.gaps else False

    def process(self):

        #self.flag_gaps()

        if len(self.sections) == 0:
            print("Filtered sections produced no results")
            return

        split_section_groups = self.split_sections_around_gaps()

        gaps_count = len(self.get_gap_sections())
        area_has_gaps = gaps_count >= 1
        gaps_section_size_y_px = self.config.get('style').get('gaps_size', 20)

        if area_has_gaps:

            total_gaps_size_y_px = self.get_gaps_total_size_px()
            total_non_gaps_size_y_px = self.get_non_gaps_total_size_px(self.sections)
            expandable_size_px = total_gaps_size_y_px - (gaps_section_size_y_px * gaps_count)

            last_area_pos = self.pos_y + self.size_y

            for section_group in split_section_groups:

                if self.is_gap_section_group(section_group):
                    corrected_size = gaps_section_size_y_px
                else:
                    split_section_size_px = self.get_non_gaps_total_size_px(section_group.get_sections())
                    corrected_size = (split_section_size_px / total_non_gaps_size_y_px) * (
                            total_non_gaps_size_y_px + expandable_size_px)

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

    def get_gaps_total_size_px(self):
        total_gaps_size_px = 0

        for gap in self.get_gap_sections():
            total_gaps_size_px += self.to_pixels(gap.size)

        return total_gaps_size_px

    @staticmethod
    def is_gap_section_group(section_group):
        for section in section_group.get_sections():
            if section.is_gap():
                return True
        return False

    def get_non_gaps_total_size_px(self, sections_list):
        total_no_gaps_size_px = 0

        for section in sections_list:
            if not section.is_gap():
                total_no_gaps_size_px += self.to_pixels(section.size)
        return total_no_gaps_size_px

