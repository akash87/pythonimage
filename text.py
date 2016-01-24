from enum import Enum
from itertools import groupby
import textwrap
from PIL import ImageFont, Image
from PIL.ImageDraw import ImageDraw


class Type(Enum):
    default = 'default'
    east = 'east'
    west = 'west'


class Style(Enum):
    normal = 'normal'
    h1 = 'h1'
    h2 = 'h2'
    h3 = 'h3'


class XLocation(Enum):
    center = 'center'
    left = 'left'
    right = 'right'


class YLocation(Enum):
    center = 'center'
    top = 'top'
    bottom = 'bottom'


def get_symbol_size(font):
    return font.getsize('A')


class Text(object):
    """Text representation"""

    # noinspection PyShadowingBuiltins
    def __init__(self, index, value, keywords, type, style, xloc=None, yloc=None, points=None,
                 fgcolor=None, bgcolor=None, bgopacity=1.0):
        """
        :type index: int
        :type value: str
        :type keywords: list[str]
        :type type: Type
        :type style: Style
        :type xloc: XLocation
        :type yloc: YLocation
        :type points: list[tuple(3)]
        """
        super(Text, self).__init__()
        self.__index = index
        self.__value = value
        self.__keywords = keywords
        self.__type = type
        self.__style = style
        self.__xloc = xloc
        self.__yloc = yloc
        self.__boWidth = 2
        self.__boColor = (255, 255, 255)
        self.__fgcolor = fgcolor or (255, 255, 255)
        self.__bgcolor = bgcolor or (0, 0, 0)
        self.__bgOpacity = bgopacity
        self.__points = points

    @property
    def fgcolor(self):
        return self.__fgcolor

    @property
    def bgcolor(self):
        return self.__bgcolor

    @property
    def bgopacity(self):
        return self.__bgOpacity

    @property
    def type(self):
        """
        :rtype: Type
        """
        return self.__type

    @property
    def value(self):
        return self.__value

    @property
    def index(self):
        return self.__index

    @property
    def keywords(self):
        return self.__keywords

    @property
    def style(self):
        return self.__style

    @property
    def xloc(self):
        return self.__xloc

    @property
    def yloc(self):
        return self.__yloc

    @property
    def bowidth(self):
        return self.__boWidth

    @bowidth.setter
    def bowidth(self, width=2):
        """
        Set the outline width in pixels

        :type width: int
        """

        self.__boWidth = width

    @property
    def bocolor(self):
        return self.__boColor

    @bocolor.setter
    def bocolor(self, color=None):
        if not isinstance(color, tuple):
            raise Exception("color should be tuple")

        if len(color) not in (3, 4):
            raise Exception("color should be defined as 3")

        color = color if color else (0, 0, 0)
        self.__boColor = color

    def __str__(self):
        return str.format('Type: {0}, xloc: {1}, yloc: {2}, value: {3}', self.type, self.xloc, self.yloc, self.value)


class Page(object):
    """docstring for Page"""

    def __init__(self, idx, width, height):
        super(Page, self).__init__()
        self.__id = idx
        self.__width = width
        self.__height = height

        self.__texts = []
        self.__image = None
        self.__bgimage = None
        self.__draw = None
        self.__filename = None

        self.__styles = {
            Style.normal: StyleInfo(10, 12, 'regular'),
            Style.h1: StyleInfo(30, 32, 'regular'),
            Style.h2: StyleInfo(24, 26, 'regular'),
            Style.h3: StyleInfo(20, 22, 'regular'),
        }

    # noinspection PyPep8Naming
    def generateTextImage(self, texts, imagefile):
        """

        :param texts:
        :param imagefile:
        :type texts: list[Text]
        :type imagefile: str
        :return:
        """
        self.__filename = imagefile
        self.__texts = texts

        self.__draw_image()

    def __draw_image(self):
        self.__image = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))
        self.__bgimage = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))
        self.__draw = ImageDraw2(self.__image, mode="RGBA")
        self.__bgdraw = ImageDraw2(self.__bgimage, mode="RGBA")

        for key, group in groupby(self.__texts, lambda x: [x.type, x.xloc, x.yloc]):
            group = list(sorted(group, key=lambda x: x.index))

            if key[0] == Type.default:
                self.__draw_bottom(group)
            else:
                self.__draw_side_group(key, group)

        width = self.__width / 2
        height = self.__height
        xy = [width - 1, 0, width - 1, height]

        self.__draw.line(xy, fill=(0, 0, 0), width=2)

        # self.__bgimage.paste(self.__image, (0, 0), self.__image)
        # self.__image.save(self.__filename, format='png')

        result = Image.alpha_composite(self.__bgimage, self.__image)
        result.save(self.__filename, format='png')

    def __draw_side_group(self, key, group):
        if len(group) == 0:
            return

        type = key[0]
        xloc = key[1]
        yloc = key[2]

        width = self.__width

        if xloc == XLocation.left:
            x = width * 0.05 if type == Type.west else width * 0.55
            align = "left"
        elif xloc == XLocation.center:
            x = width / 4 if type == Type.west else width * 3 / 4
            align = "center"
        else:
            x = width * 0.45 if type == Type.west else width * 0.95
            align = "right"

        box_width = width * 0.3
        y = self.__calc_y_top(yloc, group)
        x_min = x
        x_max = 0
        y_min = y

        for t in group:
            style = self.__styles[t.style]
            line_height = style.line_height
            font = ImageFont.truetype(style.font_face, size=style.font_size)
            symbol_size = self.__draw.textsize('A', font=font)[1]
            spacing = line_height - symbol_size

            split = self.__draw.split_text_to_multiline(t.value, font, box_width, spacing)
            bbox = self.__draw.multiline_text((x, y), split.text, fill=t.fgcolor, font=font, align=align)

            x_min = min(x_min, bbox[0])
            x_max = max(x_max, bbox[2])

            y += split.size[1] + spacing

        self.__bgdraw.rectangle([x_min, y_min, x_max, y], fill=group[0].bgcolor)

    def __calc_y_top(self, yloc, group):
        height = self.__height
        width = self.__width * 0.3

        if yloc == YLocation.top:
            return height * 0.05

        if yloc == YLocation.center:
            y = height / 2
        else:
            y = height * 0.95

        for t in group:
            style = self.__styles[t.style]
            line_height = style.line_height
            font = ImageFont.truetype(style.font_face, size=style.font_size)
            symbol_size = self.__draw.textsize('A', font=font)[1]
            spacing = line_height - symbol_size
            split = self.__draw.split_text_to_multiline(t.value, font, width, spacing)
            size = split.size

            if yloc == YLocation.center:
                y -= size[1] / 2
            else:
                y -= size[1]

        return y

    def __draw_bottom(self, group):
        y = self.__height

        for t in group:
            style = self.__styles[t.style]
            font = ImageFont.truetype(style.font_face, size=style.font_size)
            symbol_size = get_symbol_size(font)
            spacing = style.line_height - symbol_size[1]

            text = t.value
            result = self.__draw.split_text_to_multiline(text, font, self.__width, spacing)

            y -= result.size[1]
            y -= symbol_size[1]

        y_min = y

        for t in group:
            style = self.__styles[t.style]
            font = ImageFont.truetype(style.font_face, size=style.font_size)
            symbol_size = get_symbol_size(font)
            spacing = style.line_height - symbol_size[1]
            text = t.value

            result = self.__draw.split_text_to_multiline(text, font, self.__width, spacing)

            self.__draw.multiline_text((symbol_size[0] * 2, y), text, fill=t.fgcolor, font=font)
            y += result.size[1]
            y += symbol_size[1]

        self.__bgdraw.rectangle([0, y_min, self.__width, self.__height], fill=group[0].bgcolor)

    def set_font_style(self, style, font_size, line_height, font_weight):
        """

        :type style: Style
        :type font_size: int
        :type line_height: int
        :type font_weight: int
        """
        self.__styles[style] = StyleInfo(font_size, line_height, font_weight)


class SplitResult(object):
    def __init__(self, text, size):
        self.text = text
        self.size = size

    def __str__(self):
        return str.format("Size={0} Text={1}", self.size, self.text)


class StyleInfo(object):
    def __init__(self, font_size, line_height, font_weight):
        self.font_size = font_size
        self.line_height = line_height
        self.font_weight = font_weight
        self.font_face = "arial.ttf"

    def __str__(self):
        return str.format("FS={0} LH={1} FW={2}", self.font_size, self.line_height, self.font_weight)


class ImageDraw2(ImageDraw):
    def multiline_text(self, xy, text, fill=None, font=None, anchor=None,
                       spacing=4, align="left"):
        widths = []
        max_width = 0
        lines = self._multiline_split(text)
        line_spacing = self.textsize('A', font=font)[1] + spacing

        for line in lines:
            line_width, line_height = self.textsize(line, font)
            widths.append(line_width)
            max_width = max(max_width, line_width)

        if align == "center":
            x = xy[0] - max_width / 2.0
            y = xy[1]
            xy = [x, y]
        elif align == "right":
            x = xy[0] - max_width
            y = xy[1]
            xy = [x, y]

        left, top = xy
        top_initial = top

        for idx, line in enumerate(lines):
            if align == "left":
                pass  # left = x
            elif align == "center":
                left += (max_width - widths[idx]) / 2.0
            elif align == "right":
                left += (max_width - widths[idx])
            else:
                assert False, 'align must be "left", "center" or "right"'
            self.text((left, top), line, fill, font, anchor)
            top += line_spacing
            left = xy[0]

        return [left, top_initial, left + max_width, top]

    def split_text_to_multiline(self, text, font, width, spacing):
        """
        :type text: str
        :type font: ImageFont
        :type width: int
        :type spacing: int
        """
        size = self.textsize(text, font)
        if size[0] < width:
            return SplitResult(text, size)

        text.rsplit()

        symbol_size = self.textsize('A', font=font)
        symbol_width = symbol_size[0]
        max_symbols_in_line = width / symbol_width

        text = textwrap.fill(text, width=max_symbols_in_line)
        size = self.multiline_textsize(text, font, spacing)

        return SplitResult(text, size)


if __name__ == '__main__':
    p = Page(0, 400, 400)
    style_ = Style.normal
    text_ = "The quick brown fox jumps over the lazy dog"
    bgcolor = (253, 120, 120, 70)

    t1 = Text(0, text_, [], Type.default, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t2 = Text(1, text_, [], Type.east, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)
    t3 = Text(2, text_, [], Type.east, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)

    t4 = Text(3, text_, [], Type.west, style_,
              XLocation.right, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t5 = Text(4, text_, [], Type.west, style_,
              XLocation.right, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    p.generateTextImage([t1, t2, t3, t4, t5], '1.png')

    # text_ = "small text"
    t1 = Text(0, text_, [], Type.default, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)
    t2 = Text(0, text_, [], Type.default, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)

    t3 = Text(1, text_, [], Type.east, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t4 = Text(2, text_, [], Type.east, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t5 = Text(3, text_, [], Type.east, style_,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t6 = Text(4, text_, [], Type.east, style_,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t5 = Text(3, text_, [], Type.east, style_,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t6 = Text(4, text_, [], Type.east, style_,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t7 = Text(3, text_, [], Type.east, style_,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t8 = Text(4, text_, [], Type.east, style_,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    p.generateTextImage([t1, t2, t3, t4, t5, t6, t7, t8], '2.png')

    t3 = Text(1, text_, [], Type.west, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t4 = Text(2, text_, [], Type.west, style_,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t5 = Text(3, text_, [], Type.west, style_,
              XLocation.left, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t6 = Text(4, text_, [], Type.west, style_,
              XLocation.left, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t7 = Text(3, text_, [], Type.west, style_,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 255), bgcolor=bgcolor)
    t8 = Text(4, text_, [], Type.west, style_,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 255), bgcolor=bgcolor)

    t9 = Text(3, text_, [], Type.west, style_,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t1 = Text(4, text_, [], Type.west, style_,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)

    p.generateTextImage([t3, t4, t5, t6, t7, t8, t9, t1], '3.png')

    t1 = Text(3, text_, [], Type.west, style_,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t2 = Text(4, text_, [], Type.west, style_,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)

    t3 = Text(3, text_, [], Type.east, style_,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t4 = Text(4, text_, [], Type.east, style_,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t5 = Text(5, text_, [], Type.east, style_,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)

    p.generateTextImage([t1, t2, t3, t4, t5], '4.png')
