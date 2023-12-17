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
