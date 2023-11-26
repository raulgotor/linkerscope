#!/usr/bin/env python3

import copy
import argparse
import yaml

from map_drawer import Map
from style import Style

from map_file_parser import MapFileParser
from sectionsview import SectionsView, Sections

#todo cleanme

default_style = Style()
default_style.section_fill_color = '#CCE5FF'
default_style.section_stroke_color = '#3399FF'
default_style.section_stroke_width = 2
default_style.label_color = 'blue'
default_style.label_size = '16px'
default_style.label_stroke_width = 1
default_style.link_stroke_width = 1
default_style.link_stroke_color = 'grey'
default_style.map_background_color = '#CCCCFF'

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

sec = MapFileParser(args.input).parse()
sec2 = copy.deepcopy(sec)
sec3 = copy.deepcopy(sec)

config = []
with open(args.configuration, 'r') as file:
    config = yaml.safe_load(file)

_areas = config['areas']
areas = []
if _areas is not None:
    for element in _areas:
        area = element.get('area')
        filtered_sections = (Sections(sections=sec2).filter_address_min(area.get('address', {}).get('lowest')))

        filtered_sections = (Sections(sections=sec2)
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

#todo cleanme
for key, value in config.get('style').items():
    setattr(default_style, key, value)

a = Map(diagrams=areas,
        links=config.get('links'),
        style=default_style
        )

a.draw(args.output)

