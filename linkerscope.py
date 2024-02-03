#!/usr/bin/env python3

import argparse
import copy

import yaml

from area_view import AreaView
from helpers import safe_element_list_get, safe_element_dict_get, DefaultAppValues
from links import Links
from logger import logger
from map_render import MapRender
from style import Style
from map_file_loader import MapFileLoader
from sections import Sections


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('input',
                        help='Name of the map file,'
                             'can be either linker .map files or .yaml descriptor')
    parser.add_argument('--output',
                        '-o',
                        help='Name for the generated .svg file',
                        default='map.svg')
    parser.add_argument('--convert',
                        help='Performs the conversion of a .map file to .yaml if a .map file was passed without any additional step',
                        action='store_true',
                        default=False,
                        required=False
                        )
    parser.add_argument('--config',
                        '-c',
                        help='Configuration file (.yml). If not specified,'
                             'will use config.yaml as default',
                        )

    return parser.parse_args()


def get_area_views(_raw_sections, _base_style, config=None):
    """
    Get the area view/s with the specified style and properties (if any)

    Given a list of sections, base style and configuration, this function produce a series of
    area views with specific properties and styles. If a configuration object is passed, it will
    be used to retrieve additional configured style and properties for one or more area views.
    If no configuration is passed, only one area view will be generated with the default style
    and properties

    :param _raw_sections: A list of unprocessed sections to be selected from and displayed
    :param _base_style: Base / default style to build child styles from
    :param config: Optional, configuration object indicating number of areas, style, properties,...
    :return: A list of configured area views
    """
    def get_default_area_view(sections, style):
        """
        Get an area view configured with default parameters
        :param sections: A list of unprocessed sections to be selected from and displayed
        :param style: Base / default style to build child styles from
        :return: List of one element corresponding to a default area view
        """
        return [AreaView(
            sections=(Sections(sections=sections)),
            style=copy.deepcopy(style)
        )]

    def get_custom_area_views(sections, style):
        """
        Get a list of area views configured according to passed parameters

        :param sections: A list of unprocessed sections to be selected from and displayed
        :param style: Base / default style to build child styles from
        :return: List of one or various custom area views
        """
        area_views = []
        for i, area_element in enumerate(area_configurations):
            area_config = safe_element_dict_get(area_element, 'area')
            section_size = safe_element_dict_get(area_config, 'section-size', None)
            memory_range = safe_element_dict_get(area_config, 'range', None)
            area_style = copy.deepcopy(style)
            filtered_sections = (Sections(sections=copy.deepcopy(sections))
                                 .filter_address_min(safe_element_list_get(memory_range, 0))
                                 .filter_address_max(safe_element_list_get(memory_range, 1))
                                 .filter_size_min(safe_element_list_get(section_size, 0))
                                 .filter_size_max(safe_element_list_get(section_size, 1))
                                 )
            if len(filtered_sections.get_sections()) == 0:
                logger.warning(f"Filter for area view with index {i} doesn't result in any"
                               f"section. Try re-adjusting memory range, size, ... This area "
                               f"will be omitted")
                continue

            area_views.append(
                AreaView(
                    sections=filtered_sections,
                    area_config=area_config,
                    style=area_style.override_properties_from(
                        Style(style=safe_element_dict_get(area_config, 'style', None)))
                )
            )

        return area_views

    area_configurations = safe_element_dict_get(config, 'areas', []) or []

    if len(area_configurations) == 0:
        return get_default_area_view(_raw_sections, _base_style)
    else:
        return get_custom_area_views(_raw_sections, _base_style)


arguments = parse_arguments()
raw_sections = MapFileLoader(arguments.input, arguments.convert).parse()
base_style = Style().get_default()


links = None
document_size = DefaultAppValues.DOCUMENT_SIZE
configuration = {}

# Apply custom configuration if configuration file is available
if arguments.config:
    with open(arguments.config, 'r', encoding='utf-8') as file:
        configuration = yaml.safe_load(file)
        if configuration is None:
            configuration = {}

    base_style_cpy = copy.deepcopy(base_style)
    style_config = safe_element_dict_get(configuration, 'style', None)
    base_style.override_properties_from(Style(style=style_config))
    yaml_links = safe_element_dict_get(configuration, 'links', None)
    links_style = base_style_cpy.override_properties_from(
        Style(style=safe_element_dict_get(yaml_links,
                                          'style', None)))

    links = Links(yaml_links, style=links_style)
    document_size = safe_element_dict_get(configuration, 'size', DefaultAppValues.DOCUMENT_SIZE)

MapRender(area_view=get_area_views(raw_sections, base_style, configuration),
          links=links,
          style=base_style,
          file=arguments.output,
          size=document_size
          ).draw()
