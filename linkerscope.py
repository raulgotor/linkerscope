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

sections = MapFileParser(args.input).parse()

config = []
areas = []

with open(args.configuration, 'r') as file:
    config = yaml.safe_load(file)

if config['areas'] is None:
    print('No information to show on current configuration file')
    exit(-1)

for element in config['areas']:
    last_discontinuity = None

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



    #dis = tamano total pixels discontinuitys - nuevos tamanos
    #total = suma de splited sections en pixels

    #splitsectpixels / total * dis es el nuevo size.
    #nueva posicion es la misma
    #|=====|==|===|

    splitted_secs = filtered_sections.split_sections_in_groups(config['discontinuities'])
    for i, group in enumerate(splitted_secs):
        #print('Section group', i)
        for section in group.sections:
            pass
            #print(section.name)


    disc_sec = filtered_sections.get_discontinuities_sections(config['discontinuities'])
    disc_count = len(disc_sec)
    discontinuity_size_pixels = 40
    if disc_count >= 1:

        sections_view = SectionsView(
            sections=filtered_sections.get_sections(),
            area=area)

        total_disc_size_px = sections_view.get_discontinuities_size_total_px(config['discontinuities'])
        total_sec_size_px = sections_view.get_non_discontinuities_size_total_px(config['discontinuities'])
        expandable_size_px = total_disc_size_px - (discontinuity_size_pixels * disc_count)

        print(total_disc_size_px)
        print(total_sec_size_px)
        print(expandable_size_px)

        x = 0
        last_area_pos = area['y'] + area['size_y']

        for sec in splitted_secs:
            is_discontinuous_view = False
            split_section_size_px = 0

            for s in sec.get_sections():
                if sec.is_discontinuous_section(s, config['discontinuities']):
                    is_discontinuous_view = True
                    break

                split_section_size_px += sections_view.to_pixels(s.size)

            if is_discontinuous_view:
                corrected_size = discontinuity_size_pixels
            else:
                corrected_size = (split_section_size_px / total_sec_size_px) * (total_sec_size_px + expandable_size_px)
                print(corrected_size)

            new_area = copy.deepcopy(area)
            new_area['size_y'] = corrected_size
            new_area['y'] = last_area_pos - corrected_size
            last_area_pos = new_area['y']

            v = SectionsView(
                sections=sec.get_sections(),
                area=new_area)
            areas.append(v)

    else:
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
        style=base_style,
        file=args.output
        )

a.draw()

