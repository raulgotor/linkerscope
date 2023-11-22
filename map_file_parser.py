import yaml

from area import Section
from map_parser import MapParser


class MapFileParser:
    def __init__(self, file):
        self.input_filename = file
        self.parse()

    def parse(self):
        if 1:
            return self.parse_yaml(self.input_filename)

    @staticmethod
    def parse_yaml(filename):
        sections = []

        address_max = 0x60000
        with open(filename, 'r') as file:
            y = yaml.safe_load(file)

        for element in y['map']:
            sections.append(Section(address=element['address'],
                                    size=element['size'],
                                    name=element['name'],
                                    parent=element.get('parent') if element.get('parent') is not None else 'none',
                                    type=element.get('type') if element.get('type') is not None else 'area',
                                    ))

        return sections

    @staticmethod
    def parse_map(input_filename):
        a = MapParser(input_filename=input, output_filename='temp.yaml')

