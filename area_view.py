import copy

from helpers import safe_element_get
from labels import Labels
from style import Style


class AreaView:
    """
    AreaView provides the container for a given set of sections and the methods to process
    and transform the information they contain into useful data for graphical representation
    """
    pos_y: int
    pos_x: int
    zoom: int
    address_to_pxl: int
    total_height_pxl: int
    start_address: int
    end_address: int

    def __init__(self,
                 sections,
                 area_config,
                 style,
                 **kwargs):
        self.sections = sections
        self.processed_section_views = []
        self.config = kwargs.get('global_config')
        self.area = area_config
        self.style = style
        self.start_address = self.area.get('start', self.sections.lowest_memory)
        self.end_address = self.area.get('end', self.sections.highest_memory)
        self.pos_x = safe_element_get(self.area.get('pos'), 0, default=50)
        self.pos_y = safe_element_get(self.area.get('pos'), 1, default=50)
        self.size_x = safe_element_get(self.area.get('size'), 0, default=200)
        self.size_y = safe_element_get(self.area.get('size'), 1, default=500)
        self.labels = Labels(self.area.get('labels', []), style)

        self.address_to_pxl = (self.end_address - self.start_address) / self.size_y

        if self.config is not None:
            self._process()

    def get_split_area_views(self):
        """
        Get current area view split in multiple area views around break sections
        :return: List of AreaViews
        """
        return self.processed_section_views

    def to_pixels(self, value) -> float:
        """
        Convert a given address to pixels in an absolute manner,
        according to the address / pixel size ratio of current area

        :param value: Address to be converted to pixels
        :return: Conversion result
        """
        return value / self.address_to_pxl

    def to_pixels_relative(self, value) -> float:
        """
        Convert a given address to pixels in a relative manner,
        according to the address / pixel size ratio of current area

        Relative in this context means relative to the start address of the Area view. If Area View
        starts at 0x20000 and ends at 0x30000, passing these values to this function for an area
        with a height of 1000 pixels, will result in 0 and 1000 respectively

        :param value: Address to be converted to pixels
        :return: Conversion result
        """
        return self.size_y - ((value - self.start_address) / self.address_to_pxl)

    def _overwrite_sections_info(self):
        for section in self.sections.get_sections():

            section_style = copy.deepcopy(self.style)
            section.style = section_style

            for element in self.area.get('sections', []):
                sections = element.get('names')
                for item in sections:
                    if item == section.id:
                        # OVERWRITE style, address, size and type if needed
                        section_style.override_properties_from(Style(style=element.get('style')))
                        section.address = element.get('address', section.address)
                        section.type = element.get('type', section.type)
                        section.size = element.get('size', section.size)
                        # As flags can be defined previously at map file, APPEND whatever is new
                        section.flags += element.get('flags', section.flags)

    def _process(self):
        self._overwrite_sections_info()

        if len(self.sections.get_sections()) == 0:
            print("Filtered sections produced no results")
            return

        split_section_groups = self.sections.split_sections_around_breaks()

        breaks_count = len(self.sections.filter_breaks().get_sections())
        area_has_breaks = breaks_count >= 1
        breaks_section_size_y_px = self.style.break_size if self.style is not None else 20

        if area_has_breaks:

            total_breaks_size_y_px = self._get_break_total_size_px()
            total_non_breaks_size_y_px = self._get_non_breaks_total_size_px(
                self.sections.get_sections())
            expandable_size_px = total_breaks_size_y_px - (breaks_section_size_y_px * breaks_count)

            last_area_pos = self.pos_y + self.size_y

            for section_group in split_section_groups:

                if section_group.is_break_section_group():
                    corrected_size = breaks_section_size_y_px
                else:
                    split_section_size_px = self._get_non_breaks_total_size_px(
                        section_group.get_sections())
                    corrected_size = (split_section_size_px / total_non_breaks_size_y_px) * (
                            total_non_breaks_size_y_px + expandable_size_px)

                new_area = copy.deepcopy(self.area)
                new_area['size'] = [200,500]
                if new_area.get('pos') is None:
                    new_area['pos'] = [10,10]
                new_area['size'][1] = corrected_size
                new_area['pos'][1] = last_area_pos - corrected_size
                last_area_pos = new_area['pos'][1]

                self.processed_section_views.append(
                    AreaView(
                        sections=section_group,
                        area_config=new_area,
                        labels=self.labels,
                        style=self.style))

        else:
            if len(self.sections.get_sections()) == 0:
                print("Current view doesn't show any section")
                return
            self.processed_section_views.append(self)

    def _get_break_total_size_px(self):
        total_breaks_size_px = 0

        for _break in self.sections.filter_breaks().get_sections():
            total_breaks_size_px += self.to_pixels(_break.size)

        return total_breaks_size_px

    def _get_non_breaks_total_size_px(self, sections_list):
        total_no_breaks_size_px = 0

        for section in sections_list:
            if not section.is_break():
                total_no_breaks_size_px += self.to_pixels(section.size)
        return total_no_breaks_size_px
