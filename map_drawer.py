import copy
import svgwrite
from svgwrite import Drawing
from style import Style


class Map:
    dwg: Drawing
    area_width: 200
    pointer_y: int

    def __init__(self, diagrams=[], links={}, force=False, **kwargs):
        self.style = kwargs.get('style')
        self.type = type
        self.diagrams = diagrams
        self.force = force
        self.current_style = Style()
        _links = links.get('addresses')
        for section in self.diagrams[0].sections:
            if section.name in links.get('sections'):
                _links.append(section.address)
                _links.append(section.address + section.size)

        self.lsections = []
        for section in self.diagrams[0].sections:
            if section.name in links.get('sections'):
                self.lsections.append([section.address, section.address + section.size])

        self.links = _links

    def draw_maps(self, file):
        def _configure_current_style(diagram):
            members = [attr for attr in dir(diagram.style) if
                       not callable(getattr(diagram.style, attr)) and not attr.startswith("__") and getattr(
                           diagram.style, attr) is not None]

            self.current_style = copy.deepcopy(self.style)
            for member in members:
                value = getattr(diagram.style, member)
                setattr(self.current_style, member, value)

        def _draw_map(diagram):
            _configure_current_style(diagram)
            group = dwg.add(dwg.g())
            group.add(self._make_main_frame(dwg, diagram))

            for section in diagram.sections:
                self._make_section(group, dwg, section, diagram)
                pass
            group.translate(diagram.pos_x,
                            diagram.pos_y)

        dwg = svgwrite.Drawing(file,
                               profile='full',
                               size=('200%', '200%')
                               )

        lines_group = dwg.add(dwg.g())

        for address in self.links:
            #lines_group.add(self._make_links(address, dwg))
            pass


        lsectionsgroup = dwg.add(dwg.g())
        for lsection in self.lsections:
            for diagram in self.diagrams[1:]:
                if lsection[0] > diagram.lowest_memory and lsection[1] <= diagram.highest_memory:
                    lsectionsgroup.add(self._make_poly(dwg, diagram, lsection[0], lsection[1]))

        for diagram in self.diagrams:
            _draw_map(diagram)

        dwg.save()

    def _make_main_frame(self, dwg, diagram):
        size_x = diagram.size_x
        size_y = diagram.size_y
        rectangle = dwg.rect((0, 0), (size_x, size_y))
        rectangle.fill(self.style.area_fill_color)
        rectangle.stroke(self.style.area_fill_color, width=1)
        return rectangle

    def _make_box(self, dwg, section, diagram):
        section.size_x = diagram.size_x
        section.size_y = diagram.to_pixels(section.size)
        section.pos_y = diagram.to_pixels(diagram.end_address - section.size - section.address)
        section.pos_x = 0
        rectangle = dwg.rect((section.pos_x, section.pos_y), (section.size_x, section.size_y))
        rectangle.fill(self.current_style.box_fill_color)
        rectangle.stroke(self.current_style.box_stroke_color, width=self.current_style.box_stroke_width)
        return rectangle

    def _make_text(self, dwg, text, pos_x, pos_y, anchor, baseline='middle', small=False):
        return dwg.text(text, insert=(pos_x, pos_y),
                        stroke='white',
                        #focusable='true',
                        fill=self.current_style.label_color,
                        stroke_width=self.current_style.label_stroke_width,
                        font_size='12px' if small else self.current_style.label_size,
                        font_weight="normal",
                        font_family=self.current_style.label_font,
                        text_anchor=anchor,
                        alignment_baseline=baseline
                        )

    def _make_name(self, dwg, section):
        return self._make_text(dwg,
                               section.name,
                               section.name_label_pos_x,
                               section.name_label_pos_y,
                              'middle')

    def _make_size_label(self, dwg, section):
        return self._make_text(dwg,
                               hex(section.size),
                               section.size_label_pos[0],
                               section.size_label_pos[1],
                              'start',
                              'hanging',
                               True)

    def _make_address(self, dwg, section):
        return self._make_text(dwg,
                               hex(section.address),
                               section.addr_label_pos_x,
                               section.addr_label_pos_y,
                              'start')

    def _make_section(self, group, dwg, section, diagram):

        group.add(self._make_box(dwg, section, diagram))
        if section.size_y > 20:
            group.add(self._make_name(dwg, section))
            group.add(self._make_address(dwg, section))
            group.add(self._make_size_label(dwg, section))
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

    def _make_poly(self, dwg, diagram, start_address, end_address):

        points = []
        reversed = self._get_points_for_address(end_address, diagram)
        reversed.reverse()
        points.extend(self._get_points_for_address(start_address, diagram))
        points.extend(reversed)

        return dwg.polyline(points,
                            stroke='darkgrey',
                            fill='lightgrey')

    def _make_links(self, address, dwg: Drawing):
        hlines = dwg.g(id='hlines', stroke='grey')

        for diagram in self.diagrams[1:]:
            if not diagram.has_address(address) and not self.force:
                continue

            def _make_line(dwg, x1, y1, x2, y2):
                return dwg.line(start=(x1, y1), end=(x2, y2),
                                stroke_width=self.style.link_stroke_width,
                                stroke=self.style.link_stroke_color)

            points = self._get_points_for_address(address, diagram)

            hlines.add(_make_line(dwg,
                                  x1=points[0][0], y1=points[0][1],
                                  x2=points[1][0], y2=points[1][1]))

            hlines.add(_make_line(dwg,
                                  x1=points[1][0], y1=points[1][1],
                                  x2=points[2][0], y2=points[2][1]))

            hlines.add(_make_line(dwg,
                                  x1=points[2][0], y1=points[2][1],
                                  x2=points[3][0], y2=points[3][1]))
        return hlines
