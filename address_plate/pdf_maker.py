import cairo
import io
from math import sin, cos, radians
from reportlab.pdfgen import canvas
from reportlab.lib.colors import PCMYKColor
import textwrap
import pathlib
import sys

from .regex_objs import house_number_re_tuple, house_number_arrow_re_tuple
from .pdf_utils import create_cairo_font_face_for_file

COLOR_WHITE = PCMYKColor(0, 0, 0, 0)
COLOR_DARK_BLUE = PCMYKColor(75, 65, 0, 75)
# пока будет так, если цвета не подойдут поменяю

REGULAR = 'regular'
SEMI_BOLD = 'semi-bold'
BOLD = 'bold'

THIN = 'thin'
WIDE = 'wide'

LVL1 = 'lvl1'  # (основной)
SLASH = 'lvl2_slash'
LVL2C = 'lvl2c'  # (литера)
LVL2S = 'lvl2s'  # (номер после дроби)
LVL3 = 'lvl3'  # (Літера номеру після дробу)
LVL_A1 = 'lvl_a1'
LVL_A2C = 'lvl_a2c'

ARROW_NO = 0b0
ARROW_LEFT = 0b10
ARROW_RIGHT = 0b01
ARROW_BOTH = ARROW_LEFT | ARROW_RIGHT


def pt(mm: float) -> float:
    """ mm to pt

    :param mm:
    :return:
    """
    return mm*2.834645669  # 72/25.4


current_file_path = pathlib.Path(__file__).parent.absolute()
FONT_FILES = {
    # 'regular': 'address_plate/fonts/probanav2-regular-webfont.ttf',
    # 'semi-bold': 'address_plate/fonts/probanav2-semibold-webfont.ttf',
    # 'bold': 'address_plate/fonts/probanav2-bold-webfont.ttf',
    'regular': str(current_file_path.joinpath('fonts', 'probanav2-regular-webfont.ttf')),
    'semi-bold': str(current_file_path.joinpath('fonts', 'probanav2-semibold-webfont.ttf')),
    'bold': str(current_file_path.joinpath('fonts', 'probanav2-bold-webfont.ttf')),
}

FONT_FACE = {
    'regular': create_cairo_font_face_for_file(FONT_FILES['regular'], faceindex=0),
    'semi-bold': create_cairo_font_face_for_file(FONT_FILES['semi-bold'], faceindex=0),
    'bold': create_cairo_font_face_for_file(FONT_FILES['bold'], faceindex=0),
}

SIZES_PT = {
    # маленькие заначения ограничивают длину строки (3360mm ~ 50 больших символов
    'abstract_width': pt(3360),
    'abstract_height': pt(720),

    'thin_round_radius': pt(15.0),
    'wide_round_radius': pt(22.5),

    'thin_margin': pt(40),
    'thin_height': pt(215),

    'wide_margin': pt(60),
    'wide_height': pt(320),

    'thin_street_type_font': {'face': 'regular', 'size': 90.0},
    'thin_street_type_bl': pt(215-173),
    'thin_street_name_font': {'face': 'semi-bold', 'size': 220.0},
    'thin_street_name_bl': pt(215-94),
    'thin_street_line_width': 4.0,
    'thin_street_line_bl': pt(215-62),
    'thin_street_translit_font': {'face': 'regular', 'size': 90.0},
    'thin_street_translit_bl': pt(215-24),

    'wide_street_type_font': {'face': 'regular', 'size': 135.0},
    'wide_street_type_bl': pt(320-260),
    'wide_street_name_font': {'face': 'semi-bold', 'size': 330.0},
    'wide_street_name_bl': pt(320-140),
    'wide_street_line_width': 6.0,
    'wide_street_line_bl': pt(320-92),
    'wide_street_translit_font': {'face': 'regular', 'size': 135.0},
    'wide_street_translit_bl': pt(320-36),

    'thin_house_number_width': (pt(215), pt(280), pt(380), pt(440), pt(520)),
    'thin_house_number_bl': pt(215-50),
    'thin_house_number_font_lvl1': {'face': 'semi-bold', 'size': 480.0},
    'thin_house_number_font_lvl2c': {'face': 'bold', 'size': 300.0},
    'thin_house_number_font_lvl2s': {'face': 'semi-bold', 'size': 300.0},
    'thin_house_number_font_lvl3': {'face': 'semi-bold', 'size': 220.0},
    'thin_house_number_slash_size': (pt(12), 75, pt(80), pt(6)),

    'wide_house_number_width': (pt(320), pt(420), pt(565), pt(640), pt(720)),
    'wide_house_number_bl': pt(320-75),
    'wide_house_number_font_lvl1': {'face': 'semi-bold', 'size': 720.0},
    'wide_house_number_font_lvl2c': {'face': 'bold', 'size': 450.0},
    'wide_house_number_font_lvl2s': {'face': 'bold', 'size': 450.0},
    'wide_house_number_font_lvl3': {'face': 'bold', 'size': 330.0},
    'wide_house_number_slash_size': (pt(20), 75, pt(125), pt(9)),

    'thin_house_number_arrow_width': (pt(215), pt(215), pt(280), pt(340), pt(440)),
    'thin_house_number_arrow_bl': pt(215 - 90),
    'thin_house_number_arrow_font_lvl1': {'face': 'semi-bold', 'size': 380.0},
    'thin_house_number_arrow_font_lvl2c': {'face': 'bold', 'size': 240.0},
    'thin_house_number_arrow_font_lvl2s': {'face': 'bold', 'size': 240.0},
    'thin_house_number_arrow_font_lvl3': {'face': 'semi-bold', 'size': 140.0},
    'thin_house_number_arrow_slash_size': (pt(10), 75, pt(65), pt(5)),
    'thin_house_number_arrow_arrow_bl': pt(215-62),
    'thin_house_number_arrow_arrow_size': {'line_width': 4, 'length': pt(9.8),
                                           'half_height': pt(8.5/2), 'half_space': pt(15/2)},
    'thin_house_number_arrow_number_bl': pt(215-24),
    'thin_house_number_arrow_number_font_lvl_a1': {'face': 'regular', 'size': 90},
    'thin_house_number_arrow_number_font_lvl_a2c': {'face': 'semi-bold', 'size': 50},

    'wide_house_number_arrow_width': (pt(320), pt(320), pt(420), pt(510), pt(660)),
    'wide_house_number_arrow_bl': pt(320 - 135),
    'wide_house_number_arrow_font_lvl1': {'face': 'semi-bold', 'size': 570.0},
    'wide_house_number_arrow_font_lvl2c': {'face': 'bold', 'size': 330.0},
    'wide_house_number_arrow_font_lvl2s': {'face': 'bold', 'size': 330.0},
    'wide_house_number_arrow_font_lvl3': {'face': 'bold', 'size': 210.0},
    'wide_house_number_arrow_slash_size': (pt(12), 75, pt(98), pt(7.5)),
    'wide_house_number_arrow_arrow_bl': pt(320-94),
    'wide_house_number_arrow_arrow_size': {'line_width': 6, 'length': pt(18.8),
                                           'half_height': pt(14.8/2), 'half_space': pt(22.5/2)},
    'wide_house_number_arrow_number_bl': pt(320-37),
    'wide_house_number_arrow_number_font_lvl_a1': {'face': 'regular', 'size': 135},
    'wide_house_number_arrow_number_font_lvl_a2c': {'face': 'semi-bold', 'size': 75},

    'thin_vertical_width': pt(360),
    'thin_vertical_height': pt(480),
    'thin_vertical_margin': pt(36),
    'thin_vertical_street_type_font': {'face': 'regular', 'size': 65.0},
    'thin_vertical_street_type_bl': pt(36.0) + 32.625,
    'thin_vertical_street_name_font': {'face': 'semi-bold', 'size': 110.0, 'leading': 120.0},
    'thin_vertical_street_name_translate': pt(18) + 77.984375,
    'thin_vertical_street_line_width': pt(2.0),
    'thin_vertical_street_line_translate': pt(24.0),
    'thin_vertical_street_name_max_char': 15,
    'thin_vertical_street_translit_font': {'face': 'regular', 'size': 65.0, 'leading': 78.0},
    'thin_vertical_street_translit_translate': pt(24) + 32.625,
    'thin_vertical_street_translit_max_char': 30,
    'thin_vertical_house_number_bl': pt(480 - 48),
    'thin_vertical_house_number_font_lvl1': {'face': 'semi-bold', 'size': 540.0},
    'thin_vertical_house_number_font_lvl2c': {'face': 'bold', 'size': 312.0},
    'thin_vertical_house_number_font_lvl2s': {'face': 'bold', 'size': 312.0},
    'thin_vertical_house_number_font_lvl3': {'face': 'bold', 'size': 220.0},
    'thin_vertical_house_number_slash_size': (pt(12), 75, pt(80), pt(6)),

    'wide_vertical_width': pt(540),
    'wide_vertical_height': pt(720),
    'wide_vertical_margin': pt(54),
    'wide_vertical_street_type_font': {'face': 'regular', 'size': 100.0},
    'wide_vertical_street_type_bl': pt(54.0) + 50.203125,
    'wide_vertical_street_name_font': {'face': 'semi-bold', 'size': 165.0, 'leading': 180.0},
    'wide_vertical_street_name_translate': pt(18) + 116.984375,
    'wide_vertical_street_name_max_char': 15,
    'wide_vertical_street_line_width': pt(3.0),
    'wide_vertical_street_line_translate': pt(36.0),
    'wide_vertical_street_translit_font': {'face': 'regular', 'size': 100.0, 'leading': 120.0},
    'wide_vertical_street_translit_translate': pt(57.0),
    'wide_vertical_street_translit_max_char': 30,
    'wide_vertical_house_number_bl': pt(720 - 72),
    'wide_vertical_house_number_font_lvl1': {'face': 'semi-bold', 'size': 810.0},
    'wide_vertical_house_number_font_lvl2c': {'face': 'bold', 'size': 470.0},
    'wide_vertical_house_number_font_lvl2s': {'face': 'bold', 'size': 470.0},
    'wide_vertical_house_number_font_lvl3': {'face': 'bold', 'size': 330.0},
    'wide_vertical_house_number_slash_size': (pt(12), 75, pt(80), pt(6)),

}


def draw_background(work_canvas, width, height, radius):
    work_canvas.saveState()
    work_canvas.setFillColor(COLOR_DARK_BLUE)
    work_canvas.setStrokeColor(COLOR_DARK_BLUE)
    work_canvas.roundRect(0, 0, width, height, radius, stroke=0, fill=1)
    work_canvas.restoreState()


def draw_house_number_arrows(work_canvas: canvas.Canvas, width: float, margin: float, base_line: float,
                             size: dict, arrows: int):

    def draw_arrow(x: float, y: float, k: int):
        """ k= -1 or 1
        """
        p = work_canvas.beginPath()
        p.moveTo(x, y)
        p.lineTo(x + k * size['length'], y + size['half_height'])
        p.lineTo(x + k * size['length'], y - size['half_height'])
        p.close()
        work_canvas.drawPath(p, fill=1, stroke=0)

    work_canvas.saveState()
    work_canvas.setFillColor(COLOR_WHITE)
    work_canvas.setStrokeColor(COLOR_WHITE)
    work_canvas.setLineWidth(size['line_width'])

    if arrows & ARROW_LEFT:
        draw_arrow(margin, base_line, 1)
        work_canvas.line(margin + size['length'], base_line, width/2-size['half_space'], base_line)
    else:
        work_canvas.line(margin, base_line, width/2+size['half_space'], base_line)

    if arrows & ARROW_RIGHT:
        draw_arrow(width-margin, base_line, -1)
        work_canvas.line(width/2+size['half_space'], base_line, width - margin - size['length'], base_line)
    else:
        work_canvas.line(width/2-size['half_space'], base_line, width - margin, base_line)

    work_canvas.restoreState()


class TextPath:

    width = SIZES_PT['abstract_width']
    height = SIZES_PT['abstract_height']

    def __init__(self, text: str, font: dict):
        """текст в кривых начало в (0, 0)

        :param text:
        :param font:
        """
        self.text, self.font = text, font
        self._init_path()

    def _init_path(self):
        mem = io.BytesIO()
        surface = cairo.PDFSurface(mem, self.width, self.height)
        ctx = cairo.Context(surface)
        ctx.set_font_face(FONT_FACE[self.font['face']])
        ctx.set_font_size(self.font['size'])
        ctx.move_to(0, 0)
        ctx.text_path(self.text)
        self.path = ctx.copy_path()
        self.path_extents = ctx.path_extents()
        self.current_point = ctx.get_current_point()

    def draw(self, work_canvas: canvas.Canvas):
        if self.text and self.font:
            work_canvas.saveState()
            work_canvas.setFillColor(COLOR_WHITE)
            work_canvas.setStrokeColor(COLOR_WHITE)
            canvas_path = work_canvas.beginPath()
            for type_op, points in self.path:
                if type_op == cairo.PATH_MOVE_TO:
                    x, y = points
                    canvas_path.moveTo(x, y)

                elif type_op == cairo.PATH_LINE_TO:
                    x, y = points
                    canvas_path.lineTo(x, y)

                elif type_op == cairo.PATH_CURVE_TO:
                    x1, y1, x2, y2, x3, y3 = points
                    canvas_path.curveTo(x1, y1, x2, y2, x3, y3)

                elif type_op == cairo.PATH_CLOSE_PATH:
                    canvas_path.close()

            work_canvas.drawPath(canvas_path, fill=1, stroke=0)
            work_canvas.restoreState()

    def get_path_extents(self):
        """
        x1: left of the resulting extents
        y1: top of the resulting extents
        x2: right of the resulting extents
        y2: bottom of the resulting extents

        :return: (x1, y1, x2, y2), all float
        """
        return self.path_extents

    def get_current_point(self):
        """

        :return: (x, y), both float
        """
        return self.current_point


class Slash:

    def __init__(self, size):
        self.margin, self.angle, self.length, self.line_width = size
        self.line = (
            self.margin,
            0,
            self.margin + self.length*cos(radians(self.angle)),
            - self.length * sin(radians(self.angle))
        )

    def get_path_extents(self):
        return 0, 0, self.line[2] + self.margin, self.line[3]

    def get_current_point(self):
        return self.line[2] + self.margin, 0

    def draw(self, work_canvas):
        work_canvas.saveState()
        work_canvas.setStrokeColor(COLOR_WHITE)
        work_canvas.setFillColor(COLOR_WHITE)
        work_canvas.setLineWidth(self.line_width)
        work_canvas.line(*self.line)
        work_canvas.restoreState()


def parse_house_number(house_num_str, regex_tuple):

    for r in regex_tuple:
        match_res = r.match(house_num_str)
        if match_res:
            return match_res.groupdict()
    return None


def house_number_pdf(house_num: str = None, left_num: str = None, right_num: str = None, wide: str = THIN):

    arrows = (ARROW_LEFT if left_num else ARROW_NO) | (ARROW_RIGHT if right_num else ARROW_NO)
    arrow = '_arrow' if arrows else ''

    width = SIZES_PT[f'{wide}_house_number{arrow}_width'][min(len(house_num)-1, 4)]
    height = SIZES_PT[f'{wide}_height']
    margin = SIZES_PT[f'{wide}_margin']

    pdf = io.BytesIO()
    work_canvas = canvas.Canvas(pdf, (width, height), bottomup=0)

    draw_background(work_canvas, width, height, SIZES_PT[f'{wide}_round_radius'])

    house_number_dict = parse_house_number(house_num, house_number_re_tuple)

    paths = {}
    after_slash = False
    house_number_width = 0
    for key in sorted(house_number_dict.keys()):
        if key != SLASH:
            if house_number_dict[key]:
                temp_text_path = TextPath(house_number_dict[key], SIZES_PT[f'{wide}_house_number{arrow}_font_{key}'])
                paths.update({key: temp_text_path})
                if after_slash:
                    house_number_width += temp_text_path.get_current_point()[0] - temp_text_path.get_path_extents()[0]
                    after_slash = False
                else:
                    house_number_width += temp_text_path.get_current_point()[0]
        else:
            temp_slash = Slash(SIZES_PT[f'{wide}_house_number{arrow}_slash_size'])
            paths.update({key: temp_slash})
            after_slash = True
            house_number_width += temp_slash.get_current_point()[0]

    work_canvas.saveState()
    work_canvas.translate(SIZES_PT[f'{wide}_margin'], SIZES_PT[f'{wide}_house_number{arrow}_bl'])
    translate_x = (width - house_number_width - SIZES_PT[f'{wide}_margin']*2)/2
    if translate_x >= 0:
        work_canvas.translate(translate_x, 0)
    else:
        scale = (width - SIZES_PT[f'{wide}_margin']*2)/house_number_width
        work_canvas.translate(SIZES_PT[f'{wide}_margin']*(1-scale), 0)
        work_canvas.scale(scale, scale)

    after_slash = False
    for key in sorted(paths):
        if after_slash:
            work_canvas.translate(-paths[key].get_path_extents()[0], 0)
            after_slash = False
        paths[key].draw(work_canvas)
        work_canvas.translate(paths[key].get_current_point()[0], 0)
        if key == SLASH:
            after_slash = True

    work_canvas.restoreState()

    if arrows:
        draw_house_number_arrows(work_canvas, width, margin, SIZES_PT[f'{wide}_house_number{arrow}_arrow_bl'],
                                 SIZES_PT[f'{wide}_house_number{arrow}_arrow_size'], arrows)

        if left_num:
            work_canvas.saveState()
            left_num_dict = parse_house_number(left_num, house_number_arrow_re_tuple)
            lvl_a1_path = TextPath(left_num_dict[LVL_A1], SIZES_PT[f'{wide}_house_number_arrow_number_font_{LVL_A1}'])
            work_canvas.translate(margin, SIZES_PT[f'{wide}_house_number_arrow_number_bl'])
            lvl_a1_path.draw(work_canvas)
            if left_num_dict[LVL_A2C]:
                lvl_a2c_path = TextPath(left_num_dict[LVL_A2C],
                                        SIZES_PT[f'{wide}_house_number_arrow_number_font_{LVL_A2C}'])
                work_canvas.translate(lvl_a1_path.get_current_point()[0], 0)
                lvl_a2c_path.draw(work_canvas)
            work_canvas.restoreState()

        if right_num:
            right_num_dict = parse_house_number(right_num, house_number_arrow_re_tuple)
            work_canvas.saveState()
            work_canvas.translate(width - margin, SIZES_PT[f'{wide}_house_number_arrow_number_bl'])
            if right_num_dict[LVL_A2C]:
                lvl_a2c_path = TextPath(right_num_dict[LVL_A2C],
                                        SIZES_PT[f'{wide}_house_number_arrow_number_font_{LVL_A2C}'])
                work_canvas.translate(-lvl_a2c_path.get_current_point()[0], 0)
                lvl_a2c_path.draw(work_canvas)
            lvl_a1_path = TextPath(right_num_dict[LVL_A1],
                                   SIZES_PT[f'{wide}_house_number_arrow_number_font_{LVL_A1}'])
            work_canvas.translate(-lvl_a1_path.get_current_point()[0], 0)
            lvl_a1_path.draw(work_canvas)
            work_canvas.restoreState()

    work_canvas.showPage()
    work_canvas.save()
    pdf.seek(0)

    file_name = f"{house_num.replace('/', '_')}.pdf"

    return pdf, file_name


def thin_house_number_pdf(house_num: str = None, left_num: str = None, right_num: str = None):
    return house_number_pdf(house_num, left_num, right_num, THIN)


def wide_house_number_pdf(house_num: str = None, left_num: str = None, right_num: str = None):
    return house_number_pdf(house_num, left_num, right_num, WIDE)


def max_width_plus(text_path_list: list = None, margin: float = SIZES_PT[f'thin_margin']):
    """ берем максимальное значение, немного увеличиваем, делаем кратной margin и добавляем 2 margin

    """
    # print([(text_path.get_path_extents()[2]) for text_path in text_path_list])
    if text_path_list:
        return ((max([text_path.get_path_extents()[2] for text_path in text_path_list])+margin*0.7)//margin+3)*margin
    # return 100
    return None


def street_name_pdf(street_type: str = None, street_name: str = None, street_translit: str = None, wide: str = THIN):

    street_type_text_path = TextPath(text=street_type, font=SIZES_PT[f'{wide}_street_type_font'])
    street_name_text_path = TextPath(text=street_name, font=SIZES_PT[f'{wide}_street_name_font'])
    street_translit_text_path = TextPath(text=street_translit, font=SIZES_PT[f'{wide}_street_translit_font'])

    width = max_width_plus([street_name_text_path, street_type_text_path, street_translit_text_path],
                           SIZES_PT[f'{wide}_margin'])
    height = SIZES_PT[f'{wide}_height']
    margin = SIZES_PT[f'{wide}_margin']

    pdf = io.BytesIO()
    work_canvas = canvas.Canvas(pdf, (width, height), bottomup=0)

    draw_background(work_canvas, width, height, SIZES_PT[f'{wide}_round_radius'])

    work_canvas.saveState()
    work_canvas.setStrokeColor(COLOR_WHITE)
    work_canvas.setLineWidth(SIZES_PT[f'{wide}_street_line_width'])
    work_canvas.line(SIZES_PT[f'{wide}_margin'], SIZES_PT[f'{wide}_street_line_bl'],
                     width - SIZES_PT[f'{wide}_margin'], SIZES_PT[f'{wide}_street_line_bl'])
    work_canvas.restoreState()

    work_canvas.translate(margin, 0)

    work_canvas.saveState()
    work_canvas.translate(0, SIZES_PT[f'{wide}_street_type_bl'])
    street_type_text_path.draw(work_canvas)
    work_canvas.restoreState()

    work_canvas.saveState()
    work_canvas.translate(0, SIZES_PT[f'{wide}_street_name_bl'])
    street_name_text_path.draw(work_canvas)
    work_canvas.restoreState()

    work_canvas.saveState()
    work_canvas.translate(0, SIZES_PT[f'{wide}_street_translit_bl'])
    street_translit_text_path.draw(work_canvas)
    work_canvas.restoreState()

    work_canvas.showPage()
    work_canvas.save()
    pdf.seek(0)

    file_name = f"{street_type}_{street_name}.pdf"

    return pdf, file_name


def thin_street_name_pdf(street_type: str = None, street_name: str = None, street_translit: str = None):
    return street_name_pdf(street_type, street_name, street_translit, THIN)


def wide_street_name_pdf(street_type: str = None, street_name: str = None, street_translit: str = None):
    return street_name_pdf(street_type, street_name, street_translit, WIDE)




def vertical_pdf(street_type: str = None, street_name: str = None, street_translit: str = None,
                 house_num: str = None, wide: str = THIN):

    width = SIZES_PT[f'{wide}_vertical_width']
    height = SIZES_PT[f'{wide}_vertical_height']
    margin = SIZES_PT[f'{wide}_vertical_margin']

    pdf = io.BytesIO()
    work_canvas = canvas.Canvas(pdf, (width, height), bottomup=0)

    draw_background(work_canvas, width, height, SIZES_PT[f'{wide}_round_radius'])

    work_canvas.saveState()
    work_canvas.translate(margin, 0)

    street_type_text_path = TextPath(text=street_type, font=SIZES_PT[f'{wide}_vertical_street_type_font'])
    work_canvas.translate(0, SIZES_PT[f'{wide}_vertical_street_type_bl'])
    street_type_text_path.draw(work_canvas)

    street_name_text_path = TextPath(text=street_name, font=SIZES_PT[f'{wide}_vertical_street_name_font'])
    work_canvas.translate(0, SIZES_PT[f'{wide}_vertical_street_name_translate'])
    if street_name_text_path.get_path_extents()[2] < width - 2 * margin:
        street_name_text_path.draw(work_canvas)
    else:
        str_list = textwrap.wrap(street_name, width=SIZES_PT[f'{wide}_vertical_street_name_max_char'],
                                 break_long_words=False)

        str_path_list = [TextPath(text=s, font=SIZES_PT[f'{wide}_vertical_street_name_font']) for s in str_list]
        scale = min(1, (width - margin * 2) / max([path.get_path_extents()[2] for path in str_path_list]))
        work_canvas.scale(scale, scale)
        for path in str_path_list:
            path.draw(work_canvas)
            if path != str_path_list[-1]:
                work_canvas.translate(0, SIZES_PT[f'{wide}_vertical_street_name_font']['leading'])
        work_canvas.scale(1, 1)

    work_canvas.translate(0, SIZES_PT[f'{wide}_vertical_street_line_translate'])
    work_canvas.setLineWidth(SIZES_PT[f'{wide}_vertical_street_line_width'])
    work_canvas.setStrokeColor(COLOR_WHITE)
    work_canvas.line(0, 0, width - 2 * margin, 0)

    street_translit_text_path = TextPath(text=street_translit, font=SIZES_PT[f'{wide}_vertical_street_translit_font'])
    work_canvas.translate(0, SIZES_PT[f'{wide}_vertical_street_translit_translate'])
    if street_translit_text_path.get_path_extents()[2] < width - 2 * margin:
        street_translit_text_path.draw(work_canvas)
    else:
        str_list = textwrap.wrap(street_translit, width=SIZES_PT[f'{wide}_vertical_street_translit_max_char'],
                                 break_long_words=False)

        str_path_list = [TextPath(text=s, font=SIZES_PT[f'{wide}_vertical_street_translit_font']) for s in str_list]
        scale = min(1, (width - margin * 2) / max([path.get_path_extents()[2] for path in str_path_list]))
        work_canvas.scale(scale, scale)
        for path in str_path_list:
            path.draw(work_canvas)
            if path != str_path_list[-1]:
                work_canvas.translate(0, SIZES_PT[f'{wide}_vertical_street_translit_font']['leading'])
        work_canvas.scale(1, 1)

    work_canvas.restoreState()

    # =========================================================================================
    house_number_dict = parse_house_number(house_num, house_number_re_tuple)

    paths = {}
    after_slash = False
    house_number_width = 0
    for key in sorted(house_number_dict.keys()):
        if key != SLASH:
            if house_number_dict[key]:
                temp_text_path = TextPath(house_number_dict[key], SIZES_PT[f'{wide}_vertical_house_number_font_{key}'])
                paths.update({key: temp_text_path})
                if after_slash:
                    house_number_width += temp_text_path.get_current_point()[0] - temp_text_path.get_path_extents()[0]
                    after_slash = False
                else:
                    house_number_width += temp_text_path.get_current_point()[0]
        else:
            temp_slash = Slash(SIZES_PT[f'{wide}_vertical_house_number_slash_size'])
            paths.update({key: temp_slash})
            after_slash = True
            house_number_width += temp_slash.get_current_point()[0]

    work_canvas.saveState()
    work_canvas.translate(SIZES_PT[f'{wide}_margin'], SIZES_PT[f'{wide}_vertical_house_number_bl'])
    if house_number_width > width - margin * 2:
        scale = (width - margin * 2) / house_number_width
        work_canvas.scale(scale, scale)

    after_slash = False
    for key in sorted(paths):
        if after_slash:
            work_canvas.translate(-paths[key].get_path_extents()[0], 0)
            after_slash = False
        paths[key].draw(work_canvas)
        work_canvas.translate(paths[key].get_current_point()[0], 0)
        if key == SLASH:
            after_slash = True

    work_canvas.restoreState()

    # =========================================================================================

    work_canvas.showPage()
    work_canvas.save()
    pdf.seek(0)

    file_name = f"{street_type}_{street_name}.pdf"

    return pdf, file_name


def thin_vertical_pdf(street_type: str = None, street_name: str = None, street_translit: str = None,
                      house_num: str = None):
    return vertical_pdf(street_type, street_name, street_translit,house_num, THIN)


def wide_vertical_pdf(street_type: str = None, street_name: str = None, street_translit: str = None,
                      house_num: str = None):
    return vertical_pdf(street_type, street_name, street_translit,house_num, WIDE)
