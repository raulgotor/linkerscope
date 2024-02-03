from linkerscope.helpers import safe_element_dict_get
from linkerscope.style import Style
from linkerscope.logger import logger


class Links:
    """
    Stores the link information between given section or address
    Additionally, provides style information for drawing the link
    """
    sections: []
    addresses: []
    style: Style

    def __init__(self, links=None, style=None):
        self.links = links
        self.addresses = safe_element_dict_get(self.links, 'addresses', [])
        self.sections = safe_element_dict_get(self.links, 'sections', [])
        self.style = style
        self.configuration_validator()

    def configuration_validator(self):

        if self.addresses is None:
            logger.warning("'addresses' property is declared but is empty. Field has been ignored")
            self.addresses = []

        if self.sections is None:
            logger.warning("'sections' property is declared but is empty. Field has been ignored")
            self.sections = []

        for address in self.addresses:

            if not isinstance(address, int):
                self.addresses.remove(address)
                logger.warning(f"Link address '{address}' is incorrect: can only be of the type "
                               f"integer. It will be ignored")

        for section_address in self.sections:
            if not isinstance(section_address, str) and not isinstance(section_address, list):
                self.sections.remove(section_address)
                logger.warning(f"Section link '{section_address}' is incorrect: can only be of the "
                               f"type integer or list. It will be ignored")

            elif isinstance(section_address, list) and len(section_address) != 2:
                self.sections.remove(section_address)
                logger.warning(f"Section link list '{section_address}' can only have exactly two "
                               f"sections. It will be ignored")

            elif isinstance(section_address, list) and \
                    (not isinstance(section_address[0], str) or
                     not isinstance(section_address[1], str)):

                self.sections.remove(section_address)
                logger.warning(f"Section link list elements'{section_address}' must be strings. "
                               f"They will be ignored")
