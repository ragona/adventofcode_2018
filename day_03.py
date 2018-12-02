import re
from dataclasses import dataclass
from collections import defaultdict
import unittest


rectangle_parser = re.compile(r"#(\d+)\s@\s(\d+,\d+):\s(\d+x\d+)")
with open("input/day_03.txt", 'r') as input_file:
    lines = [line.strip() for line in input_file.readlines()]


@dataclass
class Rectangle:

    uid: str
    x: int
    y: int
    width: int
    height: int

    def __str__(self):
        return f"Rectangle('#{self.uid} @ {self.x},{self.y}: {self.width}x{self.height}')"

    @classmethod
    def rectangle_from_string(cls, string):
        """
        Converts a line from the input file into a Rectangle, using the following definition:

        A claim like #123 @ 3,2: 5x4 means that claim ID 123 specifies a rectangle 3 inches from the left edge,
        2 inches from the top edge, 5 inches wide, and 4 inches tall.
        """
        try:
            result = rectangle_parser.match(string)
            uid = result.group(1)
            x, y = [int(i) for i in result.group(2).split(',')]
            w, h = [int(i) for i in result.group(3).split('x')]
        except (AttributeError, TypeError):
            raise ValueError(f"Failed to parse: '{string}'")

        return Rectangle(uid, x, y, w, h)

    def points(self):
        points = []
        for x in range(self.x, self.x + self.width):
            for y in range(self.y, self.y + self.height):
                points.append((x, y))
        return points


def rectangles():
    return [Rectangle.rectangle_from_string(line) for line in lines]


def grid_map():
    """
    Returns a map with points mapped an int for the number of times the point has been seen

    :return: map[(x,y)]count
    """
    grid = defaultdict(int)

    for rect in rectangles():
        for point in rect.points():
            grid[point] += 1

    return grid


def total_overlapped_cells_list(grid):
    total = 0
    for row in grid:
        for count in row:
            if count > 1:
                total += 1

    return total


def total_overlapped_cells_map(grid):
    return len([x for x in grid.values() if x > 1])


class TestFabricOverlap(unittest.TestCase):

    def setUp(self):
        self.grid = grid_map()

    def test_part_1(self):
        print("Part 1:", total_overlapped_cells_map(self.grid))

    def test_part_2(self):
        for rect in rectangles():
            points = rect.points()
            if sum(self.grid[point] for point in points) == len(points):
                print("Part 2:", rect)


if __name__ == '__main__':
    unittest.main()


"""
--- Day 3: No Matter How You Slice It ---
The Elves managed to locate the chimney-squeeze prototype fabric for Santa's suit (thanks to someone who helpfully
wrote its box IDs on the wall of the warehouse in the middle of the night). Unfortunately, anomalies are still
affecting them - nobody can even agree on how to cut the fabric.

The whole piece of fabric they're working on is a very large square - at least 1000 inches on each side.

Each Elf has made a claim about which area of fabric would be ideal for Santa's suit. All claims have an ID and consist
of a single rectangle with edges parallel to the edges of the fabric. Each claim's rectangle is defined as follows:

The number of inches between the left edge of the fabric and the left edge of the rectangle.
The number of inches between the top edge of the fabric and the top edge of the rectangle.
The width of the rectangle in inches.
The height of the rectangle in inches.
A claim like #123 @ 3,2: 5x4 means that claim ID 123 specifies a rectangle 3 inches from the left edge, 2 inches from
the top edge, 5 inches wide, and 4 inches tall. Visually, it claims the square inches of fabric represented by # (and
ignores the square inches of fabric represented by .) in the diagram below:

...........
...........
...#####...
...#####...
...#####...
...#####...
...........
...........
...........
The problem is that many of the claims overlap, causing two or more claims to cover part of the same areas. For example,
consider the following claims:

#1 @ 1,3: 4x4
#2 @ 3,1: 4x4
#3 @ 5,5: 2x2
Visually, these claim the following areas:

........
...2222.
...2222.
.11XX22.
.11XX22.
.111133.
.111133.
........
The four square inches marked with X are claimed by both 1 and 2. (Claim 3, while adjacent to the others, does not
overlap either of them.)

If the Elves all proceed with their own plans, none of them will have enough fabric. How many square inches of fabric
are within two or more claims?
"""
