from enum import Enum
from itertools import groupby
import textwrap
from PIL import ImageFont, Image, ImageDraw
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


class Text(object):
    """Text representation"""

    # noinspection PyShadowingBuiltins
    def __init__(self, index, value, keywords, type, style, xloc=None, yloc=None, points=None,
                 fgColor=None, bgColor=None, bgOpacity=1.0):
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
        self.__fgColor = fgColor or (255, 255, 255)
        self.__bgColor = bgColor or (0, 0, 0)
        self.__bgOpacity = bgOpacity
        self.__points = points

    @property
    def fgColor(self):
        return self.__fgColor

    @property
    def bgColor(self):
        return self.__bgColor

    @property
    def bgOpacity(self):
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
    def boWidth(self):
        return self.__boWidth

    @boWidth.setter
    def boWidth(self, width=2):
        """
        Set the outline width in pixels

        :type width: int
        """

        self.__boWidth = width

    @property
    def boColor(self):
        return self.__boColor

    @boColor.setter
    def boColor(self, color=None):
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
        self.__draw = None
        self.__filename = None

        self.__styles = {
            Style.normal: StyleInfo(10, 12, 'regular'),
            Style.h1: StyleInfo(30, 32, 'regular'),
            Style.h2: StyleInfo(24, 26, 'regular'),
            Style.h3: StyleInfo(20, 22, 'regular'),
        }

    def generateTextImage(self, texts, imageFile):
        """

        :param texts:
        :param imageFile:
        :type texts: list[Text]
        :type imageFile: basestring
        :return:
        """
        self.__filename = imageFile
        self.__texts = texts

        self.__drawImage()

    def __drawImage(self):
        self.__image = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))
        self.__draw = ImageDraw2(self.__image)

        # font = ImageFont.truetype("arial.ttf")
        # self.__draw.text((10, 10), "hello", font=font)
        #
        # font = ImageFont.truetype("arial.ttf")
        # self.__draw.text((10, 25), "world", fill=(0, 0, 0), font=font)
        #

        for key, group in groupby(self.__texts, lambda x: [x.type, x.xloc, x.yloc]):
            group = list(sorted(group, key=lambda x: x.index))

            if key[0] == Type.default:
                self.__drawAtTheBottom(group)
            else:
                self.__drawGroup(key, group)

        self.__image.save(self.__filename, format='png')

    def __drawGroup(self, key, group):
        if len(group) == 0:
            return

        type = key[0]
        xloc = key[1]
        yloc = key[2]

        width = self.__width
        height = self.__height

        if xloc == XLocation.left:
            x = width * 0.05 if type == Type.west else width * 0.55
            align = "left"
        elif xloc == XLocation.center:
            x = width / 4 if type == Type.west else width * 3 / 4
            align = "center"
        else:
            # NO!
            x = width * 0.4 if type == Type.west else width * 0.9
            align = "right"

        if yloc == YLocation.top:
            y = height * 0.05
        elif yloc == YLocation.center:
            y = height * 0.5
        else:
            # NO!
            y = height * 0.9
            y_end = height * 0.9

        for t in group:
            style = self.__styles[t.style]
            font = ImageFont.truetype("arial.ttf", size=style.fontSize)
            top = self.__draw.multiline_text((x, y), t.value, fill=t.fgColor, font=font, align=align)
            y += top

            # self.__draw.rectangle()

    def __drawAtTheBottom(self, group):
        y = self.__height

        for t in group:
            style = self.__styles[t.style]
            font = ImageFont.truetype("arial.ttf", size=style.fontSize)
            symbol_size = font.getsize('A')
            spacing = style.lineHeight - symbol_size[1]
            font = ImageFont.truetype("arial.ttf", size=style.fontSize)
            text = t.value
            result = self.__draw.split_text_to_multiline(text, font, self.__width, spacing)

            y -= result.size[1]
            y -= symbol_size[1]

        for t in group:
            style = self.__styles[t.style]
            font = ImageFont.truetype("arial.ttf", size=style.fontSize)
            symbol_size = font.getsize('A')
            spacing = style.lineHeight - symbol_size[1]
            text = t.value

            result = self.__draw.split_text_to_multiline(text, font, self.__width, spacing)

            self.__draw.multiline_text((symbol_size[0] * 2, y), text, fill=t.fgColor, font=font)
            y += result.size[1]
            y += symbol_size[1]

    def set_font_style(self, style, fontSize, lineHeight, fontWeight):
        """

        :type style: Style
        :type fontSize: int
        :type lineHeight: int
        :type fontWeight: int
        """
        self.__styles[style] = StyleInfo(fontSize, lineHeight, fontWeight)


class SplitResult(object):
    def __init__(self, text, size):
        self.text = text
        self.size = size


class StyleInfo(object):
    def __init__(self, fontSize, lineHeight, fontWeight):
        self.fontSize = fontSize
        self.lineHeight = lineHeight
        self.fontWeight = fontWeight


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
        left, top = xy
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
        return top

    def split_text_to_multiline(self, text, font, width, spacing):
        """
        :type text: str
        :type font: ImageFont
        :type width: int
        :type spacing: int
        """
        size = self.textsize(text, font)
        if size[1] < width:
            return SplitResult(text, size)

        text.rsplit()

        symbolSize = self.textsize('A', font=font)
        symbol_width = symbolSize[0]
        max_symbols_in_line = width / symbol_width

        text = textwrap.fill(text, width=max_symbols_in_line)
        size = self.multiline_textsize(text, font, spacing)
        return SplitResult(text, size)


if __name__ == '__main__':
    p = Page(0, 400, 200)
    style = Style.normal

    t1 = Text(0, '123', [], Type.default, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t2 = Text(1, '000', [], Type.east, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t3 = Text(2, '000', [], Type.east, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t4 = Text(3, '456', [], Type.west, style, XLocation.right, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t5 = Text(4, '456', [], Type.west, style, XLocation.right, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    p.generateTextImage([t1, t2, t3, t4], 'D:\\1.png')

    t1 = Text(0, '123', [], Type.default, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t2 = Text(0, '123', [], Type.default, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t3 = Text(1, 'LT1', [], Type.east, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t4 = Text(2, 'LT2', [], Type.east, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t5 = Text(3, 'RB1', [], Type.east, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t6 = Text(4, 'RB2', [], Type.east, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t5 = Text(3, 'RB1', [], Type.east, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t6 = Text(4, 'RB2', [], Type.east, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t7 = Text(3, 'CR1', [], Type.east, style, XLocation.right, YLocation.center, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t8 = Text(4, 'CR2', [], Type.east, style, XLocation.right, YLocation.center, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    p.generateTextImage([t1, t2, t3, t4, t5, t6, t7, t8], 'D:\\2.png')

    t3 = Text(1, 'LT1', [], Type.west, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t4 = Text(2, 'LT2', [], Type.west, style, XLocation.left, YLocation.top, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t5 = Text(3, 'RB1', [], Type.west, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t6 = Text(4, 'RB2', [], Type.west, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t5 = Text(3, 'RB1', [], Type.west, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t6 = Text(4, 'RB2', [], Type.west, style, XLocation.right, YLocation.bottom, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    t7 = Text(3, 'CR1', [], Type.west, style, XLocation.right, YLocation.center, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))
    t8 = Text(4, 'CR2', [], Type.west, style, XLocation.right, YLocation.center, None, fgColor=(0, 0, 0),
              bgColor=(255, 0, 0))

    p.generateTextImage([t1, t2, t3, t4, t5, t6, t7, t8], 'D:\\3.png')
