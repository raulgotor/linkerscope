import copy

from style import Style


class Labels:
    sections: []
    addresses: []
    style: Style

    def __init__(self, labels, style):
        self.style = style
        self.labels = self.build_labels(labels)

    def build_labels(self, labels_yaml):
        labels = []

        for element in labels_yaml:
            style = copy.deepcopy(self.style)
            label = Label(style.override_properties_from(Style(element.get('style'))))

            for key, value in element.items():
                if key != 'style':
                    setattr(label, key.replace('-','_'), value)

            labels.append(label)

        return labels


class Label:

    def __init__(self, style):
        self.style = style
        self.address = 0
        self.text = 'Label'
        self.length = 20
        self.directions = []
