import os
import sys
import yaml
from logger import logger
from section import Section
from gnu_linker_map_parser import GNULinkerMapParser


class MapFileLoader:
    """
    Takes input file provided by user and loads it in memory for further processing.
    Depending on the type of file (.map or .yaml) will include an additional conversion step and
    create a temporary .yaml file
    """
    def __init__(self, file):
        self.input_filename = file

    def parse(self):
        _, file_extension = os.path.splitext(self.input_filename)

        if file_extension == '.map':
            self.parse_map(self.input_filename)
            return self.parse_yaml('examples/map.yaml')

        if file_extension in ['.yaml', '.yml']:
            return self.parse_yaml(self.input_filename)

        logger.error(f"Wrong map file extension: '{file_extension}'. Use .map or .yaml files")
        sys.exit(-1)

    @staticmethod
    def parse_yaml(filename):
        sections = []

        with open(filename, 'r', encoding='utf-8') as file:
            y = yaml.safe_load(file)

        for element in y['map']:
            sections.append(Section(address=element['address'],
                                    size=element['size'],
                                    id=element['id'],
                                    name=element.get('name'),
                                    parent=element.get('parent', 'none'),
                                    _type=element.get('type', 'area'),
                                    flags=element.get('flags', '')
                                    )
                            )

        return sections

    @staticmethod
    def parse_map(input_filename):
        GNULinkerMapParser(input_filename=input_filename, output_filename='examples/map.yaml').parse()
