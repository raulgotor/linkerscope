import copy
from dataclasses import dataclass
from linkerscope.style import Style


@dataclass
class Labels:
    """
    Container for labels, and methods to build them from a yaml label specification
    """
    sections: []
    addresses: []
    style: Style

    def __init__(self, labels, style):
        self.style = style
        self.labels = self.build_labels(labels)

    def build_labels(self, labels_yaml) -> []:
        """
        Build a list of labels (`[Label]`) from a list of labels in a yaml format
        :param labels_yaml: List of labels in a yaml format
        :return: list of labels (`[Label]`)
        """
        labels = []

        for element in labels_yaml:
            style = copy.deepcopy(self.style)
            label = Label(style.override_properties_from(Style(element.get('style'))))

            for key, value in element.items():
                if key != 'style':
                    setattr(label, key.replace('-','_'), value)

            labels.append(label)

        return labels


class Side:
    RIGHT = 'right'
    LEFT = 'left'


@dataclass
class Label:
    """
    Stores single label information for a given address.
    Additionally, provides style information for drawing the link
    """
    def __init__(self, style):
        self.style = style
        self.address = 0
        self.text = 'Label'
        self.length = 20
        self.directions = []
        self.side = Side.RIGHT
