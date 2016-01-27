from unittest import TestCase
from text import *
from bezier import line, get_angle, convert_to_degree


class TestColor(TestCase):
    def testColorParsed(self):
        t = Text(0, "", [], bgcolor="#cccccc", bgopacity=0.3)
        self.assertEqual(t.bgcolor, (204, 204, 204, 76))

        t = Text(0, "", [], bgcolor=(204, 204, 204), bgopacity=0.3)
        self.assertEqual(t.bgcolor, (204, 204, 204, 76))

        t = Text(0, "", [], bgcolor=(204, 204, 204, 76), bgopacity=0.3)
        self.assertEqual(t.bgcolor, (204, 204, 204, 76))


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
    test_page = Page(0, 1024, 576)
    style = Style.normal
    text = "The quick brown fox jumps over the lazy dog"
    bgcolor = (253, 120, 120)

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

    coords = [(100, 300), (200, 250),
              (300, 100), (500, 100),
              (500, 300), (300, 300)]

    text = '123 456'
    t1 = Text(3, text, ['123', '456'], points=coords, bgcolor=bgcolor, fgcolor='black', style=Style.h1)

    test_page.generateTextImage([t1], '5.png')

    polygon_page = Page(0, 1024, 576)
    polygon_page.set_font_style(Style.normal, 16, 20)

    t1 = Text(0,
              "BOTTOM\nLEFT WEST\nWorld champion Viswanathan Anand started his title defence in style, holding off"
              " world number one Magnus Carlsen of Norway to a draw in quick time in the.", [],
              Type.west, Style.normal, XLocation.left, YLocation.bottom, fgcolor="#FFFFFF", bgcolor="#cccccc",
              bgopacity=0.5)
    t2 = Text(1,
              "DEFAULT One - 1 One = 1 ONe ===  1", [], Type.default, Style.h2, XLocation.left, YLocation.top,
              fgcolor="#ffffff", bgcolor="#000000", bgopacity=0.5)

    t3 = Text(2,
              "RIGHT BOTTOM EAST on same location 2", [], Type.east, Style.normal, XLocation.right, YLocation.bottom,
              fgcolor="#ffffff", bgcolor="#000000", bgopacity=0.5)

    t4 = Text(3,
              "1\n 2 3\n 4 5 6 7 6 5 4 3 2 1 2 3 4 5 6 7 8 9 0 9 8 7 8 9 7 6 5 5 4 3 2 2 3 4 2 3 2 13 3 4"
              "  6 6 7 7 5 43 3 2 2  3 4 45 5  6 77 8 99 77 5 45", [],
              Type.polygon, Style.h3, fgcolor="#FFFFFF", bgcolor="#FF0000", bgopacity=0.5,
              points=[(299, 345),
                      (248, 379),
                      (231, 409),
                      (220, 454),
                      (221, 518),
                      (243, 550),
                      (286, 562),
                      (358, 569),
                      (432, 570),
                      (491, 567),
                      (500, 543),
                      (505, 500),
                      (506, 450),
                      (502, 418),
                      (462, 397),
                      (412, 379),
                      (353, 366),
                      (332, 353),
                      (353, 310),
                      (305, 338)])

    t5 = Text(4,
              "A hamster does not need many supplies. Every hamster needs shelter, water and food. A hamster should "
              "have a large cage that it cannot escape from. The cage needs some sort of soft bedding, such as wood "
              "shavings. You should get a water bottle and food bowl to put in the cage.", [],
              Type.polygon, Style.normal, fgcolor="#FFFFFF", bgcolor="#FF0FF0", bgopacity=0.5,
              points=[(578, 55),
                      (540, 115),
                      (400, 155),
                      (554, 172),
                      (600, 217),
                      (667, 232),
                      (745, 223),
                      (794, 197),
                      (823, 146),
                      (817, 87),
                      (774, 44),
                      (714, 22),
                      (635, 23)])

    polygon_page.set_font_style(Style.normal, 13, 18)
    polygon_page.generateTextImage([t1, t2, t3, t4, t5], 'test1.png')

    t4 = Text(3,
              "1\n 2 3\n 4 5 6 7 6 5 4 3 2 1 2 3 4 5 6 7 8 9 0 9 8 7 8 9 7 6 5 5 4 3 2 2 3 4 2 3 2 13 3 4"
              "  6 6 7 7 5 43 3 2 2  3 4 45 5  6 77 8 99 77 5 45", [],
              Type.polygon, Style.h3, fgcolor="#FFFFFF", bgcolor="#FF0000", bgopacity=0.5,
              points=[(142, 113),
                      (282, 39),
                      (424, 135),
                      (390, 201),
                      (500, 300),
                      (332, 221),
                      (128, 273),
                      (132, 173),
                      (142, 113)
                      ])

    t5 = Text(4,
              "A hamster does not need many supplies. Every hamster needs shelter, water and food. A hamster should "
              "have a large cage that it cannot escape from. The cage needs some sort of soft bedding, such as wood "
              "shavings. You should get a water bottle and food bowl to put in the cage.", [],
              Type.callout, Style.normal, fgcolor="#FFFFFF", bgcolor="#FF0FF0", bgopacity=0.5, bocolor="#000000",
              points=[(578, 55),
                      (540, 115),
                      (400, 155),
                      (554, 172),
                      (600, 217),
                      (667, 232),
                      (745, 223),
                      (794, 197),
                      (823, 146),
                      (817, 87),
                      (774, 44),
                      (714, 22),
                      (635, 23)])

    polygon_page.set_font_style(Style.h3, 18, 24)
    polygon_page.set_font_style(Style.normal, 13, 18)
    polygon_page.generateTextImage([t4, t5], 'test2.png')

    t1 = Text(0,
              "BOTTOM\nLEFT WEST\nWorld champion Viswanathan Anand started his title defence in style, holding off"
              " world number one Magnus Carlsen of Norway to a draw in quick time in the.",
              [], Type.west, Style.normal, xloc=XLocation.left, yloc=YLocation.bottom, fgcolor="#FFFFFF",
              bgcolor="#cccccc", bgopacity=0.5)

    t2 = Text(1,
              "CENTER CENTER WEST World champion Viswanathan Anand started his title defence in style, holding off "
              "world number one Magnus Carlsen of Norway to a draw in quick time in the.",
              [], Type.west, Style.h1, xloc=XLocation.center, yloc=YLocation.center, fgcolor="#170170",
              bgcolor="#00C00C", bgopacity=0.5)

    t3 = Text(2,
              "TOP RIGHT WEST\nWorld champion \n Viswanathan \n Anand \n started his title defence in style, holding "
              "off world number one Magnus Carlsen of Norway to a draw in quick time in the.",
              [], Type.west, Style.h2, xloc=XLocation.right, yloc=YLocation.top, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)

    t4 = Text(3,
              "BOTTOM LEFT EAST World champion \n Viswanathan \n Anand \n started his title defence in style, holding "
              "off world number one Magnus Carlsen of Norway to a draw in quick time in the.",
              [], Type.east, Style.h3, xloc=XLocation.left, yloc=YLocation.bottom, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)

    t5 = Text(4,
              "CENTER CENTER EAST on same location 1",
              [], Type.east, Style.normal, xloc=XLocation.center, yloc=YLocation.center, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)

    t6 = Text(5,
              "CENTER CENTER EAST on same location 2",
              [], Type.east, Style.normal, xloc=XLocation.center, yloc=YLocation.center, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)

    t7 = Text(6,
              "CENTER CENTER EAST on same location 3",
              [], Type.east, Style.normal, xloc=XLocation.center, yloc=YLocation.center, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)

    t8 = Text(7,
              "RIGHT BOTTOM EAST on same location 1",
              [], Type.east, Style.normal, xloc=XLocation.right, yloc=YLocation.bottom, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)
    t9 = Text(8,
              "RIGHT BOTTOM EAST on same location 2",
              [], Type.east, Style.normal, xloc=XLocation.right, yloc=YLocation.bottom, fgcolor="#ffffff",
              bgcolor="#000000", bgopacity=0.5)

    t10 = Text(9,
               "RIGHT BOTTOM EAST on same location 3",
               [], Type.east, Style.normal, xloc=XLocation.right, yloc=YLocation.bottom, fgcolor="#ffffff",
               bgcolor="#000000", bgopacity=0.5)

    t11 = Text(11,
               "DEFAULT One - 1 One = 1 ONe ===  1",
               [], Type.default, Style.h2, xloc=XLocation.left, yloc=YLocation.top, fgcolor="#ffffff",
               bgcolor="#000000", bgopacity=0.5)

    t12 = Text(12,
               "DEFAULT Two 2 = Two = 2 ===Two 2",
               [], Type.default, Style.h2, xloc=XLocation.left, yloc=YLocation.top, fgcolor="#ffffff",
               bgcolor="#000000", bgopacity=0.5)

    test_page.generateTextImage([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12], 'test3.png')

    t1 = Text(0,
              "Brady's numbers were hardly noteworthy. He was 25 for 43, with 269 yards passing, a touchdown and an "
              "interception. But it was his sense of timing, and the killer instinct he displayed on New England's "
              "final drive that will be seared into our memories and become New England football folklore. And unless "
              "the Patriots win another Super Bowl this time, or least make it to Met Life Stadium in the snow and cold"
              " of February, his 17-yard TD pass to rookie Kenbrell Thompkins with five seconds to play will be the"
              " signature moment of their season.",
              [], bgcolor=(0, 0, 0))

    test_page.generateTextImage([t1], 'test4.png')


if __name__ == '__main__':
    __test()
# unittest.main()
