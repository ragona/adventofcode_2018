from collections import namedtuple
from dataclasses import dataclass
from util import number_grabber
from scipy.spatial import distance
from heapq import heappop, heappush

import unittest


class Point(namedtuple('Point', ['x', 'y', 'z'])):

    def dist(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)


@dataclass
class Nanobot:

    pos: Point
    radius: int

    @classmethod
    def nanobot_from_string(cls, string):
        numbers = number_grabber(string)
        return Nanobot(
            pos=Point(numbers[0], numbers[1], numbers[2]),
            radius=numbers[3]
        )


@dataclass(frozen=True)
class SearchArea:

    center: tuple
    bots_in_range: int = 0
    search_size: int = int(1e6)

    def __lt__(self, other):
        if self.bots_in_range > other.bots_in_range:
            return True
        elif self.bots_in_range == other.bots_in_range:
            return (self.search_size, self.dist_to_origin) < (other.search_size, other.dist_to_origin)
        return False

    @property
    def dist_to_origin(self):
        return abs(sum(self.center))


class BotSwarm:

    def __init__(self):
        self.bots = dict()
        self.points = []
        self.radii = []

    @classmethod
    def swarm_from_file(cls, filepath):
        with open(filepath) as f:
            lines = [line.strip() for line in f.readlines()]

        swarm = BotSwarm()
        for line in lines:
            bot = Nanobot.nanobot_from_string(line)
            swarm.bots[bot.pos] = bot
            swarm.points.append((bot.pos.x, bot.pos.y, bot.pos.z))
            swarm.radii.append(bot.radius)

        return swarm

    @classmethod
    def octants(cls, size, center, samples=3):
        points = [center]
        half = max(1, size // 2)
        step = max(1, size // samples)
        minx, maxx = center[0] - half, center[0] + half
        miny, maxy = center[1] - half, center[1] + half
        minz, maxz = center[2] - half, center[2] + half

        for x in range(minx, maxx + 1, step):
            for y in range(miny, maxy + 1, step):
                for z in range(minz, maxz + 1, step):
                    points.append((x, y, z))

        return set(points)

    def distances_from_point(self, point):
        return distance.cdist([point], self.points, metric='cityblock')[0]

    def bots_in_range(self, point, size=0):
        distances = self.distances_from_point(point)
        count = 0
        for i, dist in enumerate(distances):
            if self.radii[i] + size >= dist:
                count += 1

        return count

    def bots_near_strongest_bot(self):
        strongest_bot = None
        for bot in self.bots.values():
            if not strongest_bot or bot.radius > strongest_bot.radius:
                strongest_bot = bot

        return len([d for d in self.distances_from_point(strongest_bot.pos) if d <= strongest_bot.radius])

    def most_central_location(self):

        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        zs = [p[2] for p in self.points]

        avg_x = sum(xs) // len(xs)
        avg_y = sum(ys) // len(ys)
        avg_z = sum(zs) // len(zs)
        min_x = min(xs)
        min_y = min(ys)
        min_z = min(zs)
        max_x = max(xs)
        max_y = max(ys)
        max_z = max(zs)

        size = max(
            abs(max_x - min_x),
            abs(max_y - min_y),
            abs(max_z - min_z),
        ) // 2

        mean_point = (avg_x, avg_y, avg_z)
        search_area = SearchArea(
            center=mean_point,
            bots_in_range=self.bots_in_range(mean_point, size),
            search_size=size)

        heap = [search_area]

        while heap:
            area: SearchArea = heappop(heap)
            if area.search_size == 0:
                return area

            # print(f"{area}")
            points = BotSwarm.octants(area.search_size, area.center)

            print("=== heappop ===")
            print(*area.center)
            # print()

            for point in points:
                print(*point)

            for point in points:
                bots = self.bots_in_range(point, area.search_size // 2)
                new_area = SearchArea(center=point,
                                      bots_in_range=bots,
                                      search_size=area.search_size // 2)

                heappush(heap, new_area)

        return None


class TestEmergencyTeleport(unittest.TestCase):

    def test_sample_swarm(self):
        swarm = BotSwarm.swarm_from_file("input/day_23_test.txt")
        assert swarm.bots_near_strongest_bot() == 7

    def test_bots_in_range(self):
        swarm = BotSwarm.swarm_from_file("input/day_23_test_2.txt")
        assert swarm.bots_in_range((12, 12, 12)) == 5

    def test_most_central_loc(self):
        swarm = BotSwarm.swarm_from_file("input/day_23_test_2.txt")
        search_area = swarm.most_central_location()
        assert search_area.center == (12, 12, 12) and search_area.dist_to_origin == 36

    def test_octants(self):
        points = BotSwarm.octants(1, (11, 12, 10))
        # print(points)

    def test_antagonistic(self):
        swarm = BotSwarm.swarm_from_file("input/day_23_antagonistic.txt")
        search_area = swarm.most_central_location()

        print(len(swarm.bots))

    def test_visualize(self):
        swarm = BotSwarm.swarm_from_file("input/day_23_antagonistic.txt")
        # for point, bot in swarm.bots.items():
        #     print(*list(point), bot.radius)
        search_area = swarm.most_central_location()




    def test_part_1(self):
        swarm = BotSwarm.swarm_from_file("input/day_23.txt")

        print("Part 1:", swarm.bots_near_strongest_bot())
        assert swarm.bots_near_strongest_bot() == 659

    def test_part_2(self):
        swarm = BotSwarm.swarm_from_file("input/day_23.txt")
        search_area = swarm.most_central_location()

        print("Part 2:", search_area.dist_to_origin)
        print(search_area)

        assert search_area.center == (17304966, 29121001, 52139624)
        assert search_area.dist_to_origin == 98565591
        assert search_area.bots_in_range == 975




"""
--- Day 23: Experimental Emergency Teleportation ---
Using your torch to search the darkness of the rocky cavern, you finally locate the man's friend: a small reindeer.

You're not sure how it got so far in this cave. It looks sick - too sick to walk - and too heavy for you to carry all
the way back. Sleighs won't be invented for another 1500 years, of course.

The only option is experimental emergency teleportation.

You hit the "experimental emergency teleportation" button on the device and push I accept the risk on no fewer than 18
different warning messages. Immediately, the device deploys hundreds of tiny nanobots which fly around the cavern,
apparently assembling themselves into a very specific formation. The device lists the X,Y,Z position (pos) for each
nanobot as well as its signal radius (r) on its tiny screen (your puzzle input).

Each nanobot can transmit signals to any integer coordinate which is a distance away from it less than or equal to its
signal radius (as measured by Manhattan distance). Coordinates a distance away of less than or equal to a nanobot's
signal radius are said to be in range of that nanobot.

Before you start the teleportation process, you should determine which nanobot is the strongest (that is, which has the
largest signal radius) and then, for that nanobot, the total number of nanobots that are in range of it, including
itself.

For example, given the following nanobots:

pos=<0,0,0>, r=4
pos=<1,0,0>, r=1
pos=<4,0,0>, r=3
pos=<0,2,0>, r=1
pos=<0,5,0>, r=3
pos=<0,0,3>, r=1
pos=<1,1,1>, r=1
pos=<1,1,2>, r=1
pos=<1,3,1>, r=1

The strongest nanobot is the first one (position 0,0,0) because its signal radius, 4 is the largest. Using that
nanobot's location and signal radius, the following nanobots are in or out of range:

The nanobot at 0,0,0 is distance 0 away, and so it is in range.
The nanobot at 1,0,0 is distance 1 away, and so it is in range.
The nanobot at 4,0,0 is distance 4 away, and so it is in range.
The nanobot at 0,2,0 is distance 2 away, and so it is in range.
The nanobot at 0,5,0 is distance 5 away, and so it is not in range.
The nanobot at 0,0,3 is distance 3 away, and so it is in range.
The nanobot at 1,1,1 is distance 3 away, and so it is in range.
The nanobot at 1,1,2 is distance 4 away, and so it is in range.
The nanobot at 1,3,1 is distance 5 away, and so it is not in range.
In this example, in total, 7 nanobots are in range of the nanobot with the largest signal radius.

Find the nanobot with the largest signal radius. How many nanobots are in range of its signals?
"""
