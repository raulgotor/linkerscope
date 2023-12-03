#!/usr/bin/env python3

import argparse
import copy

import yaml
from map_drawer import Map
from style import Style
from map_file_parser import MapFileParser
from sectionsview import SectionsView, Sections

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

    # TODO: drawing of a discontinuity
    # TODO: linked sections compatibility

for element in config['areas']:
    area = element.get('area')

    # TODO: SectionsView should be more of an Area
    sections_view = SectionsView(
        sections=(Sections(sections=MapFileParser(args.input).parse())
                  .filter_address_min(area.get('address', {}).get('min'))
                  .filter_address_max(area.get('address', {}).get('max'))
                  .filter_size_min(area.get('size', {}).get('min'))
                  .filter_size_max(area.get('size', {}).get('max'))
                  ).get_sections(),
        # TODO: area parameter should be named as area configuration
        area=area,
        # TODO: Passing config looks weird since all necessary things should be in area config
        config=config)
    areas.extend(sections_view.get_processed_section_views())

base_style = Style().get_default()
base_style.override_properties_from(Style(style=config.get('style', None)))

Map(diagrams=areas, links=config.get('links', None), style=base_style, file=args.output).draw()

