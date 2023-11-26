import copy
import svgwrite
from svgwrite import Drawing
from style import Style


class Map:
    dwg: Drawing
    pointer_y: int

    def __init__(self, diagrams=[], links={}, **kwargs):
        self.style = kwargs.get('style')
        self.type = type
        self.diagrams = diagrams
        self.current_style = Style()
        _links = links.get('addresses')
        for section in self.diagrams[0].sections:
            if section.name in links.get('sections'):
                _links.append(section.address)
                _links.append(section.address + section.size)
        self.links = _links

    def draw_maps(self, file):

        def _draw_map(diagram):
            base_and_diagram_style = Style()
            base_and_diagram_style.extend_style(self.style)
            base_and_diagram_style.extend_style(diagram.style)
            group = dwg.add(dwg.g())
            group.add(self._make_main_frame(dwg, diagram))

            for section in diagram.sections:
                self._make_section(group, dwg, section, diagram, base_and_diagram_style)

            group.translate(diagram.pos_x,
                            diagram.pos_y)

        dwg = svgwrite.Drawing(file,
                               profile='full',
                               size=('200%', '200%')
                               )

        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill=self.style.background_color))

        lines_group = dwg.add(dwg.g())

        for address in self.links:
            lines_group.add(self._make_links(address, dwg))

        for diagram in self.diagrams:
            _draw_map(diagram)

        dwg.save()

    def _make_main_frame(self, dwg, diagram):
        size_x = diagram.size_x
        size_y = diagram.size_y
        rectangle = dwg.rect((0, 0), (size_x, size_y))
        rectangle.fill(self.style.map_background_color)
        rectangle.stroke(self.style.map_background_color, width=1)
        return rectangle

    def _make_box(self, dwg, section, diagram, style):
        section.size_x = diagram.size_x
        section.size_y = diagram.to_pixels(section.size)
        section.pos_y = diagram.to_pixels(diagram.end_address - section.size - section.address)
        section.pos_x = 0
        rectangle = dwg.rect((section.pos_x, section.pos_y), (section.size_x, section.size_y))
        rectangle.fill(style.section_fill_color)
        rectangle.stroke(style.section_stroke_color, width=style.section_stroke_width)
        return rectangle

    def _make_text(self, dwg, text, pos_x, pos_y, style, anchor, baseline='middle', small=False):
        return dwg.text(text, insert=(pos_x, pos_y),
                        stroke='white',
                        #focusable='true',
                        fill=style.label_color,
                        stroke_width=style.label_stroke_width,
                        font_size='12px' if small else style.label_size,
                        font_weight="normal",
                        font_family=style.label_font,
                        text_anchor=anchor,
                        alignment_baseline=baseline
                        )

    def _make_name(self, dwg, section, style):
        return self._make_text(dwg,
                               section.name,
                               section.name_label_pos_x,
                               section.name_label_pos_y,
                               style=style,
                               anchor='middle',
                               )

    def _make_size_label(self, dwg, section, style):
        return self._make_text(dwg,
                               hex(section.size),
                               section.size_label_pos[0],
                               section.size_label_pos[1],
                               style,
                               'start',
                               'hanging',
                               True,
                               )

    def _make_address(self, dwg, section, style):
        return self._make_text(dwg,
                               hex(section.address),
                               section.addr_label_pos_x,
                               section.addr_label_pos_y,
                               anchor='start',
                               style=style)

    def _make_section(self, group, dwg, section, diagram, style):
        custom_styles = getattr(style, 'regions', None)
        section_style = Style()
        section_style.extend_style(style)

        if custom_styles:
            for item in custom_styles:
                if section.name in item.get('regions'):
                    section_style.extend_style(Style(style=item))

        group.add(self._make_box(dwg, section, diagram, section_style))
        if section.size_y > 20:
            group.add(self._make_name(dwg, section, section_style))
            group.add(self._make_address(dwg, section, section_style))
            group.add(self._make_size_label(dwg, section, section_style))
        return group

    def _make_links(self, address, dwg: Drawing):
        hlines = dwg.g(id='hlines', stroke='grey')
        main_diagram = self.diagrams[0]

        for diagram in self.diagrams[1:]:
            if not diagram.has_address(address):
                continue

            left_block_view = main_diagram
            right_block_view = diagram

            left_block_x = main_diagram.size_x + main_diagram.pos_x
            left_block_x2 = left_block_x + 30
            left_block_y = left_block_view.pos_y + left_block_view.to_pixels_relative(address)

            right_block_x = diagram.pos_x
            right_block_x2 = right_block_x - 30
            right_block_y = right_block_view.pos_y + right_block_view.to_pixels_relative(address)

            def _make_line(dwg, x1, y1, x2, y2):
                return dwg.line(start=(x1, y1), end=(x2, y2),
                                stroke_width=self.style.link_stroke_width,
                                stroke=self.style.link_stroke_color)

            hlines.add(_make_line(dwg,
                                  x1=left_block_x, y1=left_block_y,
                                  x2=left_block_x2, y2=left_block_y))

            hlines.add(_make_line(dwg,
                                  x1=right_block_x2, y1=right_block_y,
                                  x2=right_block_x, y2=right_block_y))

            hlines.add(_make_line(dwg,
                                  x1=left_block_x2, y1=left_block_y,
                                  x2=right_block_x2, y2=right_block_y))

        return hlines
