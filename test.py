from unittest import TestCase
from text import Text, centroid


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
