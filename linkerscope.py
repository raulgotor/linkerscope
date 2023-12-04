#!/usr/bin/env python3

import argparse
import copy

import yaml

from area_view import AreaView
from map_drawer import Map
from style import Style
from map_file_parser import MapFileParser
from sections import Sections

parser = argparse.ArgumentParser()
parser.add_argument('--output',
                    '-o',
                    help='Name for the generated .svg file',
                    default='map.svg')
parser.add_argument('--input',
                    '-i',
                    help='Name of the map file, can be either linker .map files or .yaml descriptor',
                    default='map.yaml')
parser.add_argument('--configuration',
                    '-c',
                    help='Configuration file (.yml). If not specified, will use config.yaml as default',
                    default='config.yaml')

args = parser.parse_args()

areas = []

with open(args.configuration, 'r') as file:
    config = yaml.safe_load(file)

if config['areas'] is None:
    print('No information to show on current configuration file')
    exit(-1)

    # TODO: linked sections compatibility


def safe_element_get(_list: [], index: int) -> int:
    """
    Get an element from a list checking if both the list and the element exist

    :param _list: List to extract the element from
    :param index: Index of the element in the list
    :return: The expected element if exists, None if it doesn't
    """

    return _list[index] if _list is not None and len(_list) > index else None


base_style = Style().get_default()
base_style.override_properties_from(Style(style=config.get('style', None)))

for element in config['areas']:
    area_style = copy.deepcopy(base_style)

    area = element.get('area')
    section_size = area.get('section-size', {})
    area_view = AreaView(
        sections=(Sections(sections=MapFileParser(args.input).parse())
                  .filter_address_min(area.get('range', {})[0])
                  .filter_address_max(area.get('range', {})[1])
                  .filter_size_min(safe_element_get(section_size, 0))
                  .filter_size_max(safe_element_get(section_size, 1))
                  ),
        area_config=area,
        global_config=config,
        style=area_style.override_properties_from(Style(style=area.get('style')))
    )
    areas.extend(area_view.get_processed_section_views())

Map(area_view=areas, links=config.get('links', None), style=base_style, file=args.output).draw()
