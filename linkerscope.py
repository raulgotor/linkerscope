#!/usr/bin/env python3

import argparse
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

sections = MapFileParser(args.input).parse()

config = []
areas = []

with open(args.configuration, 'r') as file:
    config = yaml.safe_load(file)

if config['areas'] is None:
    print('No information to show on current configuration file')
    exit(-1)

for element in config['areas']:
    area = element.get('area')

    filtered_sections = (Sections(sections=sections)
     .filter_address_min(area.get('address', {}).get('min'))
     .filter_address_max(area.get('address', {}).get('max'))
     .filter_size_min(area.get('size', {}).get('min'))
     .filter_size_max(area.get('size', {}).get('max'))
     )

    if len(filtered_sections.sections) == 0:
        print("Filtered sections produced no results")
        continue

    sections_view = SectionsView(
        sections=filtered_sections.get_sections(),
         area=area)

    if len(sections_view.sections) == 0:
        print("Current view doesn't show any section")
        continue
    areas.append(sections_view)

base_style = Style().get_default()
base_style.override_properties_from(Style(style=config.get('style')))

a = Map(diagrams=areas,
        links=config.get('links'),
        style=base_style
        )

a.draw(args.output)

