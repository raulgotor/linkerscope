import svgwrite
from svgwrite import Drawing


class Style:
    box_fill_color: str
    box_stroke_color: str
    box_stroke_weight: int
    link_stroke_weight: int
    link_stroke_color: str
    label_font: str
    label_color: int
    label_size: int
    area_fill_color: int

class Map:
    dwg: Drawing
    area_width: 200
    pointer_y: int

    def __init__(self, main_diagram, magnified_diagram=[], addresses=[], force=False):
        self.type = type
        self.main_diagram = main_diagram
        self.magnified_diagram = magnified_diagram
        self.addresses = addresses
        self.force = force
        self.style = Style()
        self.style.box_fill_color='#CCE5FF'
        self.style.label_color='blue'
        self.style.box_stroke_color='#3399FF'
        self.style.box_stroke_weight=2
        self.style.link_stroke_weight=1
        self.style.link_stroke_color='grey'
        self.style.label_font="Courier New",
        self.style.label_size='16px'
        self.style.area_fill_color='#CCCCFF'

    def draw_maps(self, file):
        dwg = svgwrite.Drawing(file,
                               profile='full',
                               size=('200%', '200%')
                               )
        group3 = dwg.add(dwg.g())
        for address in self.addresses:
            group3.add(self.make_expand_lines(address, dwg))

        def draw_map(diagram):
            group = dwg.add(dwg.g())
            group.add(self.make_main_frame(dwg, diagram))
            for section in diagram.sections:
                self.make_section(group, dwg, section, diagram)
                pass
            group.translate(diagram.pos_x,
                            diagram.pos_y)

        draw_map(self.main_diagram)

        for diagram in self.magnified_diagram:
            draw_map(diagram)



        dwg.save()

    def make_main_frame(self, dwg, diagram):
        size_x = diagram.size_x
        size_y = diagram.size_y
        rectangle = dwg.rect((0, 0), (size_x, size_y))
        rectangle.fill(self.style.area_fill_color)
        rectangle.stroke(self.style.area_fill_color, width=1)
        return rectangle

    def make_box(self, dwg, section, diagram):
        section.size_x = diagram.size_x
        section.size_y = diagram.to_pixels(section.size)
        section.pos_y = diagram.to_pixels(diagram.end_address - section.size - section.address)
        section.pos_x = 0
        print('dh', hex(diagram.highest_memory))
        rectangle = dwg.rect((section.pos_x, section.pos_y), (section.size_x, section.size_y))
        rectangle.fill(self.style.box_fill_color)
        rectangle.stroke(self.style.box_stroke_color, width=self.style.link_stroke_weight)
        return rectangle

    def make_text(self, dwg, text, pos_x, pos_y, anchor, baseline='middle',small=False):
        return dwg.text(text, insert=(pos_x, pos_y),
                        stroke=self.style.label_color,
                        #focusable='true',
                        fill=self.style.label_color,
                        stroke_width=0,
                        font_size='12px' if small else self.style.label_size,
                        font_weight="normal",
                        font_family="Courier New",
                        text_anchor=anchor,
                        alignment_baseline=baseline
                        )

    def make_name(self, dwg, section):
        return self.make_text(dwg,
                              section.name,
                              section.name_label_pos_x,
                              section.name_label_pos_y,
                              'middle')

    def make_size_label(self, dwg, section):
        return self.make_text(dwg,
                              hex(section.size),
                              section.size_label_pos[0],
                              section.size_label_pos[1],
                              'start',
                              'hanging',
                              True)

    def make_address(self, dwg, section):
        return self.make_text(dwg,
                              hex(section.address),
                              section.addr_label_pos_x,
                              section.addr_label_pos_y,
                              'start')

    def make_section(self, group, dwg, section, diagram):

        group.add(self.make_box(dwg, section, diagram))
        if section.size_y > 20:
            group.add(self.make_name(dwg, section))
            group.add(self.make_address(dwg, section))
            group.add(self.make_size_label(dwg, section))
        return group

    def make_expand_lines(self, address, dwg: Drawing):
        hlines = dwg.g(id='hlines', stroke='grey')

        for diagram in self.magnified_diagram:
            if not diagram.has_address(address) and not self.force:
                continue

            left_block_view = self.main_diagram
            right_block_view = diagram

            left_block_x = self.main_diagram.size_x + self.main_diagram.pos_x
            left_block_x2 = left_block_x + 30
            left_block_y = left_block_view.pos_y + left_block_view.to_pixels_relative(address)

            right_block_x = diagram.pos_x
            right_block_x2 = right_block_x - 30
            right_block_y = right_block_view.pos_y + right_block_view.to_pixels_relative(address)

            print(left_block_y, right_block_y)
            #0 and syze_y ok

            hlines.add(dwg.line(start=(left_block_x, left_block_y),
                                end=(left_block_x2, left_block_y)))

            hlines.add(dwg.line(start=(right_block_x2, right_block_y),
                                end=(right_block_x, right_block_y)))

            hlines.add(dwg.line(start=(left_block_x2, left_block_y),
                                end=(right_block_x2, right_block_y)))

        return hlines