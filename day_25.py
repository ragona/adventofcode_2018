from dataclasses import dataclass, field
from collections import namedtuple
import networkx as nx
import unittest


class Star(namedtuple('Star', ['x', 'y', 'z', 't'])):

    @classmethod
    def star_from_string(cls, string):
        return cls(*[int(i) for i in string.strip().split(',')])

    @classmethod
    def stars_from_file(cls, filename):
        with open(filename) as f:
            lines = [line.strip() for line in f.readlines()]

        return [Star.star_from_string(line) for line in lines]

    def dist(self, other):
        return sum([
            abs(self.x - other.x),
            abs(self.y - other.y),
            abs(self.z - other.z),
            abs(self.t - other.t),
        ])


@dataclass
class Galaxy:

    stars: list = field(repr=False)

    def num_constellations(self, tolerance=3):
        if len(self.stars) == 0:
            return

        graph = nx.Graph()

        for star1 in self.stars:
            for star2 in self.stars:
                if star1.dist(star2) <= tolerance:
                    graph.add_edge(star1, star2)

        return nx.number_connected_components(graph)


class TestConstellation(unittest.TestCase):

    def test_star_from_string(self):
        star = Star.star_from_string("4,5,0,-5")

        assert star.x == 4
        assert star.y == 5
        assert star.z == 0
        assert star.t == -5

    def test_stars_from_file(self):
        pass

    def test_num_constellations(self):
        lines = [
            "0,0,0,0",
            "3,0,0,0",
            "0,3,0,0",
            "0,0,3,0",
            "0,0,0,3",
            "0,0,0,6",
            "9,0,0,0",
            "12,0,0,0"
        ]

        stars = [Star.star_from_string(line) for line in lines]
        galaxy = Galaxy(stars)

        assert galaxy.num_constellations() == 2

    def test_part_1(self):
        stars = Star.stars_from_file("input/day_25.txt")
        galaxy = Galaxy(stars)

        print("Part 1:", galaxy.num_constellations())
