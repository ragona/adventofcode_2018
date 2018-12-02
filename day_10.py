import unittest
import re
import numpy as np
import matplotlib.pyplot as plt


pattern = re.compile("position=<(.+)> velocity=<(.+)>")
lines = [line.strip() for line in open("input/day_10.txt").readlines()]


class Starmap:

    def __init__(self, star_count):
        self.star_count = star_count
        self.positions = np.zeros((star_count, 2))
        self.velocities = np.zeros((star_count, 2))

    @classmethod
    def starmap_from_string(cls, lines):
        starmap = Starmap(len(lines))

        for i, line in enumerate(lines):
            parsed = pattern.match(line.strip())
            position, velocity = parsed.groups()
            position = [int(n) for n in position.split(",")]
            velocity = [int(n) for n in velocity.split(",")]

            starmap.positions[i] = position
            starmap.velocities[i] = velocity

        return starmap

    @property
    def ydiff(self):
        return max(self.positions[:, 1]) - min(self.positions[:, 1])

    def step_forward(self):
        self.positions += self.velocities

    def step_backwards(self):
        self.positions -= self.velocities

    def find_convergence(self):
        start = 0
        ydiff = self.ydiff
        while True:
            self.step_forward()
            start += 1
            if self.ydiff < ydiff:
                ydiff = self.ydiff
            else:
                self.step_backwards()  # we hit this when we go too far; rewind one step
                break

        print(start - 1)

    def draw(self):
        plt.scatter(self.positions[:, 0], self.positions[:, 1])
        plt.gca().invert_yaxis()
        plt.show()


def main():
    starmap = Starmap.starmap_from_string(lines)
    starmap.find_convergence()
    starmap.draw()


if __name__ == '__main__':
    main()


class TestStarmap(unittest.TestCase):

    test_map = """position=< 9,  1> velocity=< 0,  2>
    position=< 7,  0> velocity=<-1,  0>
    position=< 3, -2> velocity=<-1,  1>
    position=< 6, 10> velocity=<-2, -1>
    position=< 2, -4> velocity=< 2,  2>
    position=<-6, 10> velocity=< 2, -2>
    position=< 1,  8> velocity=< 1, -1>
    position=< 1,  7> velocity=< 1,  0>
    position=<-3, 11> velocity=< 1, -2>
    position=< 7,  6> velocity=<-1, -1>
    position=<-2,  3> velocity=< 1,  0>
    position=<-4,  3> velocity=< 2,  0>
    position=<10, -3> velocity=<-1,  1>
    position=< 5, 11> velocity=< 1, -2>
    position=< 4,  7> velocity=< 0, -1>
    position=< 8, -2> velocity=< 0,  1>
    position=<15,  0> velocity=<-2,  0>
    position=< 1,  6> velocity=< 1,  0>
    position=< 8,  9> velocity=< 0, -1>
    position=< 3,  3> velocity=<-1,  1>
    position=< 0,  5> velocity=< 0, -1>
    position=<-2,  2> velocity=< 2,  0>
    position=< 5, -2> velocity=< 1,  2>
    position=< 1,  4> velocity=< 2,  1>
    position=<-2,  7> velocity=< 2, -2>
    position=< 3,  6> velocity=<-1, -1>
    position=< 5,  0> velocity=< 1,  0>
    position=<-6,  0> velocity=< 2,  0>
    position=< 5,  9> velocity=< 1, -2>
    position=<14,  7> velocity=<-2,  0>
    position=<-3,  6> velocity=< 2, -1>"""

    def test_starmap(self):
        starmap = Starmap.starmap_from_string(
            lines=TestStarmap.test_map.strip().split('\n'),
        )

        starmap.find_convergence()
        starmap.draw()





"""
--- Day 10: The Stars Align ---
It's no use; your navigation system simply isn't capable of providing walking directions in the arctic circle, and 
certainly not in 1018.

The Elves suggest an alternative. In times like these, North Pole rescue operations will arrange points of light in 
the sky to guide missing Elves back to base. Unfortunately, the message is easy to miss: the points move slowly enough 
that it takes hours to align them, but have so much momentum that they only stay aligned for a second. If you blink at 
the wrong time, it might be hours before another message appears.

You can see these points of light floating in the distance, and record their position in the sky and their velocity, 
the relative change in position per second (your puzzle input). The coordinates are all given from your perspective; 
given enough time, those positions and velocities will move the points into a cohesive message!

Rather than wait, you decide to fast-forward the process and calculate what the points will eventually spell.

For example, suppose you note the following points:

position=< 9,  1> velocity=< 0,  2>
position=< 7,  0> velocity=<-1,  0>
position=< 3, -2> velocity=<-1,  1>
position=< 6, 10> velocity=<-2, -1>
position=< 2, -4> velocity=< 2,  2>
position=<-6, 10> velocity=< 2, -2>
position=< 1,  8> velocity=< 1, -1>
position=< 1,  7> velocity=< 1,  0>
position=<-3, 11> velocity=< 1, -2>
position=< 7,  6> velocity=<-1, -1>
position=<-2,  3> velocity=< 1,  0>
position=<-4,  3> velocity=< 2,  0>
position=<10, -3> velocity=<-1,  1>
position=< 5, 11> velocity=< 1, -2>
position=< 4,  7> velocity=< 0, -1>
position=< 8, -2> velocity=< 0,  1>
position=<15,  0> velocity=<-2,  0>
position=< 1,  6> velocity=< 1,  0>
position=< 8,  9> velocity=< 0, -1>
position=< 3,  3> velocity=<-1,  1>
position=< 0,  5> velocity=< 0, -1>
position=<-2,  2> velocity=< 2,  0>
position=< 5, -2> velocity=< 1,  2>
position=< 1,  4> velocity=< 2,  1>
position=<-2,  7> velocity=< 2, -2>
position=< 3,  6> velocity=<-1, -1>
position=< 5,  0> velocity=< 1,  0>
position=<-6,  0> velocity=< 2,  0>
position=< 5,  9> velocity=< 1, -2>
position=<14,  7> velocity=<-2,  0>
position=<-3,  6> velocity=< 2, -1>
Each line represents one point. Positions are given as <X, Y> pairs: X represents how far left (negative) or right 
(positive) the point appears, while Y represents how far up (negative) or down (positive) the point appears.

At 0 seconds, each point has the position given. Each second, each point's velocity is added to its position. So, a 
point with velocity <1, -2> is moving to the right, but is moving upward twice as quickly. If this point's initial 
position were <3, 9>, after 3 seconds, its position would become <6, 3>.

Over time, the points listed above would move like this:

Initially:
........#.............
................#.....
.........#.#..#.......
......................
#..........#.#.......#
...............#......
....#.................
..#.#....#............
.......#..............
......#...............
...#...#.#...#........
....#..#..#.........#.
.......#..............
...........#..#.......
#...........#.........
...#.......#..........

After 1 second:
......................
......................
..........#....#......
........#.....#.......
..#.........#......#..
......................
......#...............
....##.........#......
......#.#.............
.....##.##..#.........
........#.#...........
........#...#.....#...
..#...........#.......
....#.....#.#.........
......................
......................

After 2 seconds:
......................
......................
......................
..............#.......
....#..#...####..#....
......................
........#....#........
......#.#.............
.......#...#..........
.......#..#..#.#......
....#....#.#..........
.....#...#...##.#.....
........#.............
......................
......................
......................

After 3 seconds:
......................
......................
......................
......................
......#...#..###......
......#...#...#.......
......#...#...#.......
......#####...#.......
......#...#...#.......
......#...#...#.......
......#...#...#.......
......#...#..###......
......................
......................
......................
......................

After 4 seconds:
......................
......................
......................
............#.........
........##...#.#......
......#.....#..#......
.....#..##.##.#.......
.......##.#....#......
...........#....#.....
..............#.......
....#......#...#......
.....#.....##.........
...............#......
...............#......
......................
......................
After 3 seconds, the message appeared briefly: HI. Of course, your message will be much longer and will take many 
more seconds to appear.

What message will eventually appear in the sky?
"""
