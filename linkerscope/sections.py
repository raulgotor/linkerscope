from linkerscope.section import Section


class Sections:
    """
    Provide methods and to select and filter sections according to their base address, size, parent,
    type,...
    """
    sections: [Section] = []

    def __init__(self, sections: [Section]):
        self.sections = sections

    def get_sections(self) -> [Section]:
        return self.sections

    @property
    def highest_section(self) -> int:
        return max(self.sections, key=lambda x: x.address)

    @property
    def highest_address(self) -> int:
        return max(self.sections, key=lambda x: x.address).address

    @property
    def highest_memory(self) -> int:
        section = max(self.sections, key=lambda x: x.address + x.size)
        return section.address + section.size

    @property
    def lowest_memory(self) -> int:
        return min(self.sections, key=lambda x: x.address).address

    @property
    def lowest_size(self) -> int:
        return min(self.sections, key=lambda x: x.size).size

    def has_address(self, address: int) -> bool:
        for section in self.sections:
            if section.address <= address <= (section.address + section.size):
                return True
        return False

    def is_break_section_group(self):
        for section in self.get_sections():
            if section.is_break():
                return True
        return False

    def filter_size_min(self, size_bytes: int):
        return Sections(self.sections) if size_bytes is None \
            else Sections(list(filter(lambda item: item.size > size_bytes, self.sections)))

    def filter_size_max(self, size_bytes: int):
        return Sections(self.sections) if size_bytes is None \
            else Sections(list(filter(lambda item: item.size < size_bytes, self.sections)))

    def filter_address_max(self, address_bytes: int):
        return Sections(self.sections) if address_bytes is None \
            else Sections(list(filter(lambda item: (item.address + item.size)
                                                   <= address_bytes, self.sections)))

    def filter_address_min(self, address_bytes: int):
        return Sections(self.sections) if address_bytes is None \
            else Sections(list(filter(lambda item: item.address >= address_bytes, self.sections)))

    def filter_type(self, _type: str):
        return Sections(self.sections) if _type is None \
            else Sections(list(filter(lambda item: item.filter_type == _type, self.sections)))

    def filter_parent(self, parent: str):
        return Sections(self.sections) if parent is None \
            else Sections(list(filter(lambda item: item.filter_parent == parent, self.sections)))

    def filter_breaks(self):
        return Sections(list(filter(lambda item: item.is_break(), self.sections)))

    def split_sections_around_breaks(self) -> []:
        """
        Split a Sections object into different Sections objects having a break section as delimiter

        :return: A list of Section objects
        """
        split_sections = []
        previous_break_end_address = self.lowest_memory

        breaks = self.filter_breaks().get_sections()

        for _break in breaks:

            # Section that covers from previous break till start of this break
            # If it was the first break, will cover from begining of the whole area to this break.
            # Only append if search returns more than 0 counts
            s = Sections(sections=self.sections) \
                .filter_address_max(_break.address) \
                .filter_address_min(previous_break_end_address)
            if len(s.get_sections()) > 0:
                split_sections.append(s)

            # This section covers the break itself
            split_sections.append(Sections(sections=[_break]))
            previous_break_end_address = _break.address + _break.size

        # Section that covers from the last break end address to the end of the whole area. Only
        # append if search returns more than 0 counts
        last_group = Sections(sections=self.sections) \
            .filter_address_max(self.highest_memory) \
            .filter_address_min(previous_break_end_address)

        if len(last_group.sections) > 0:
            split_sections.append(last_group)

        return split_sections
