from style import Style


class Links:
    sections: []
    addresses: []
    style: Style

    def __init__(self, links={}, style=None):
        self.addresses = links.get('addresses', [])
        self.sections = links.get('sections', [])
        self.style = style
