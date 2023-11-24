import yaml

from area import Section
from map_parser import MapParser
import os

class MapFileParser:
    def __init__(self, file):
        self.input_filename = file

    def parse(self):
        filename, file_extension = os.path.splitext(self.input_filename)

        if file_extension == '.map':
            self.parse_map(self.input_filename)
            return self.parse_yaml('examples/map.yaml')
        elif file_extension in ['.yaml', '.yml']:
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
        MapParser(input_filename=input_filename, output_filename='examples/map.yaml').parse()

