import copy

from helpers import safe_element_list_get, safe_element_dict_get, DefaultAppValues
from labels import Labels
from logger import logger
from style import Style


class AreaView:
    """
    AreaView provides the container for a given set of sections and the methods to process
    and transform the information they contain into useful data for graphical representation
    """
    pos_y: int
    pos_x: int
    zoom: int
    address_to_pxl: float
    total_height_pxl: int
    start_address: int
    end_address: int

    def __init__(self,
                 sections,
                 style,
                 area_config=[],
                 labels=None,
                 is_subarea = False):
        self.sections = sections
        self.processed_section_views = []
        self.is_subarea = is_subarea
        self.area = area_config
        self.style = style
        self.start_address = safe_element_dict_get(self.area, 'start', self.sections.lowest_memory)
        self.end_address = safe_element_dict_get(self.area, 'end', self.sections.highest_memory)
        self.pos_x = safe_element_list_get(
            safe_element_dict_get(self.area, 'pos'), 0, default=DefaultAppValues.POSITION_X)

        self.pos_y = safe_element_list_get(
            safe_element_dict_get(self.area, 'pos'), 1, default=DefaultAppValues.POSITION_Y)

        self.size_x = safe_element_list_get(
            safe_element_dict_get(self.area, 'size'), 0, default=DefaultAppValues.SIZE_X)

        self.size_y = safe_element_list_get(
            safe_element_dict_get(self.area, 'size'), 1, default=DefaultAppValues.SIZE_Y)

        self.labels = Labels(safe_element_dict_get(self.area, 'labels', []), style)
        self.title = safe_element_dict_get(self.area, 'title', DefaultAppValues.TITLE)
        self.address_to_pxl = (self.end_address - self.start_address) / self.size_y

        if not self.is_subarea:
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
        """
        Override default style with section specific style

        Overrides default style (normally style defined by the area it is at) and flags information
        on a section given a new definition is provided for an specific section at the map or
        configuration files
        """

        for section in self.sections.get_sections():

            section_style = copy.deepcopy(self.style)
            section.style = section_style

            inner_sections = safe_element_dict_get(self.area, 'sections', [])

            if inner_sections is None:
                logger.warning(
                    "'sections' property is declared but is empty. Field has been ignored")
                inner_sections = []

            for element in inner_sections:

                section_names = safe_element_dict_get(element, 'names', [])

                if section_names is None:
                    logger.warning(
                        "'sections' property is declared but is empty. Field has been ignored")
                    section_names = []

                for item in section_names:
                    if item == section.id:
                        # OVERWRITE style, address, size and type if needed
                        section_style.override_properties_from(Style(style=element.get('style')))
                        section.address = element.get('address', section.address)
                        section.type = element.get('type', section.type)
                        section.size = element.get('size', section.size)
                        # As flags can be defined previously at map file, APPEND whatever is new
                        section.flags += element.get('flags', section.flags)

    def _process(self):
        def recalculate_subarea_size_y(start_mem_addr, end_mem_addr):
            """
            Recalculates the size of the current sub-area, provided the maximum and minimum
            memory that this area has to show

            For that, it makes a relation between the memory that needs to be displayed and
            the total non-break memory available

            :param start_mem_addr: minimum memory address that the new sub-area must show
            :param end_mem_addr: maximum memory address that the new sub-area must show
            :return: Recalculated size for this area
            """

            return (self.to_pixels(end_mem_addr - start_mem_addr) / total_non_breaks_size_y_px) * \
                   (total_non_breaks_size_y_px + expandable_size_px)

        def area_config_clone(configuration, pos_y_px, size_y_px, start_mem_addr, end_mem_addr):
            """
            Clones an area configuration and changes position and size

            :param configuration: Area configuration to clone
            :param pos_y_px: Position in pixels for the new cloned configuration
            :param size_y_px: Size y in pixels of the new cloned configuration
            :param start_mem_addr: minimum memory address that the new sub-area must show
            :param end_mem_addr: maximum memory address that the new sub-area must show
            :return: A new area configuration with the provided configuration and provided parameters
            """
            new_configuration = copy.deepcopy(configuration)
            new_configuration['size'] = [DefaultAppValues.SIZE_X, DefaultAppValues.SIZE_Y]
            if new_configuration.get('pos') is None:
                new_configuration['pos'] = [DefaultAppValues.POSITION_X, DefaultAppValues.POSITION_Y]
            new_configuration['size'][1] = size_y_px
            new_configuration['pos'][1] = pos_y_px - size_y_px
            new_configuration['start'] = start_mem_addr
            new_configuration['end'] = end_mem_addr
            return new_configuration

        self._overwrite_sections_info()

        if len(self.sections.get_sections()) == 0:
            print("Filtered sections produced no results")
            return

        split_section_groups = self.sections.split_sections_around_breaks()

        breaks_count = len(self.sections.filter_breaks().get_sections())
        area_has_breaks = breaks_count >= 1
        breaks_section_size_y_px = self.style.break_size if self.style is not None else 20

        if not area_has_breaks:
            if len(self.sections.get_sections()) == 0:
                logger.error(f"An area view without sections made its through the process. "
                             f"This shouldn't be happening")
                exit(-1)
            self.processed_section_views.append(self)
            return

        total_breaks_size_y_px = self._get_break_total_size_before_transform_px()
        total_non_breaks_size_y_px = self._get_non_breaks_total_size_px(total_breaks_size_y_px)

        # Size gained at the area after flagged sections transformed to breaks
        expandable_size_px = total_breaks_size_y_px - (breaks_section_size_y_px * breaks_count)

        last_area_pos = self.pos_y + self.size_y

        for i, section_group in enumerate(split_section_groups):

            # TODO: ideally, instead of doing this, we should have previously obtained an array
            #       of sub-areas with already start and end values set. That method should live
            #       at area class and not at sections. That is, kill the
            #       `split_sections_around_breaks` method
            if section_group is split_section_groups[0]:
                start_addr = self.start_address
                end_addr = split_section_groups[1].lowest_memory
            elif section_group is split_section_groups[-1]:
                end_addr = self.end_address if self.end_address > section_group.highest_memory else section_group.highest_memory
                start_addr = split_section_groups[-2].highest_memory
            elif section_group.is_break_section_group():
                start_addr = section_group.lowest_memory
                end_addr = section_group.highest_memory
            else:
                start_addr = split_section_groups[i - 1].highest_memory
                end_addr = split_section_groups[i + 1].lowest_memory

            # Assign new calculated size y
            corrected_size_y_px = breaks_section_size_y_px \
                if section_group.is_break_section_group() \
                else recalculate_subarea_size_y(start_addr, end_addr)

            subconfig = area_config_clone(self.area,
                                          last_area_pos,
                                          corrected_size_y_px,
                                          start_addr,
                                          end_addr)

            last_area_pos = subconfig['pos'][1]

            self.processed_section_views.append(AreaView(
                sections=section_group,
                area_config=subconfig,
                labels=self.labels,
                style=self.style,
                is_subarea=True)
            )

    def _get_break_total_size_before_transform_px(self):
        """
        Compute the sum of pixels that the break sections would occupy if they wouldn't be break
        sections
        :return: Computed size in pixels
        """
        total_breaks_size_px = 0

        for _break in self.sections.filter_breaks().get_sections():
            total_breaks_size_px += self.to_pixels(_break.size)

        return total_breaks_size_px

    def _get_non_breaks_total_size_px(self, breaks_size_y_sum_px):
        """
        Get pixel count at y of displayed memory that is not break-flagged section before
        transformation into a break section.

        That takes into account both normal sections and empty memory

        :param breaks_size_y_sum_px: Total pixel count at y axis occupied by break-flagged sections before transformation into break sections.
        :return:
        """

        highest_mem = self.end_address if self.end_address > self.sections.highest_memory else self.sections.highest_memory
        lowest_mem = self.start_address if self.start_address < self.sections.lowest_memory else self.sections.lowest_memory
        return self.to_pixels(highest_mem - lowest_mem) - breaks_size_y_sum_px
