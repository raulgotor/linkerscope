#!/usr/bin/env python3

import argparse
import copy
import sys

import yaml

from area_view import AreaView
from helpers import safe_element_get
from links import Links
from map_drawer import Map
from style import Style
from map_file_loader import MapFileLoader
from sections import Sections

parser = argparse.ArgumentParser()
parser.add_argument('--output',
                    '-o',
                    help='Name for the generated .svg file',
                    default='map.svg')
parser.add_argument('--input',
                    '-i',
                    help='Name of the map file,'
                         'can be either linker .map files or .yaml descriptor',
                    default='map.yaml')
parser.add_argument('--config',
                    '-c',
                    help='Configuration file (.yml). If not specified,'
                         'will use config.yaml as default',
                    default='config.yaml')

args = parser.parse_args()

areas = []

with open(args.config, 'r', encoding='utf-8') as file:
    config = yaml.safe_load(file)

if config['areas'] is None:
    print('No information to show on current configuration file')
    sys.exit(-1)

base_style = Style().get_default()
base_style.override_properties_from(Style(style=config.get('style', None)))

for element in config['areas']:
    area_style = copy.deepcopy(base_style)

    area = element.get('area')
    section_size = area.get('section-size', {})
    _range = area.get('range', {})
    area_view = AreaView(
        sections=(Sections(sections=MapFileLoader(args.input).parse())
                  .filter_address_min(safe_element_get(_range, 0))
                  .filter_address_max(safe_element_get(_range, 1))
                  .filter_size_min(safe_element_get(section_size, 0))
                  .filter_size_max(safe_element_get(section_size, 1))
                  ),
        area_config=area,
        global_config=config,
        style=area_style.override_properties_from(Style(style=area.get('style')))
    )
    areas.extend(area_view.get_split_area_views())
yaml_links = config.get('links', None)

links_style = copy.deepcopy(base_style)
links = Links(config.get('links', {}),
              style=links_style.override_properties_from(
                  Style(style=yaml_links.get('style') if yaml_links is not None else None)))
Map(area_view=areas,
    links=links,
    style=base_style,
    file=args.output,
    size=config.get('size', (500, 500))
    ).draw()
