from math import cos
from svgwrite import Drawing
import svgwrite

from helpers import DefaultAppValues
from labels import Side
from logger import logger
from section import Section
from style import Style


class MapRender:
    """
    This class does the actual rendering of the map.

    Takes all the graphical information stored at the different sections and areas, together
    with their style and configuration, and convert them to SVG objects (see `draw()` function)
    """
    dwg: Drawing
    pointer_y: int

    def __init__(self, area_view, links, file='map.svg', size=DefaultAppValues.DOCUMENT_SIZE, **kwargs):
        self.style = kwargs.get('style')
        self.type = type
        self.area_views = area_view
        self.current_style = Style()
        self.links = links
        self.links_sections = self._get_valid_linked_sections(links.sections) if links is not None else []
        self.file = file
        self.size = size
        self.dwg = svgwrite.Drawing(file,
                                    profile='full',
                                    size=self.size
                                    )

    def _get_valid_linked_sections(self, linked_sections):
        """
        Get a valid list of linked sections to draw, given a list of wished sections to be linked

        For a link to be valid, the starting and ending addresses of the linked section/s must be
        visible and available inside of at least one single area

        :param linked_sections: List of sections or pair of sections to be linked
        :return: List of valid (start, end) addresses for sections
        """

        l_sections = []

        # Iterate through all linked sections
        for linked_section in linked_sections:
            appended = False
            multi_section = False

            # Check if we are dealing with a link for a single section or for many of them.
            # That is, user passed a string or a list of two strings
            if isinstance(linked_section, list):
                multi_section = True

            # Iterate through all available areas checking if this is a valid link: i.e, the
            # starting and ending addresses of the linked section/s is visible and available
            # inside of a single area
            for area in self.area_views:
                start = None
                end = None

                # Exit loop if we found that the link is valid
                if appended:
                    break

                for section in area.sections.get_sections():
                    # If single section, the start and end address of the linked section equals
                    # those of the section
                    if not multi_section:
                        if section.id == linked_section:
                            l_sections.append([section.address, section.address + section.size])
                            appended = True
                            break
                    # If multiple section, the start and end address of the linked section are the
                    # start of the first provided section and the end of the second provided section
                    # respectively
                    else:
                        if section.id == linked_section[0]:
                            start = section.address
                        elif section.id == linked_section[1]:
                            end = section.address + section.size

                        # If before finishing the iteration on this area, we found a valid start and
                        # end address, we can append this linked section to the list
                        if start is not None and end is not None:
                            l_sections.append([start, end])
                            appended = True
                            break

                # If we finish iterating the area, and we have a valid start (or end) address but
                # the section was not appended, means that the other end of the section is at
                # another area, and that is not valid
                if multi_section and not appended and (start is not None or end is not None):
                    logger.warning("A multisection zoom region was specified for two sections"
                                   f"of different areas, which is not supported: "
                                   f"{linked_section[0]}, {linked_section[1]}")
                    break

        return l_sections

    def draw(self):

        dwg = self.dwg

        def _draw_area(area) -> svgwrite.container.Group:
            """
            Draw given area

            Draw the title for the area, then, for each subarea proceed to draw
            the different elements. Those are the frame and sections, with its
            information such as labels, name, memory, etc...

            :param area: Area to be drawn
            :return Container with an area to be drawn
            """
            area_group = dwg.g()
            title = self._make_title(area)
            title.translate(area.pos_x, area.pos_y)
            area_group.add(title)

            for sub_area in area.get_split_area_views():
                subarea_group = dwg.g()

                subarea_group.add(self._make_main_frame(sub_area))

                for section in sub_area.sections.get_sections():
                    if section.is_hidden():
                        continue
                    self._make_section(subarea_group, section, sub_area)

                subarea_group.translate(sub_area.pos_x, sub_area.pos_y)

                area_group.add(subarea_group)

            return area_group

        def draw_section_links() -> svgwrite.container.Group:
            linked_sections_group = dwg.g()
            for section_link in self.links_sections:
                is_drawn = False
                for _area_view in self.area_views[1:]:
                    if section_link[0] >= _area_view.sections.lowest_memory and \
                            section_link[1] <= _area_view.sections.highest_memory and \
                            section_link[0] >= self.area_views[0].sections.lowest_memory and \
                            section_link[1] <= self.area_views[0].sections.highest_memory:
                        linked_sections_group.add(self._make_poly(_area_view,
                                                                  section_link[0],
                                                                  section_link[1],
                                                                  self.links.style))
                        is_drawn = True
                        break
                if not is_drawn:
                    logger.warning(f"Starting or ending point of the zoom region is outside the "
                                   f"shown areas for the link with addresses "
                                   f"[{hex(section_link[0])}, {hex(section_link[1])}]")

            return linked_sections_group

        def draw_labels() -> svgwrite.container.Group:
            global_labels = dwg.g()
            for area in self.area_views:
                for subarea in area.get_split_area_views():
                    g = dwg.g()

                    if subarea.labels is not None:
                        for label in subarea.labels.labels:

                            if subarea.sections.has_address(label.address):
                                g.add(self._make_label(label, subarea))

                    g.translate(subarea.pos_x, subarea.pos_y)
                    global_labels.add(g)
            return global_labels

        def draw_growths() -> svgwrite.container.Group:
            # We need to do another pass once all areas are drawn in order to be able to properly
            # draw the growth arrows without the break areas hiding them. Also, as we do stuff
            # outside the loop where the areas are drawn, we loose the reference for translation,
            # and we have to manually translate the grows here
            for _area_view in self.area_views:
                for subarea in _area_view.get_split_area_views():

                    area_growth = dwg.g()
                    for section in subarea.sections.get_sections():
                        if section.is_hidden():
                            continue
                        area_growth.add(self._make_growth(section))

                    area_growth.translate(subarea.pos_x, subarea.pos_y)
                    growths_group.add(area_growth)
            return growths_group

        def draw_links() -> svgwrite.container.Group:
            lines_group = dwg.g()
            for address in self.links.addresses:
                lines_group.add(self._make_link(address, self.links.style))
            return lines_group

        dwg.add(dwg.rect(insert=(0, 0),
                         size=('100%', '100%'),
                         rx=None,
                         ry=None,
                         fill=self.style.background))

        growths_group = dwg.g()

        dwg.add(draw_section_links()) if self.links_sections is not None else None
        dwg.add(draw_links()) if self.links is not None else None

        for area_view in self.area_views:
            dwg.add(_draw_area(area_view))

        dwg.add(draw_labels())
        dwg.add(draw_growths())
        dwg.save()

    def _make_title(self, area_view):
        title_pos_x = area_view.size_x / 2
        title_pos_y = -20
        return self._make_text(area_view.title,
                               (title_pos_x, title_pos_y),
                               style=area_view.style,
                               anchor='middle',
                               text_type='title'
                               )

    def _make_growth(self, section: Section) -> svgwrite.container.Group:
        """
        Make the growth arrows for the sections that have it
        :param section: Section for which to draw the arrow
        :return: A SVG group containing the new arrows
        """
        group = self.dwg.g()
        # Why grows doesn't draw on a break section?
        multiplier = section.style.growth_arrow_size
        mid_point_x = (section.pos_x + section.size_x) / 2
        arrow_head_width = 5 * multiplier
        arrow_head_height = 10 * multiplier
        arrow_length = 10 * multiplier
        arrow_tail_width = 1 * multiplier

        def _make_growth_arrow_generic(arrow_start_y, direction):
            points_list = [(mid_point_x - arrow_tail_width, arrow_start_y),
                           (mid_point_x - arrow_tail_width,
                            arrow_start_y - direction * arrow_length),
                           (mid_point_x - arrow_head_width,
                            arrow_start_y - direction * arrow_head_height),
                           (mid_point_x,
                            arrow_start_y - direction * (arrow_length + arrow_head_height)),
                           (mid_point_x + arrow_head_width,
                            arrow_start_y - direction * arrow_head_height),
                           (mid_point_x + arrow_tail_width,
                            arrow_start_y - direction * arrow_length),
                           (mid_point_x + arrow_tail_width,
                            arrow_start_y)]

            group.add(self.dwg.polyline(points_list,
                                        stroke=section.style.growth_arrow_stroke,
                                        stroke_width=1,
                                        fill=section.style.growth_arrow_fill))

        if section.is_grow_up():
            _make_growth_arrow_generic(section.pos_y, 1)
        if section.is_grow_down():
            _make_growth_arrow_generic(section.pos_y + section.size_y, -1)

        return group

    def _make_main_frame(self, area_view):
        return self.dwg.rect((0, 0), (area_view.size_x, area_view.size_y),
                             fill=area_view.style.background,
                             stroke=area_view.style.stroke,
                             stroke_width=area_view.style.stroke_width)

    def _make_box(self, section: Section):
        return self.dwg.rect((section.pos_x, section.pos_y),
                             (section.size_x, section.size_y),
                             fill=section.style.fill,
                             stroke=section.style.stroke,
                             stroke_width=section.style.stroke_width)

    def _make_break(self, section: Section) -> svgwrite.container.Group:
        """
        Make a break representation for a given section.

        Depending on the selected break type (at style/break_type), break can be wave (~), double
        wave(≈), diagonal(/) or dots(...)
        :param section: Section for which the break wants to be created
        :return: SVG group container with the breaks graphics
        """
        group = self.dwg.g()
        mid_point_x = (section.pos_x + section.size_x) / 2
        mid_point_y = (section.pos_y + section.size_y) / 2
        style = section.style

        def _make_break_dots(_section: Section) -> svgwrite.container.Group:
            """
            Make a break representation using dot style

            :param _section: Section for which the break wants to be created
            :return: SVG group container with the breaks graphics
            """
            rectangle = self.dwg.rect((_section.pos_x, _section.pos_y),
                                      (_section.size_x, _section.size_y))

            rectangle.fill(style.fill)
            rectangle.stroke(style.stroke, width=style.stroke_width)

            group.add(rectangle)

            points_list = [
                (mid_point_x, mid_point_y),
                (mid_point_x, mid_point_y + 12),
                (mid_point_x, mid_point_y - 12),
            ]

            for points_set in points_list:
                group.add(self.dwg.circle(points_set, 3, fill=style.text_fill))

            return group

        def _make_break_wave(_section: Section) -> svgwrite.container.Group:
            """
            Make a break representation using wave style

            :param _section: Section for which the break wants to be created
            :return: SVG group container with the breaks graphics
            """
            wave_len = _section.size_x + 1
            shifts = [(-5, 2/5, 0), (5, 3 / 5, _section.size_y), ]

            for shift in shifts:
                points = [(i, mid_point_y + shift[0] + 2 * cos(i / 24)) for i in range(wave_len)]
                points.extend(
                    [
                        (_section.pos_x + _section.size_x,
                         (_section.pos_y + _section.size_y) * shift[1]),
                        (_section.pos_x + _section.size_x, _section.pos_y + shift[2]),
                        (_section.pos_x, _section.pos_y + shift[2]),
                        (_section.pos_x, mid_point_y + shift[0] + 2 * cos(_section.pos_x / 24)),
                    ]
                )

                group.add(self.dwg.polyline(points,
                                            stroke=style.stroke,
                                            stroke_width=style.stroke_width,
                                            fill=style.fill))

            return group

        def _make_break_double_wave(_section: Section) -> svgwrite.container.Group:
            """
            Make a break representation using double wave style

            :param _section: Section for which the break wants to be created
            :return: SVG group container with the breaks graphics
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

            rectangle = self.dwg.rect((_section.pos_x, _section.pos_y),
                                      (_section.size_x, _section.size_y))
            rectangle.fill(section.style.fill)
            group.add(rectangle)

            for points_set in points_list:
                group.add(self.dwg.polyline(points_set,
                                            stroke=style.stroke,
                                            stroke_width=style.stroke_width,
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
                                            stroke=style.stroke,
                                            stroke_width=style.stroke_width,
                                            fill='none'))

            return group

        def _make_break_diagonal(_section: Section) -> svgwrite.container.Group:
            """
            Make a break representation using diagonal style

            :param _section: Section for which the break wants to be created
            :return: SVG group container with the breaks graphics
            """
            points_list = [[(_section.pos_x, _section.pos_y),
                            (_section.pos_x + _section.size_x, _section.pos_y),
                            (_section.pos_x + _section.size_x,
                             (_section.pos_y + _section.size_y) * 3 / 10),
                            (_section.pos_x, (_section.pos_y + _section.size_y) * 5 / 10),
                            (_section.pos_x, _section.pos_y)
                            ], [(_section.pos_x, _section.pos_y + _section.size_y),
                                (_section.pos_x + _section.size_x,
                                 _section.pos_y + _section.size_y),
                                (_section.pos_x + _section.size_x,
                                 (_section.pos_y + _section.size_y) * 5 / 10),
                                (_section.pos_x, (_section.pos_y + _section.size_y) * 7 / 10),
                                (_section.pos_x, _section.pos_y + _section.size_y),
                                ]]

            for points_set in points_list:
                group.add(self.dwg.polyline(points_set,
                                            stroke=style.stroke,
                                            stroke_width=style.stroke_width,
                                            fill=style.fill))

            return group

        breaks = [('/', _make_break_diagonal),
                  ('≈', _make_break_double_wave),
                  ('~', _make_break_wave),
                  ('...', _make_break_dots), ]

        for _break in breaks:
            if style.break_type == _break[0]:
                return _break[1](section)

    def _make_text(self,
                   text,
                   position,
                   style,
                   text_type='normal',
                   **kwargs):

        if text_type == 'title':
            size = '24px'
        elif text_type == 'small':
            size = '12px'
        else:
            size = style.font_size

        return self.dwg.text(text, insert=(position[0], position[1]),
                             stroke=style.text_stroke,
                             # focusable='true',
                             fill=style.text_fill,
                             stroke_width=style.text_stroke_width,
                             font_size=size,
                             font_weight="normal",
                             font_family=style.font_type,
                             text_anchor=kwargs.get('anchor', 'middle'),
                             alignment_baseline=kwargs.get('baseline', 'middle')
                             )

    def _make_name(self, section):
        name = section.name if section.name is not None else section.id
        return self._make_text(name,
                               (section.name_label_pos_x, section.name_label_pos_y),
                               style=section.style,
                               anchor='middle',
                               )

    def _make_size_label(self, section):
        return self._make_text(hex(section.size),
                               (section.size_label_pos[0], section.size_label_pos[1]),
                               section.style,
                               anchor='start',
                               baseline='hanging',
                               text_type='small'
                               )

    def _make_address(self, section):
        return self._make_text(hex(section.address),
                               (section.addr_label_pos_x, section.addr_label_pos_y),
                               anchor='start',
                               style=section.style)

    def _make_section(self, group, section: Section, area_view):
        section.size_x = area_view.size_x
        section.size_y = area_view.to_pixels(section.size)
        section.pos_y = area_view.to_pixels(area_view.end_address - section.size - section.address)
        section.pos_x = 0

        if section.is_break():
            group.add(self._make_break(section))
        else:
            group.add(self._make_box(section))
            if not section.is_name_hidden():
                group.add(self._make_name(section))
            if not section.is_address_hidden():
                group.add(self._make_address(section))
            if not section.is_size_hidden():
                group.add(self._make_size_label(section))

        return group

    def _get_points_for_address(self, address, area_view):
        left_block_view = self.area_views[0]
        right_block_view = area_view

        left_block_x = left_block_view.size_x + left_block_view.pos_x
        left_block_x2 = left_block_x + 30
        left_block_y = left_block_view.pos_y + left_block_view.to_pixels_relative(address)

        right_block_x = area_view.pos_x
        right_block_x2 = right_block_x - 30
        right_block_y = right_block_view.pos_y + right_block_view.to_pixels_relative(address)

        return [(left_block_x, left_block_y),
                (left_block_x2, left_block_y),
                (right_block_x2, right_block_y),
                (right_block_x, right_block_y),
                ]

    def _make_poly(self, area_view, start_address, end_address, style):

        def find_right_subarea_view(address, area):
            """
            Given an area, find the subarea where the provided address is

            :param address: Address to look for
            :param area: Area that contains the subarea to be found
            :return: Found subarea, if not found, parent area
            """
            for subarea in area.get_split_area_views():
                if subarea.start_address <= address <= subarea.end_address:
                    return subarea
            return area

        points = []

        end_subarea = find_right_subarea_view(end_address, area_view)
        start_subarea = find_right_subarea_view(start_address, area_view)

        _reversed = self._get_points_for_address(end_address, end_subarea)
        _reversed.reverse()
        points.extend(self._get_points_for_address(start_address, start_subarea))
        points.extend(_reversed)

        return self.dwg.polyline(points,
                                 stroke=style.stroke,
                                 stroke_width=style.stroke_width,
                                 fill=style.fill,
                                 opacity=style.opacity)

    def _make_arrow_head(self, label, direction='down'):
        if direction == 'left':
            angle = 90
        elif direction == 'right':
            angle = 270
        elif direction == 'up':
            angle = 0
        else:
            angle = 180

        arrow_head_width = 5 * label.style.weight
        arrow_head_height = 10 * label.style.weight
        group = self.dwg.g()
        points_list = [(0, 0 - arrow_head_height),
                       (0 - arrow_head_width, 0 - arrow_head_height),
                       (0, 0),
                       (0 + arrow_head_width, 0 - arrow_head_height),
                       (0, 0 - arrow_head_height),
                       ]

        poly = self.dwg.polyline(points_list,
                                 stroke=label.style.stroke,
                                 stroke_width=1,
                                 fill=label.style.stroke)
        poly.rotate(angle, center=(0, 0))
        group.add(poly)

        return group

    def _make_label(self, label, area_view):
        line_label_spacer = 3
        g = self.dwg.g()
        address = label.address
        text = label.text
        label_length = label.length

        if address is None:
            raise KeyError("A label without address was found")

        if label.side == Side.RIGHT:
            pos_x_d = area_view.size_x
            direction = 1
            anchor = 'start'

        else:
            pos_x_d = 0
            direction = -1
            anchor = 'end'

        pos_y = area_view.to_pixels_relative(address)
        points = [(0 + pos_x_d, pos_y), (direction*(label_length + pos_x_d), pos_y)]

        def add_arrow_head(_direction):
            arrow_direction = 'right'
            if 'in' == _direction:
                if label.side == Side.LEFT:
                    arrow_direction = 'right'
                elif label.side == Side.RIGHT:
                    arrow_direction = 'left'

                arrow_head_x = pos_x_d

            elif 'out' == _direction:
                if label.side == Side.LEFT:
                    arrow_direction = 'left'
                elif label.side == Side.RIGHT:
                    arrow_direction = 'right'

                arrow_head_x = direction * (label_length + pos_x_d)

            else:
                logger.warning(f"Invalid direction {_direction} provided")
                return

            g.add(self._make_arrow_head(label, direction=arrow_direction))\
                .translate(arrow_head_x, pos_y)

        if type(label.directions) == str:
            add_arrow_head(label.directions)
        elif type(label.directions) == list:
            for head_direction in label.directions:
                add_arrow_head(head_direction)

        g.add(self._make_text(text,
                              (direction*(pos_x_d + label_length + line_label_spacer), pos_y),
                              label.style,
                              anchor=anchor))

        g.add(self.dwg.polyline(points,
                                stroke=label.style.stroke,
                                stroke_dasharray=label.style.stroke_dasharray,
                                stroke_width=label.style.stroke_width
                                ))
        return g

    def _make_link(self, address, style):
        hlines = self.dwg.g(id='hlines', stroke='grey')

        for area_view in self.area_views[1:]:
            for subarea in area_view.get_split_area_views():

                if not subarea.sections.has_address(address):
                    continue

                def _make_line(x1, y1, x2, y2):
                    return self.dwg.line(start=(x1, y1), end=(x2, y2),
                                         stroke_width=style.stroke_width,
                                         stroke=style.stroke)

                points = self._get_points_for_address(address, subarea)

                hlines.add(_make_line(x1=points[0][0], y1=points[0][1],
                                      x2=points[1][0], y2=points[1][1]))

                hlines.add(_make_line(x1=points[1][0], y1=points[1][1],
                                      x2=points[2][0], y2=points[2][1]))

                hlines.add(_make_line(x1=points[2][0], y1=points[2][1],
                                      x2=points[3][0], y2=points[3][1]))
        return hlines
