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

    def split_sections_according_to(self, discontinuities):
        splitted_sections = []
        prev_disc_sec_end_addr = self.lowest_memory

        discontinuous_sections = self.get_gap_sections(discontinuities)

        for disc_sec in discontinuous_sections:
            splitted_sections.append(Sections(sections=self.sections)
                                     .filter_address_max(disc_sec.address)
                                     .filter_address_min(prev_disc_sec_end_addr)
                                     )
            splitted_sections.append(Sections(sections=[disc_sec]))
            prev_disc_sec_end_addr = disc_sec.address + disc_sec.size

        splitted_sections.append(Sections(sections=self.sections)
                                 .filter_address_max(self.highest_memory)
                                 .filter_address_min(prev_disc_sec_end_addr)
                                 )

        return splitted_sections

    def get_gap_sections(self, discontinuities):
        discontinuous_sections = []
        for section in self.sections:
            if self.is_gap_section(section, discontinuities):
                discontinuous_sections.append(section)
        return discontinuous_sections

    def is_gap_section(self, section, gaps):
        if section.is_gap:
            return True
        return False


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
            if section.name in self.gaps:
                section.is_gap = True
            else:
                section.is_gap = False

    def process(self):

        self.flag_gaps()

        if len(self.sections) == 0:
            print("Filtered sections produced no results")
            return

        split_section_groups = self.split_sections_according_to(self.gaps)

        gap_sections = self.get_gap_sections(self.gaps)
        gaps_count = len(gap_sections)
        gaps_section_size_y_px = self.config.get('style').get('gaps_size', 20)

        if gaps_count >= 1:

            total_disc_size_px = self.get_gaps_total_size_px(self.gaps)
            total_sec_size_px = self.get_non_gaps_total_size_px(self.gaps)
            expandable_size_px = total_disc_size_px - (gaps_section_size_y_px * gaps_count)

            last_area_pos = self.area['y'] + self.area['size_y']

            for section_group in split_section_groups:
                is_gap_view = False
                split_section_size_px = 0

                for section in section_group.get_sections():
                    if section_group.is_gap_section(section, self.gaps):
                        is_gap_view = True
                        break

                    split_section_size_px += self.to_pixels(section.size)

                if is_gap_view:
                    corrected_size = gaps_section_size_y_px
                else:
                    corrected_size = (split_section_size_px / total_sec_size_px) * (
                                     total_sec_size_px + expandable_size_px)

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

    def get_gaps_total_size_px(self, gaps):
        total_gaps_size_px = 0

        for gap in self.get_gap_sections(gaps):
            total_gaps_size_px += self.to_pixels(gap.size)

        return total_gaps_size_px

    def get_non_gaps_total_size_px(self, gaps):
        total_no_gaps_size_px = 0
        for split_section_groups in self.split_sections_according_to(gaps):
            is_gap = False
#            if self.is_gap_section_group(split_section_groups):
 #               continue
            for section in split_section_groups.sections:
                if self.is_gap_section(section, gaps):
                    is_gap = True
                    break
                total_no_gaps_size_px += self.to_pixels(section.size)
            if is_gap:
                continue
        return total_no_gaps_size_px
