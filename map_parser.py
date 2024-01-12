import re
import yaml

from section import Section


class MapParser:
    """
    Parse a linker map file and convert it to a yaml file for further processing
    """
    def __init__(self, input_filename, output_filename):
        self.sections = []
        self.subsections = []
        self.input_filename = input_filename
        self.output_filename = output_filename

    def parse(self):
        with open(self.input_filename, 'r', encoding='utf8') as file:

            file_iterator = iter(file)
            prev_line = next(file_iterator)
            for line in file_iterator:
                self.process_areas(prev_line)
                multiple_line = prev_line + line
                self.process_sections(multiple_line)
                prev_line = line

        my_dict = {'map': []}
        for section in self.sections:
            my_dict['map'].append({
                'type': 'area',
                'address': section.address,
                'size': section.size,
                'id': section.id,
                'flags': section.flags
            })

        for subsection in self.subsections:
            my_dict['map'].append({
                'type': 'section',
                'parent': subsection.parent,
                'address': subsection.address,
                'size': subsection.size,
                'id': subsection.id,
                'flags': subsection.flags
            })

        with open(self.output_filename, 'w', encoding='utf8') as file:
            yaml_string = yaml.dump(my_dict)
            file.write(yaml_string)

    def process_areas(self, line):
        pattern = r'([.][a-z]{1,})[ ]{1,}(0x[a-fA-F0-9]{1,})[ ]{1,}(0x[a-fA-F0-9]{1,})\n'

        p = re.compile(pattern)
        result = p.search(line)

        if result is not None:
            self.sections.append(Section(parent=None,
                                         id=result.group(1),
                                         address=int(result.group(2), 0),
                                         size=int(result.group(3), 0),
                                         _type='area'
                                         )
                                 )

    def process_sections(self, line):
        pattern = r'\s(.[^.]+).([^. \n]+)[\n\r]\s+(0x[0-9a-fA-F]{16})\s+' \
                  r'(0x[0-9a-fA-F]+)\s+[^\n]+[\n\r]{1}'

        p = re.compile(pattern)
        result = p.search(line)

        if result is not None:
            self.subsections.append(Section(parent=result.group(1),
                                            id=result.group(2),
                                            address=int(result.group(3), 0),
                                            size=int(result.group(4), 0),
                                            _type='section'
                                            )
                                    )
