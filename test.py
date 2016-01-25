from unittest import TestCase
import math
from text import Text, centroid, get_angle, convert_to_degree


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
