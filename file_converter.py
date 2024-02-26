import yaml


class GenericFileConverter:

    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = output_filename

    def save(self):
        _dict = self._parse()

        with open(self.output_filename, 'w', encoding='utf8') as file:
            file.write(yaml.dump(_dict))

    def _parse(self):
        pass


class NordicPartitionsFileConverter(GenericFileConverter):

    def _parse(self):
        _list = []

        with open(self.input_filename, 'r', encoding='utf-8') as file:
            nordic_partitions_file = yaml.safe_load(file)

        for name in nordic_partitions_file:
            e = nordic_partitions_file[name]
            _list.append({'id': name, 'address': e.get('address', 0), 'size': e.get('size', 0)})

        return {'map': _list}


