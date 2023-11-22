import re

from area import Section
import yaml

class MapParser:
    def __init__(self, input_filename, output_filename):
        self.areas = []
        self.sections = []
        self.input_filename = input_filename
        self.output_filename = output_filename

    def parse(self):
        with open(self.input_filename, 'r') as file:

            found_memory_map_section = False
            file_iterator = iter(file)
            prev_line = next(file_iterator)
            for line in file_iterator:
                if 0:#not found_memory_map_section:
                    if 'Linker script and memory map' in line:
                        found_memory_map_section = True
                    else:
                        continue

                process_areas(self, prev_line)
                multiple_line = prev_line + line
                process_sections(self, multiple_line)
                prev_line = line

        my_dict = {'map': []}
        for area in self.areas:
            my_dict['map'].append({
                'type': 'area',
                'address': area.address,
                'size': area.size,
                'name': area.name,
            })

        for section in self.sections:
            my_dict['map'].append({
                'type': 'section',
                'parent': section.parent,
                'address': section.address,
                'size': section.size,
                'name': section.name,
            })

        with open(self.output_filename, 'w') as file:
            yaml_string = yaml.dump(my_dict)
            file.write(yaml_string)

    def process_areas(self, line):
        pattern = ('([.][a-z]{1,})[ ]{1,}(0x[a-fA-F0-9]{1,})[ ]{1,}(0x[a-fA-F0-9]{1,})\n')

        p = re.compile(pattern)
        result = p.search(line)

        if result is not None:
            self.areas.append(Section(parent=None,
                                      name=result.group(1),
                                      address=int(result.group(2), 0),
                                      size=int(result.group(3), 0),
                                      type='area'
                                      )
                              )

    def process_sections(self, line):
        pattern = ('\s(.[^.]+).([^. \n]+)[\n\r]\s+(0x[0-9a-fA-F]{16})\s+(0x[0-9a-fA-F]+)\s+[^\n]+[\n\r]{1}')

        p = re.compile(pattern)
        result = p.search(line)

        if result is not None:
            self.sections.append(Section(parent=result.group(1),
                                         name=result.group(2),
                                         address=int(result.group(3), 0),
                                         size=int(result.group(4), 0),
                                         type='section'
                                         )
                                 )
