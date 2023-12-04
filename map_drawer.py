import copy
from math import cos

import svgwrite
from svgwrite import Drawing

from area import Section
from style import Style


class Map:
    dwg: Drawing
    pointer_y: int

    def __init__(self, diagrams=[], links={}, file='map.svg', **kwargs):
        self.style = kwargs.get('style')
        self.type = type
        self.diagrams = diagrams
        self.current_style = Style()
        self.links = links.get('addresses')
        self.zooms = self._get_valid_linked_sections(links.get('sections'))
        self.file = file
        self.dwg = svgwrite.Drawing(file,
                                    profile='full',
                                    size=('900', '1300'))

    def _get_valid_linked_sections(self, linked_sections):
        """
        Get a valid list of linked sections to draw, given a list of wished sections to be linked

        For a link to be valid, the starting and ending addresses of the linked section/s must be visible and available
        inside of at least one single area

        :param linked_sections: List of sections or pair of sections to be linked
        :return: List of valid (start, end) addresses for sections
        """

        l_sections = []

        # Iterate through all linked sections
        for linked_section in linked_sections:
            appended = False
            multi_section = False

            # Check if we are dealing with a link for a single section or for many of them. That is, user passed a
            # string or a list of two strings
            if isinstance(linked_section, list):
                multi_section = True

            # Iterate through all available areas checking if this is a valid link: i.e, the starting and ending
            # addresses of the linked section/s is visible and available inside of a single area
            for area in self.diagrams:
                start = None
                end = None

                # Exit loop if we found that the link is valid
                if appended:
                    break

                for section in area.sections:
                    # If single section, the start and end address of the linked section equals those of the section
                    if not multi_section:
                        if section.name == linked_section:
                            l_sections.append([section.address, section.address + section.size])
                            appended = True
                            break
                    # If multiple section, the start and end address of the linked section are the start of the first
                    # provided section and the end of the second provided section respectively
                    else:
                        if section.name == linked_section[0]:
                            start = section.address
                        elif section.name == linked_section[1]:
                            end = section.address + section.size

                        # If before finishing the iteration on this area, we found a valid start and end address,
                        # we can append this linked section to the list
                        if start is not None and end is not None:
                            l_sections.append([start, end])
                            appended = True
                            break

                # If we finish iterating the area, and we have a valid start (or end) address but the section was not
                # appended, means that the other end of the section is at another area, and that is not valid
                if multi_section and not appended and (start is not None or end is not None):
                    print("WARNING: A multisection zoom region was specified for two sections of different areas,"
                          "which is not supported")
                    break

        return l_sections

    def draw(self):

        dwg = self.dwg

        def _draw_area(diagram):
            base_and_diagram_style = Style()
            base_and_diagram_style.override_properties_from(self.style)
            base_and_diagram_style.override_properties_from(diagram.style)
            group = dwg.add(dwg.g())
            group.add(self._make_main_frame(diagram))

            for section in diagram.sections:
                self._make_section(group, section, diagram, base_and_diagram_style)

            group.translate(diagram.pos_x,
                            diagram.pos_y)

        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill=self.style.background_color))

        lines_group = dwg.add(dwg.g())

        for address in self.links:
            lines_group.add(self._make_links(address))
            pass

        linked_sections_group = dwg.add(dwg.g())
        for zoom in self.zooms:
            is_drawn = False
            for diagram in self.diagrams[1:]:
                if zoom[0] >= diagram.lowest_memory and \
                        zoom[1] <= diagram.highest_memory and \
                        zoom[0] >= self.diagrams[0].lowest_memory and \
                        zoom[1] <= self.diagrams[0].highest_memory:
                    linked_sections_group.add(self._make_poly(diagram, zoom[0], zoom[1]))
                    is_drawn = True
            if not is_drawn:
                print("WARNING: Starting or ending point of the zoom region is outside the shown areas")

        for diagram in self.diagrams:
            _draw_area(diagram)

        dwg.save()

    def _make_main_frame(self, diagram):
        return self.dwg.rect((0, 0), (diagram.size_x, diagram.size_y),
                             fill=self.style.area_background_color,
                             stroke=self.style.area_background_color,
                             stroke_width=1)

    def _make_box(self, section: Section, style):
        return self.dwg.rect((section.pos_x, section.pos_y),
                             (section.size_x, section.size_y),
                             fill=style.section_fill_color,
                             stroke=style.section_stroke_color,
                             stroke_width=style.section_stroke_width)

    def _make_gap(self, section: Section, style: Style) -> svgwrite.container.Group:
        """
        Make a gap representation for a given section.

        Depending on the selected gap type (at style/gaps_type), gap can be wave (~), double wave(≈), diagonal(/)
        or dots(...)
        :param section: Section for which the gap wants to be created
        :param style: Style to apply to the new gap
        :return: SVG group container with the gaps graphics
        """
        group = self.dwg.g()
        mid_point_x = (section.pos_x + section.size_x) / 2
        mid_point_y = (section.pos_y + section.size_y) / 2

        def _make_gap_dots(_section: Section, _style: Style) -> svgwrite.container.Group:
            """
            Make a gap representation using dot style

            :param _section: Section for which the gap wants to be created
            :param _style: Style to apply to the new gap
            :return: SVG group container with the gaps graphics
            """
            rectangle = self.dwg.rect((_section.pos_x, _section.pos_y), (_section.size_x, _section.size_y))
            rectangle.fill(_style.section_fill_color)
            rectangle.stroke(_style.section_stroke_color, width=_style.section_stroke_width)

            group.add(rectangle)

            points_list = [
                (mid_point_x, mid_point_y),
                (mid_point_x, mid_point_y + 12),
                (mid_point_x, mid_point_y - 12),
            ]

            for points_set in points_list:
                group.add(self.dwg.circle(points_set, 3, fill=_style.label_color))

            return group

        def _make_gap_wave(_section: Section, _style: Style) -> svgwrite.container.Group:
            """
            Make a gap representation using wave style

            :param _section: Section for which the gap wants to be created
            :param _style: Style to apply to the new gap
            :return: SVG group container with the gaps graphics
            """
            wave_len = _section.size_x + 1
            shifts = [(-5, 2/5, 0), (5, 3 / 5, _section.size_y), ]

            for shift in shifts:
                points = [(i, mid_point_y + shift[0] + 2 * cos(i / 24)) for i in range(wave_len)]
                points.extend(
                    [
                        (_section.pos_x + _section.size_x, (_section.pos_y + _section.size_y) * shift[1]),
                        (_section.pos_x + _section.size_x, _section.pos_y + shift[2]),
                        (_section.pos_x, _section.pos_y + shift[2]),
                        (_section.pos_x, mid_point_y + shift[0] + 2 * cos(_section.pos_x / 24)),
                    ]
                )

                group.add(self.dwg.polyline(points,
                                            stroke=_style.section_stroke_color,
                                            stroke_width=_style.section_stroke_width,
                                            fill=_style.section_fill_color))

            return group

        def _make_gap_double_wave(_section: Section, _style: Style) -> svgwrite.container.Group:
            """
            Make a gap representation using double wave style

            :param _section: Section for which the gap wants to be created
            :param _style: Style to apply to the new gap
            :return: SVG group container with the gaps graphics
            """
            points_list = [[
                (_section.pos_x, (_section.pos_y + _section.size_y) * 2 / 5),
                (_section.pos_x, _section.pos_y),
                (_section.pos_x + _section.size_x, _section.pos_y),
                (_section.pos_x + _section.size_x, (_section.pos_y + _section.size_y) * 2 / 5),
            ],
                [
                    (_section.pos_x, (_section.pos_y + _section.size_y) * 3 / 5),
                    (_section.pos_x, _section.pos_y + _section.size_y),
                    (_section.pos_x + _section.size_x, _section.pos_y + _section.size_y),
                    (_section.pos_x + _section.size_x, (_section.pos_y + _section.size_y) * 3 / 5),
                ]
            ]

            rectangle = self.dwg.rect((_section.pos_x, _section.pos_y), (_section.size_x, _section.size_y))
            rectangle.fill(_style.section_fill_color)

            group.add(rectangle)

            for points_set in points_list:
                group.add(self.dwg.polyline(points_set,
                                            stroke=_style.section_stroke_color,
                                            stroke_width=_style.section_stroke_width,
                                            fill='none'))
            wave_length = 20
            shifts = [(0, -5),
                      (0, +5),
                      (_section.size_x, -5),
                      (_section.size_x, +5),
                      ]

            for shift in shifts:
                points = [(i - wave_length / 2 + shift[0], mid_point_y + shift[1] + cos(i / 2))
                          for i in range(wave_length)]

                group.add(self.dwg.polyline(points,
                                            stroke=_style.section_stroke_color,
                                            stroke_width=_style.section_stroke_width,
                                            fill='none'))

            return group

        def _make_gap_diagonal(_section: Section, _style: Style) -> svgwrite.container.Group:
            """
            Make a gap representation using diagonal style

            :param _section: Section for which the gap wants to be created
            :param _style: Style to apply to the new gap
            :return: SVG group container with the gaps graphics
            """
            points_list = [[(_section.pos_x, _section.pos_y),
                            (_section.pos_x + _section.size_x, _section.pos_y),
                            (_section.pos_x + _section.size_x, (_section.pos_y + _section.size_y) * 3 / 10),
                            (_section.pos_x, (_section.pos_y + _section.size_y) * 5 / 10),
                            (_section.pos_x, _section.pos_y)
                            ], [(_section.pos_x, _section.pos_y + _section.size_y),
                                (_section.pos_x + _section.size_x, _section.pos_y + _section.size_y),
                                (_section.pos_x + _section.size_x, (_section.pos_y + _section.size_y) * 5 / 10),
                                (_section.pos_x, (_section.pos_y + _section.size_y) * 7 / 10),
                                (_section.pos_x, _section.pos_y + _section.size_y),
                                ]]

            for points_set in points_list:
                group.add(self.dwg.polyline(points_set,
                                            stroke=_style.section_stroke_color,
                                            stroke_width=_style.section_stroke_width,
                                            fill=_style.section_fill_color))

            return group

        gaps = [('/', _make_gap_diagonal),
                ('≈', _make_gap_double_wave),
                ('~', _make_gap_wave),
                ('...', _make_gap_dots),]

        for gap in gaps:
            if style.gaps_type == gap[0]:
                return gap[1](section, style)

    def _make_text(self, text, pos_x, pos_y, style, anchor, baseline='middle', small=False):
        return self.dwg.text(text, insert=(pos_x, pos_y),
                             stroke='white',
                             # focusable='true',
                             fill=style.label_color,
                             stroke_width=style.label_stroke_width,
                             font_size='12px' if small else style.label_size,
                             font_weight="normal",
                             font_family=style.label_font,
                             text_anchor=anchor,
                             alignment_baseline=baseline
                             )

    def _make_name(self, section, style):
        return self._make_text(section.name,
                               section.name_label_pos_x,
                               section.name_label_pos_y,
                               style=style,
                               anchor='middle',
                               )

    def _make_size_label(self, section, style):
        return self._make_text(hex(section.size),
                               section.size_label_pos[0],
                               section.size_label_pos[1],
                               style,
                               'start',
                               'hanging',
                               True,
                               )

    def _make_address(self, section, style):
        return self._make_text(hex(section.address),
                               section.addr_label_pos_x,
                               section.addr_label_pos_y,
                               anchor='start',
                               style=style)

    def _make_section(self, group, section: Section, diagram, style):
        section.size_x = diagram.size_x
        section.size_y = diagram.to_pixels(section.size)
        section.pos_y = diagram.to_pixels(diagram.end_address - section.size - section.address)
        section.pos_x = 0
        overrides = getattr(style, 'overrrides', None)
        section_style = Style()
        section_style.override_properties_from(style)

        if overrides:
            for item in overrides:
                if section.name in item.get('sections'):
                    section_style.override_properties_from(Style(style=item))

        if section.is_gap():
            group.add(self._make_gap(section, section_style))
        else:
            group.add(self._make_box(section, section_style))
            if section.size_y > 20:
                group.add(self._make_name(section, section_style))
                group.add(self._make_address(section, section_style))
                group.add(self._make_size_label(section, section_style))
        return group

    def _get_points_for_address(self, address, diagram):
        left_block_view = self.diagrams[0]
        right_block_view = diagram

        left_block_x = left_block_view.size_x + left_block_view.pos_x
        left_block_x2 = left_block_x + 30
        left_block_y = left_block_view.pos_y + left_block_view.to_pixels_relative(address)

        right_block_x = diagram.pos_x
        right_block_x2 = right_block_x - 30
        right_block_y = right_block_view.pos_y + right_block_view.to_pixels_relative(address)

        return [(left_block_x, left_block_y),
                (left_block_x2, left_block_y),
                (right_block_x2, right_block_y),
                (right_block_x, right_block_y),
                ]

    def _make_poly(self, diagram, start_address, end_address):

        points = []
        reversed = self._get_points_for_address(end_address, diagram)
        reversed.reverse()
        points.extend(self._get_points_for_address(start_address, diagram))
        points.extend(reversed)

        return self.dwg.polyline(points,
                                 stroke=self.style.link_stroke_color,
                                 stroke_width=self.style.link_stroke_width,
                                 fill=self.style.link_fill_color,
                                 opacity=self.style.link_opacity)

    def _make_links(self, address):
        hlines = self.dwg.g(id='hlines', stroke='grey')

        for diagram in self.diagrams[1:]:
            if not diagram.has_address(address):
                continue

            def _make_line(x1, y1, x2, y2):
                return self.dwg.line(start=(x1, y1), end=(x2, y2),
                                     stroke_width=self.style.link_stroke_width,
                                     stroke=self.style.link_stroke_color)

            points = self._get_points_for_address(address, diagram)

            hlines.add(_make_line(x1=points[0][0], y1=points[0][1],
                                  x2=points[1][0], y2=points[1][1]))

            hlines.add(_make_line(x1=points[1][0], y1=points[1][1],
                                  x2=points[2][0], y2=points[2][1]))

            hlines.add(_make_line(x1=points[2][0], y1=points[2][1],
                                  x2=points[3][0], y2=points[3][1]))
        return hlines
