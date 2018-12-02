from collections import namedtuple, defaultdict, deque
from copy import copy
import re
import unittest


def number_grabber(string):
    return [int(s) for s in re.findall(r"\d+", string)]


Bounds = namedtuple('Bounds', ['min_y', 'max_y', 'min_x', 'max_x'])


class Point(namedtuple('Point', ['x', 'y'])):

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    @property
    def down(self):
        return Point(self.x, self.y + 1)

    @property
    def left(self):
        return Point(self.x - 1, self.y)

    @property
    def right(self):
        return Point(self.x + 1, self.y)

    @property
    def up(self):
        return Point(self.x, self.y - 1)


left = Point(-1, 0)
right = Point(1, 0)


class ClayLine:

    def __init__(self, numbers, axis):
        """
        Sample: 'x=495, y=2..7' > ClayLine(numbers=[495, 2, 7], axis='x')
        """

        self.points = set()

        if axis == 'x':
            x = numbers[0]
            y = numbers[1]
            end = numbers[2]
            for i in range(y, end + 1):
                self.points.add(Point(x, i))
        else:
            y = numbers[0]
            x = numbers[1]
            end = numbers[2]
            for i in range(x, end + 1):
                self.points.add(Point(i, y))

    def __repr__(self):
        return f"ClayLine(points={''.join([f'({point.x},{point.y})' for point in self.points])})"


class Reservoir:

    def __init__(self):
        self.spring = Point(500, 0)
        self.grid = defaultdict(lambda: '.')
        self.bounds = None

    def __repr__(self):
        ret = ['\n']
        grid = copy(self.grid)  # accessing a default dict is dangerous; we'll end up expanding the grid
        bounds = self.bounds
        for y in range(bounds.min_y - 1, bounds.max_y + 2):
            ret.append(f"{y:4} ")
            for x in range(bounds.min_x - 1, bounds.max_x + 2):
                if (x, y) == self.spring:
                    ret.append('+')
                else:
                    ret.append(grid[Point(x, y)])
            ret.append('\n')

        return ''.join([''.join(line) for line in ret])

    @classmethod
    def reservoir_from_file(cls, filepath):
        reservoir = Reservoir()

        with open(filepath) as f:
            lines = [line.strip() for line in f.readlines()]

        all_clay = set()

        for line in lines:
            clay = ClayLine(numbers=number_grabber(line), axis=line[0])
            all_clay |= clay.points

        for point in all_clay:
            reservoir.grid[point] = "#"

        reservoir.bounds = reservoir._bounds()

        return reservoir

    def _bounds(self):
        """
        We just set this once -- otherwise we end up expanding the bounds with falling water!
        """
        points = self.grid.keys() | {self.spring}
        min_x = min([p.x for p in points])
        max_x = max([p.x for p in points])
        min_y = min([p.y for p in points])
        max_y = max([p.y for p in points])

        return Bounds(
            min_y=min_y,
            max_y=max_y,
            min_x=min_x,
            max_x=max_x,
        )

    def fill(self):

        def passable(point):
            return self.grid[point] == '|' or self.grid[point] == '.'

        def in_bounds(point):
            return bounds.max_y + 1 >= point.y >= bounds.min_y

        def valid(point):
            return passable(point) and in_bounds(point)

        def fall(point):
            self.grid[point] = '|'
            down = point.down
            if valid(down) and down not in traversed:
                stack.append(down)
                traversed.add(down)

        def flow(point, direction):
            """
            Flows towards the direction until it hits a wall or an open space. Returns whether it is enclosed
            in the direction.
            """
            step = point
            while True:
                if passable(step.down):  # if we can fall, we're not contained
                    fall(step)
                    return False
                elif not in_bounds(step):
                    return False
                elif not passable(step):
                    return True
                self.grid[step] = "|"
                step = step + direction

        def settle(point, direction):
            step = point
            while valid(step):
                self.grid[step] = '~'
                step = step + direction

        bounds = self.bounds
        first = Point(self.spring.x, self.spring.y + 1)
        stack = deque([first])
        traversed = set()

        while stack:
            curr = stack.pop()

            if passable(curr.down):
                node = curr
                while valid(node):
                    self.grid[node] = '|'
                    node = node.down

            closed_left = flow(curr, left)
            closed_right = flow(curr, right)

            if closed_left and closed_right:
                settle(curr, left)
                settle(curr.right, right)
                stack.append(curr.up)

    @property
    def wet_count(self):
        """
        Note that the first few bits of falling water from the spring don't count; you only count things that
        are >= to the piece of clay that you find in the scan. (And you also don't count the infinitely falling
        water below the last clay in the scan.)
        """
        min_clay = min(point.y for point, char in self.grid.items() if char == "#")
        return sum(
            1 for point, char in self.grid.items()
            if char in {'|', '~'}
            and min_clay <= point.y <= self.bounds.max_y
        )

    @property
    def settled_count(self):
        min_clay = min(point.y for point, char in self.grid.items() if char == "#")
        return sum(
            1 for point, char in self.grid.items()
            if char == '~'
            and min_clay <= point.y <= self.bounds.max_y
        )


class TestReservoir(unittest.TestCase):

    def test_reservoir(self):
        reservoir = Reservoir.reservoir_from_file("input/day_17.txt")
        reservoir.fill()

        wet = reservoir.wet_count
        settled = reservoir.settled_count

        print("Part 1:", wet)
        print("Part 2:", settled)

        assert wet == 38451
        assert settled == 28142


"""
--- Day 17: Reservoir Research ---
You arrive in the year 18. If it weren't for the coat you got in 1018, you would be very cold: the North Pole base
hasn't even been constructed.

Rather, it hasn't been constructed yet. The Elves are making a little progress, but there's not a lot of liquid water in
this climate, so they're getting very dehydrated. Maybe there's more underground?

You scan a two-dimensional vertical slice of the ground nearby and discover that it is mostly sand with veins of clay.
The scan only provides data with a granularity of square meters, but it should be good enough to determine how much
water is trapped there. In the scan, x represents the distance to the right, and y represents the distance down. There
is also a spring of water near the surface at x=500, y=0. The scan identifies which square meters are clay (your puzzle
input).

For example, suppose your scan shows the following veins of clay:

x=495, y=2..7
y=7, x=495..501
x=501, y=3..7
x=498, y=2..4
x=506, y=1..2
x=498, y=10..13
x=504, y=10..13
y=13, x=498..504

Rendering clay as #, sand as ., and the water spring as +, and with x increasing to the right and y increasing downward,
this becomes:

   44444455555555
   99999900000000
   45678901234567
 0 ......+.......
 1 ............#.
 2 .#..#.......#.
 3 .#..#..#......
 4 .#..#..#......
 5 .#.....#......
 6 .#.....#......
 7 .#######......
 8 ..............
 9 ..............
10 ....#.....#...
11 ....#.....#...
12 ....#.....#...
13 ....#######...

The spring of water will produce water forever. Water can move through sand, but is blocked by clay. Water always moves
down when possible, and spreads to the left and right otherwise, filling space that has clay on both sides and falling
out otherwise.

For example, if five squares of water are created, they will flow downward until they reach the clay and settle there.
Water that has come to rest is shown here as ~, while sand through which water has passed (but which is now dry again)
is shown as |:

......+.......
......|.....#.
.#..#.|.....#.
.#..#.|#......
.#..#.|#......
.#....|#......
.#~~~~~#......
.#######......
..............
..............
....#.....#...
....#.....#...
....#.....#...
....#######...

Two squares of water can't occupy the same location. If another five squares of water are created, they will settle on
the first five, filling the clay reservoir a little more:

......+.......
......|.....#.
.#..#.|.....#.
.#..#.|#......
.#..#.|#......
.#~~~~~#......
.#~~~~~#......
.#######......
..............
..............
....#.....#...
....#.....#...
....#.....#...
....#######...

Water pressure does not apply in this scenario. If another four squares of water are created, they will stay on the
right side of the barrier, and no water will reach the left side:

......+.......
......|.....#.
.#..#.|.....#.
.#..#~~#......
.#..#~~#......
.#~~~~~#......
.#~~~~~#......
.#######......
..............
..............
....#.....#...
....#.....#...
....#.....#...
....#######...

At this point, the top reservoir overflows. While water can reach the tiles above the surface of the water, it cannot
settle there, and so the next five squares of water settle like this:

......+.......
......|.....#.
.#..#||||...#.
.#..#~~#|.....
.#..#~~#|.....
.#~~~~~#|.....
.#~~~~~#|.....
.#######|.....
........|.....
........|.....
....#...|.#...
....#...|.#...
....#~~~~~#...
....#######...

Note especially the leftmost |: the new squares of water can reach this tile, but cannot stop there. Instead,
eventually, they all fall to the right and settle in the reservoir below.

After 10 more squares of water, the bottom reservoir is also full:

......+.......
......|.....#.
.#..#||||...#.
.#..#~~#|.....
.#..#~~#|.....
.#~~~~~#|.....
.#~~~~~#|.....
.#######|.....
........|.....
........|.....
....#~~~~~#...
....#~~~~~#...
....#~~~~~#...
....#######...

Finally, while there is nowhere left for the water to settle, it can reach a few more tiles before overflowing beyond
the bottom of the scanned data:

......+.......    (line not counted: above minimum y value)
......|.....#.
.#..#||||...#.
.#..#~~#|.....
.#..#~~#|.....
.#~~~~~#|.....
.#~~~~~#|.....
.#######|.....
........|.....
...|||||||||..
...|#~~~~~#|..
...|#~~~~~#|..
...|#~~~~~#|..
...|#######|..
...|.......|..    (line not counted: below maximum y value)
...|.......|..    (line not counted: below maximum y value)
...|.......|..    (line not counted: below maximum y value)

How many tiles can be reached by the water? To prevent counting forever, ignore tiles with a y coordinate smaller than
the smallest y coordinate in your scan data or larger than the largest one. Any x coordinate is valid. In this example,
the lowest y coordinate given is 1, and the highest is 13, causing the water spring (in row 0) and the water falling off
the bottom of the render (in rows 14 through infinity) to be ignored.

So, in the example above, counting both water at rest (~) and other sand tiles the water can hypothetically reach (|),
the total number of tiles the water can reach is 57.

How many tiles can the water reach within the range of y values in your scan?
"""

