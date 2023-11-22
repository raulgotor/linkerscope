import copy
import argparse
import yaml

from map_drawer import Map
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

sec = MapFileParser(args.input).parse()
sec2 = copy.deepcopy(sec)
sec3 = copy.deepcopy(sec)

config = []
with open(args.configuration, 'r') as file:
    config = yaml.safe_load(file)

m = config['main']

z = config.get('zoomed')
zoomed_diagrams = []

if z is not None:
    for diagram in z:
        zoomed_diagrams.append(
            SectionsView(sections=(Sections(sections=sec2)
                                   .address_higher_than(diagram.get('address').get('lowest'))
                                   .address_lower_than(diagram.get('address').get('highest'))
                                   .size_bigger_than(diagram.get('size').get('min'))
                                   .size_smaller_than(diagram.get('size').get('max'))
                                   ).get_sections(),
                         pos_x=diagram.get('map').get('x'),
                         pos_y=diagram.get('map').get('y'),
                         size_x=diagram.get('map').get('size_x'),
                         size_y=diagram.get('map').get('size_y'),
                         start_address=diagram.get('map').get('start'),
                         end_address=diagram.get('map').get('end')))


l = config.get('links')
addresses = []
if l is not None:
    a = l.get('addresses')
    s = l.get('sections')
    if a is not None:
        addresses = a
    if s is not None:
        for element in sec:
            if element.name in s:
                addresses.append(element.address)
                addresses.append(element.address + element.size)

big = (Sections(sections=sec3)
       .address_higher_than(m.get('address').get('lowest'))
       .address_lower_than(m.get('address').get('highest'))
       .size_bigger_than(m.get('size').get('min'))
       .size_smaller_than(m.get('size').get('max'))
       )

a = Map(main_diagram=SectionsView(sections=big.get_sections(),
                                  pos_x=m.get('map').get('x'),
                                  pos_y=m.get('map').get('y'),
                                  size_x=m.get('map').get('size_x'),
                                  size_y=m.get('map').get('size_y'),
                                  start_address=m.get('map').get('start'),
                                  end_address=m.get('map').get('end'),
                                  ),
        magnified_diagram=zoomed_diagrams,
        addresses=addresses,
        force=l.get('force')
        )

a.draw_maps(args.output)

