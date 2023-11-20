import copy

import svgwrite
from svgwrite import Drawing
import yaml

from map_drawer import Map
from map_parser import MapParser
from area import Section
from sectionsview import SectionsView, Sections




#a = MapParser()

def parse_yaml(file_name='map.yaml'):
    sections=[]

    address_max = 0x60000
    with open("map2.yaml", 'r') as file:
        y = yaml.safe_load(file)

    for element in y['map']:
        sections.append(Section(address=element['address'],
                            size=element['size'],
                            name=element['name'],
                            parent=element.get('parent') if element.get('parent') is not None else 'none',
                            type=element.get('type') if element.get('type') is not None else 'area',
                            ))

    return sections

sec = parse_yaml()
sec2 = copy.deepcopy(sec)
sec3 = copy.deepcopy(sec)

config = []
with open('config.yaml', 'r') as file:
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

a.draw_maps()

