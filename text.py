# -*- coding: utf-8 -*-
from collections import defaultdict

import os
from enum import Enum
from PIL import ImageFont, Image
from PIL.ImageDraw import ImageDraw, ImageColor
import math
import sys
from bezier import smooth_points, convert_to_degree, get_angle
import textwrap2


class Type(Enum):
    default = 'default'
    east = 'east'
    west = 'west'
    polygon = 'polygon'
    callout = 'callout'


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
    """
    Gets width and height for "A" symbol

    :param font:
    :return:
    """
    return font.getsize('A')


def centroid(points):
    """
    Calculates the center point of callout points

    :param points:
    :return:
    """
    center = [0, 0]
    points_count = len(points)

    if points_count == 0:
        return center

    if points_count == 1:
        return points[0]

    for point in points:
        center[0] += point[0]
        center[1] += point[1]

    center[0] /= points_count
    center[1] /= points_count

    return center


def get_polygon_width(points):
    """
    Get the available width of callout to place text

    :param points: callout points
    :return:
    """
    min_x = sys.maxsize
    max_x = 0

    for point in points:
        min_x = min(min_x, point[0])
        max_x = max(max_x, point[1])

    return int(math.floor(math.fabs(max_x - min_x)) * 0.8)


def get_color(color):
    if isinstance(color, str):
        return ImageColor.getcolor(color, "RGB")
    if isinstance(color, (tuple, list)):
        return tuple(color[:3])
    return color


def full_group_by(l, key=lambda x: x):
    d = defaultdict(list)
    for item in l:
        key1 = key(item)
        d[key1].append(item)
    return d.items()


class TextGroup(object):
    # noinspection PyShadowingBuiltins
    def __init__(self, type, xloc, yloc):
        self.type = type
        self.xloc = xloc
        self.yloc = yloc

    def __str__(self):
        return str.format("{0}{1}{2}", self.type, self.xloc, self.yloc)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.type == other.type and \
               self.xloc == other.xloc and \
               self.yloc == other.yloc


class Text(object):
    """Text representation"""

    # noinspection PyShadowingBuiltins
    def __init__(self, index, value, keywords,
                 type=Type.default,
                 style=Style.normal,
                 xloc=XLocation.center,
                 yloc=YLocation.center,
                 points=None,
                 fgcolor=None,
                 bgcolor=None,
                 bgopacity=0.3):
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
        assert 0 <= bgopacity <= 1

        super(Text, self).__init__()
        self.__index = index
        self.__value = value
        self.__keywords = keywords
        self.__type = type
        self.__style = style
        self.__xloc = xloc
        self.__yloc = yloc
        self.__boWidth = 2
        self.__boColor = (0, 0, 0)
        self.__fgcolor = fgcolor or (255, 255, 255)
        self.__points = points

        if bgcolor:
            bgcolor = get_color(bgcolor)
            bgcolor = bgcolor[:] + (int(bgopacity * 255),)
            self.__bgcolor = bgcolor
            self.__bgOpacity = bgopacity
        else:
            self.__bgcolor = None
            self.__bgOpacity = 0

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
        self.__boColor = color

    @property
    def points(self):
        return self.__points

    def __str__(self):
        return str.format('Type: {0}, xloc: {1}, yloc: {2}, value: {3}', self.type, self.xloc, self.yloc, self.value)


class Page(object):
    """Page that splitted for two halves"""

    def __init__(self, idx, width, height):
        super(Page, self).__init__()
        self.__id = idx
        self.__width = width
        self.__height = height

        self.__texts = []
        self.__images = []
        self.__filename = ""
        self.__bbox = {}
        self.__callout_pointer_angle = 45
        self.__callout_smooth_factor = 0.5

        self.__styles = {
            Style.normal: StyleInfo(20, 25),
            Style.h1: StyleInfo(26, 28),
            Style.h2: StyleInfo(22, 24),
            Style.h3: StyleInfo(20, 22),
        }

    # noinspection PyPep8Naming
    def setCalloutPointerAngle(self, angle):
        """
        :type angle: int
        """
        self.__callout_pointer_angle = angle

    # noinspection PyPep8Naming
    def generateTextImage(self, texts, imagefile):
        """
        Generates image for text items and saves to imagefile

        :type texts: list[Text]
        :type imagefile: str
        :return:
        """

        self.__filename = imagefile
        self.__texts = texts
        self.__bbox.clear()
        self.__images = []

        self.__draw_image()

        return self.__bbox

    def __draw_image(self):
        """
        Draws the images (with and without keywords highlighted)
        """
        result = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))
        self.__text_helper = ImageDraw2(result, mode='RGBA')
        result = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))

        texts = list(sorted(self.__texts, key=lambda x: x.index))

        for key, group in full_group_by(texts, lambda x: TextGroup(x.type, x.xloc, x.yloc)):
            type_ = key.type
            group = list(group)

            if type_ == Type.default:
                self.__draw_bottom(group)
            elif type_ == Type.polygon:
                for p in group:
                    self.__draw_polygon(p)
            elif type_ == Type.callout:
                for c in group:
                    self.__draw_callout(c)
            else:
                self.__draw_side_group(key, group)

        self.__highimage = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))
        self.__high_draw = ImageDraw(self.__highimage, mode="RGBA")
        self._draw_bbox()

        images_count = len(self.__images)
        if images_count > 0:
            result = self.__images[0]
            for i in range(1, images_count):
                second = self.__images[i]
                result = Image.alpha_composite(result, second)

        result.save(self.__filename)

        if len(self.__bbox):
            highl_filename = os.path.splitext(self.__filename)[0] + "_hi.png"
            result = Image.alpha_composite(result, self.__highimage)
            result.save(highl_filename)

    def __draw_side_group(self, key, group):
        """
        Draws east and west sides of the page
        """
        if len(group) == 0:
            return

        # noinspection PyShadowingBuiltins
        type = key.type
        xloc = key.xloc
        yloc = key.yloc
        width = self.__width

        _, bgdraw = self.get_new_image()
        _, draw = self.get_new_image()

        if xloc == XLocation.left:
            x = width * 0.05 if type == Type.west else width * 0.55
            align = "left"
        elif xloc == XLocation.center:
            x = width / 4 if type == Type.west else width * 3 / 4
            align = "center"
        else:
            x = width * 0.45 if type == Type.west else width * 0.95
            align = "right"

        box_width = int(width * 0.3)
        y = self.__calc_y_top(yloc, group)
        x_min = x
        x_max = 0
        y_min = y

        for t in group:
            split = self.__split_text(box_width, t)
            spacing = split.spacing
            font = split.font

            draw.set_keywords(t.keywords)
            bbox = draw.multiline_text((x, y), split.text, font=font,
                                       fill=t.fgcolor, align=align, outline=t.fgcolor)
            self.__update_bbox_dict(draw.bbox)

            x_min = min(x_min, bbox[0])
            x_max = max(x_max, bbox[2])

            y += split.size[1] + spacing

        bg = group[0].bgcolor
        if bg is not None:
            bgdraw.rectangle([x_min, y_min, x_max, y], fill=bg)

    def __split_text(self, box_width, t):
        """
        Splits text if text width will be wider than box_width.
        Also, calculates space required, spacings and etc.

        :type box_width: int
        :type t: Text
        """
        style = self.__styles[t.style]
        line_height = style.line_height
        font = ImageFont.truetype(style.font_face, size=style.font_size)
        symbol_height = self.__text_helper.textsize('A', font=font)[1]
        spacing = line_height - symbol_height

        split = self.__text_helper.split_text_to_multiline(t.value, font, box_width, spacing)
        split.symbol_height = symbol_height
        split.spacing = spacing

        return split

    def __calc_y_top(self, yloc, group):
        """
        Calculates minimum Y for group
        """

        if len(group) == 0:
            return 0

        height = self.__height
        width = self.__width * 0.3

        if yloc == YLocation.top:
            return height * 0.05

        if yloc == YLocation.center:
            y = height / 2
        else:
            y = height * 0.95

        return self.__calc_y_top_from_start_y(group, width, y, yloc)

    def __calc_y_top_from_start_y(self, group, width, y, yloc):
        for t in group:
            split = self.__split_text(width, t)
            size = split.size

            if yloc == YLocation.center:
                y -= size[1] / 2
            else:
                y -= size[1]

        return y

    def __draw_bottom(self, group):
        """
        Draws the text at the bottom of page (texts with Type.default)
        """

        _, bgdraw = self.get_new_image()
        _, draw = self.get_new_image()

        y = self.__height

        group_count = len(group)
        for idx, t in enumerate(group):
            splitted = self.__split_text(self.__width, t)
            symbol_size = splitted.symbol_height
            y -= splitted.size[1]

            if idx != group_count - 1:
                y -= symbol_size
            else:
                y -= 2

        y_min = y

        for t in group:
            margin = 3
            splitted = self.__split_text(self.__width - 2 * margin, t)
            symbol_size = splitted.symbol_height
            font = splitted.font

            draw.set_keywords(t.keywords)
            draw.multiline_text((margin, y), splitted.text,
                                fill=t.fgcolor, font=font, outline=t.fgcolor)
            self.__update_bbox_dict(draw.bbox)

            y += splitted.size[1] + symbol_size

        bg = group[0].bgcolor
        if bg is not None:
            bgdraw.rectangle([0, y_min, self.__width, self.__height], fill=bg)

    def get_new_image(self):
        """
        :rtype : tuple(Image, ImageDraw)
        """
        image = Image.new("RGBA", (self.__width, self.__height), (0, 0, 0, 0))
        draw = ImageDraw2(image, mode="RGBA")
        self.__images.append(image)
        return image, draw

    def __update_bbox_dict(self, bbox_dict):
        """
        Updates the internal bounding boxes dictionary
        """
        for kw, boxes in bbox_dict.items():
            arr = self.__bbox.get(kw, [])
            self.__bbox[kw] = arr

            for box in boxes:
                arr.append(box)

    def set_font_style(self, style, font_size, line_height):
        """
        Changes style for drawn texts

        :type style: Style
        :type font_size: int
        :type line_height: int
        """

        self.__styles[style] = StyleInfo(font_size, line_height)

    def __draw_polygon(self, t):
        """
        Draws polygon using Text.points

        :type t: Text
        """
        points = t.points

        _, bgdraw = self.get_new_image()
        _, text_draw = self.get_new_image()

        # Draw polygon
        bgdraw.polygon(points, fill=t.bgcolor, outline=t.bocolor)

        text_center_x, text_center_y = centroid(points)
        box_width = get_polygon_width(points)
        text_center_y = self.__calc_y_top_from_start_y([t], box_width, text_center_y, YLocation.center)
        center = [text_center_x, text_center_y]

        split = self.__split_text(box_width, t)
        font = split.font

        text_draw.set_keywords(t.keywords)
        text_draw.multiline_text(center, split.text, font=font,
                                 fill=t.fgcolor, align="center", outline=t.fgcolor)
        self.__update_bbox_dict(text_draw.bbox)

    def __draw_callout(self, t):
        """
        Draws callout using Text.points

        :type t: Text
        """

        all_points = t.points

        _, bgdraw = self.get_new_image()
        _, text_draw = self.get_new_image()

        # Draw polygon
        smoothed = smooth_points(all_points, self.__callout_smooth_factor, self.__callout_pointer_angle)
        bgdraw.polygon(smoothed, fill=t.bgcolor, outline=t.bocolor)

        # remove callout angle from polygon to recognize callout center
        points_no_callout_center = self.__get_points_without_callout_angle_center(all_points)
        text_center_x, text_center_y = centroid(points_no_callout_center)
        box_width = get_polygon_width(points_no_callout_center)
        text_center_y = self.__calc_y_top_from_start_y([t], box_width, text_center_y, YLocation.center)
        center = [text_center_x, text_center_y]

        split = self.__split_text(box_width, t)
        font = split.font

        text_draw.set_keywords(t.keywords)
        text_draw.multiline_text(center, split.text, font=font,
                                 fill=t.fgcolor, align="center", outline=t.fgcolor)
        self.__update_bbox_dict(text_draw.bbox)

    @staticmethod
    def __get_points_without_callout_angle_center(all_points):
        points_count = len(all_points)

        points_no_callout_center = all_points[:]
        for i in range(points_count):
            p2 = all_points[i]
            p1 = all_points[(i + 1) % points_count]
            p3 = all_points[(i + 2) % points_count]
            angle = convert_to_degree(get_angle(p1, p2, p3))
            if angle <= 45:
                del points_no_callout_center[(i + 1) % points_count]
                break
        return points_no_callout_center

    def _draw_bbox(self):
        """
        Draws bounding boxes to keywords highlighted image
        """

        for key, bbox_arr in self.__bbox.items():
            for box in bbox_arr:
                self.__high_draw.rectangle(box.box, outline=box.outline)


class SplitResult(object):
    def __init__(self, text, size, font):
        self.text = text
        self.size = size
        self.symbol_height = 10 if font is None else font.size
        self.font = font
        self.spacing = 2

    def __str__(self):
        return str.format("Size={0} Text={1}", self.size, self.text)


class BoundingBox(object):
    def __init__(self, box, outline):
        self.box = box
        self.outline = outline

    def __str__(self):
        return str.format("{0}", self.box)


class StyleInfo(object):
    def __init__(self, font_size, line_height):
        self.font_size = font_size
        self.line_height = line_height
        self.font_face = "arial.ttf"

    def __str__(self):
        return str.format("FS={0} LH={1} FW={2}", self.font_size, self.line_height)


def get_word(line):
    """
    Gets the next word from line

    :type line: str
    """
    letters = []

    for b in line:
        if str.isspace(b):
            break
        letters.append(b)

    return ''.join(letters)


class ImageDraw2(ImageDraw):
    def __init__(self, im, mode=None):
        super(ImageDraw2, self).__init__(im, mode)
        self.__keywords = []
        self.__bbox = {}

    def set_keywords(self, keywords):
        """
        :type keywords: list[str]
        """
        self.__keywords = keywords

    @property
    def bbox(self):
        return self.__bbox

    def multiline_text(self, xy, text, fill=None, font=None, anchor=None, outline=None,
                       spacing=4, align="left"):
        """
        Draws multiline text on the image
        """

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

        lines_count = len(lines)
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

            self.__find_bounding_boxes(font, left, line, line_spacing, outline, top)

            left = xy[0]
            if idx != lines_count - 1:
                top += line_spacing

        return [left, top_initial, left + max_width, top]

    def __find_bounding_boxes(self, font, left, line, line_spacing, outline, top):
        for kw in self.__keywords:
            if kw in line:
                index = 0
                while index != -1:
                    index = line.find(kw, index)
                    if index != -1:
                        skip_area = self.textsize(line[:index], font)
                        bbox = self.textsize(get_word(line[index:]), font)

                        text_start_x = left + skip_area[0] - 2
                        text_end_x = text_start_x + bbox[0] + 3
                        bbox = [text_start_x, top, text_end_x, top + line_spacing]
                        # self.rectangle(bbox, outline=outline)

                        arr = self.__bbox.get(kw, [])
                        arr.append(BoundingBox(bbox, outline))
                        self.__bbox[kw] = arr

                        index += 1

    def split_text_to_multiline(self, text, font, width, spacing):
        """
        Splits long text to multiline text if text don't fit in available width

        :type text: str
        :type font: ImageFont
        :type width: int|float
        :type spacing: int
        """
        size = self.textsize(text, font)
        if size[0] < width:
            return SplitResult(text, size, font)

        total_width = 0
        total_height = 0

        lines = []
        for line in text.splitlines():
            w = textwrap2.TextWrapper(font, width=width)
            line = w.fill(line)
            w, h = self.multiline_textsize(line, font, spacing)
            total_width += w
            total_height += h
            lines.append(line)

        result_text = "\n".join(lines)
        result_size = (total_width, total_height)
        return SplitResult(result_text, result_size, font)
