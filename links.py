from style import Style


class Links:
    """
    Stores the link information between given section or address
    Additionally, provides style information for drawing the link
    """
    sections: []
    addresses: []
    style: Style

    def __init__(self, links, style=None):
        self.addresses = links.get('addresses', [])
        self.sections = links.get('sections', [])
        self.style = style
        self.configuration_validator()

    def configuration_validator(self):
        for address in self.addresses:
            if type(address) != int:
                print(f"WARNING: Link address '{address}' is incorrect: can only be of the type integer. It will be ignored")
                self.addresses.remove(address)

        for section_address in self.sections:
            if type(section_address) != str and type(section_address) != list:
                print(
                    f"WARNING: Section link '{section_address}' is incorrect: can only be of the type integer or list. It will be ignored")
                self.sections.remove(section_address)
            elif type(section_address) == list and len(section_address) != 2:
                print(
                    f"WARNING: Section link list '{section_address}' can only have exactly two sections. It will be ignored")
                self.sections.remove(section_address)

            elif type(section_address) == list and (type(section_address[0]) != str or type(section_address[1]) != str):
                print(
                    f"WARNING: Section link list elements'{section_address}' must be strings. They will be ignored")
                self.sections.remove(section_address)