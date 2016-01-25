from unittest import TestCase
from text import centroid
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
        expected = [[0, 0], [0, 1], [1, 2], [1, 3], [2, 4], [2, 5], [3, 6], [3, 7], [4, 8], [4, 9], [5, 10]]

        result = line((0, 0), (5, 10))
        result2 = line((5, 10), (0, 0))
        self.assertEqual(expected, result)
        self.assertEqual(expected, result2)
