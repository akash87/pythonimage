from unittest import TestCase
import unittest
from text import *
from bezier import line, get_angle, convert_to_degree


class TestCentroid(TestCase):
    def testEmpty(self):
        points = []
        center = centroid(points)
        self.assertEqual([0, 0], center)

    def testOnePoint(self):
        points = [(10, 10)]
        center = centroid(points)
        self.assertEqual((10, 10), center)

    def testTwoPoints(self):
        points = [(0, 0), (10, 10)]
        center = centroid(points)
        self.assertEqual([5, 5], center)


class TestGetAngle(TestCase):
    def test90degrees(self):
        angle = get_angle((0, 10), (0, 0), (10, 0))
        self.assertAlmostEqual(45, convert_to_degree(angle), delta=0.1)

    def test45degrees(self):
        angle = get_angle((0, 10), (0, 0), (10, 10))
        self.assertAlmostEqual(90, convert_to_degree(angle), delta=0.1)


class TestCreateLine(TestCase):
    def testOnePoint(self):
        expected = [(0, 0)]
        result = line((0, 0), (0, 0))
        self.assertEqual(expected, result)

    def testTwoPoints(self):
        expected = [(0, 0), (1, 0)]
        result = line((0, 0), (1, 0))
        self.assertEqual(expected, result)

    def testMirrorPoints(self):
        expected = [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7), (4, 8), (4, 9), (5, 10)]

        result = line((0, 0), (5, 10))
        result2 = line((5, 10), (0, 0))
        self.assertEqual(expected, result)
        self.assertEqual(expected, result2)


def __test():
    test_page = Page(0, 400, 400)
    style = Style.normal
    text = "The quick brown fox jumps over the lazy dog"
    bgcolor = (253, 120, 120, 70)

    t1 = Text(0, text, [], Type.default, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t2 = Text(1, text, [], Type.east, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)
    t3 = Text(2, text, [], Type.east, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)

    t4 = Text(3, text, [], Type.west, style,
              XLocation.right, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t5 = Text(4, text, [], Type.west, style,
              XLocation.right, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    test_page.generateTextImage([t1, t2, t3, t4, t5], '1.png')

    # text = "small text"
    t1 = Text(0, text, ['brown'], Type.default, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)
    t2 = Text(0, text, ['jumps'], Type.default, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(255, 0, 0), bgcolor=bgcolor)

    t3 = Text(1, text, ['brown'], Type.east, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t4 = Text(2, text, ['brown'], Type.east, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t5 = Text(3, text, ['brown'], Type.east, style,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t6 = Text(4, text, ['brown'], Type.east, style,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t7 = Text(3, text, ['brown'], Type.east, style,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t8 = Text(4, text, ['brown'], Type.east, style,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    test_page.generateTextImage([t1, t2, t3, t4, t5, t6, t7, t8], '2.png')

    t3 = Text(1, text, ['The', 'fox'], Type.west, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t4 = Text(2, text, [], Type.west, style,
              XLocation.left, YLocation.top,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t5 = Text(3, text, [], Type.west, style,
              XLocation.left, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)
    t6 = Text(4, text, [], Type.west, style,
              XLocation.left, YLocation.bottom,
              None, fgcolor=(0, 0, 0), bgcolor=bgcolor)

    t7 = Text(3, text, [], Type.west, style,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 255), bgcolor=bgcolor)
    t8 = Text(4, text, [], Type.west, style,
              XLocation.right, YLocation.bottom,
              None, fgcolor=(0, 0, 255), bgcolor=bgcolor)

    t9 = Text(3, text, [], Type.west, style,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t1 = Text(4, text, [], Type.west, style,
              XLocation.right, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)

    test_page.generateTextImage([t3, t4, t5, t6, t7, t8, t9, t1], '3.png')

    t1 = Text(3, text, [], Type.west, Style.h2,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t2 = Text(4, text, [], Type.west, Style.h3,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)

    t3 = Text(3, text, [], Type.east, style,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t4 = Text(4, text, [], Type.east, style,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)
    t5 = Text(5, text, [], Type.east, style,
              XLocation.center, YLocation.center,
              None, fgcolor=(0, 255, 0), bgcolor=bgcolor)

    test_page.generateTextImage([t1, t2, t3, t4, t5], '4.png')

    test_page = Page(0, 600, 600)
    coords = [(100, 300), (200, 250),
              (300, 100), (500, 100),
              (500, 300), (300, 300)]

    text = '123 456'
    t1 = Text(3, text, ['123', '456'], points=coords, bgcolor=bgcolor, fgcolor='black', style=Style.h1)

    # test_page.set_font_style(Style.normal, 6, 8, 'normal')
    test_page.generateTextImage([t1], '5.png')


if __name__ == '__main__':
    __test()
    unittest.main()
