from collections import Counter
from itertools import chain
import unittest


OPEN = '.'
TREES = '|'
LUMBERYARD = '#'


class LumberArea:

    def __init__(self, grid):
        self.grid = grid
        self.width = len(grid[0])
        self.height = len(grid)

    def __str__(self):
        return '\n'.join([''.join(c for c in line) for line in self.grid])

    @classmethod
    def lumber_area_from_file(cls, filepath):
        with open(filepath) as f:
            lines = [[c for c in line.strip()] for line in f.readlines()]

        return LumberArea(lines)

    def tile(self, x, y):
        if x < 0 or y < 0:
            return None

        if x >= self.width or y >= self.height:
            return None

        return self.grid[y][x]

    def neighbors(self, x, y):
        neighbors = [
            self.tile(x - 1, y),  # west
            self.tile(x + 1, y),  # east
            self.tile(x - 1, y - 1),  # northwest
            self.tile(x - 1, y + 1),  # southwest
            self.tile(x + 1, y - 1),  # northeast
            self.tile(x + 1, y + 1),  # southeast
            self.tile(x, y - 1),  # north
            self.tile(x, y + 1),  # south
        ]

        return [neighbor for neighbor in neighbors if neighbor]

    def step(self):
        new_grid = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                tile = self.tile(x, y)
                neighbors = [
                    self.tile(x - 1, y),  # west
                    self.tile(x + 1, y),  # east
                    self.tile(x - 1, y - 1),  # northwest
                    self.tile(x - 1, y + 1),  # southwest
                    self.tile(x + 1, y - 1),  # northeast
                    self.tile(x + 1, y + 1),  # southeast
                    self.tile(x, y - 1),  # north
                    self.tile(x, y + 1),  # south
                ]
                survey = Counter(neighbors)

                if tile == OPEN:
                    if survey[TREES] >= 3:
                        row.append(TREES)
                    else:
                        row.append(OPEN)
                elif tile == TREES:
                    if survey[LUMBERYARD] >= 3:
                        row.append(LUMBERYARD)
                    else:
                        row.append(TREES)
                elif tile == LUMBERYARD:
                    if survey[LUMBERYARD] >= 1 and survey[TREES] >= 1:
                        row.append(LUMBERYARD)
                    else:
                        row.append(OPEN)
                else:
                    raise Exception("Unknown tile type")

            new_grid.append(row)

        self.grid = new_grid

    def survey(self):
        return Counter(chain.from_iterable(self.grid))

    @property
    def total_value(self):
        survey = self.survey()
        return survey[TREES] * survey[LUMBERYARD]


class TestLumberArea(unittest.TestCase):

    def test_sample_area(self):
        lumber_area = LumberArea.lumber_area_from_file('input/day_18_test.txt')

        for _ in range(10):
            lumber_area.step()

        assert lumber_area.total_value == 1147

    def test_part_1(self):
        lumber_area = LumberArea.lumber_area_from_file('input/day_18.txt')

        for _ in range(10):
            lumber_area.step()

        print("Part 1:", lumber_area.total_value)

    def test_part_2(self):
        stable_after = 531
        cycle_length = 28
        iterations = 1000000000

        lumber_area = LumberArea.lumber_area_from_file('input/day_18.txt')

        # stabilize the pattern
        for _ in range(stable_after):
            lumber_area.step()

        # find the actual answer
        for _ in range((iterations - stable_after) % cycle_length):
            lumber_area.step()

        print("Part 2:", lumber_area.total_value)

    def test_find_cycles(self):
        lumber_area = LumberArea.lumber_area_from_file('input/day_18.txt')

        def cycle_length():
            """
            Find the length of a single cycle; note that this makes a new set every time
            """
            seen = set([lumber_area.total_value])
            while True:
                lumber_area.step()
                new_value = lumber_area.total_value
                if new_value in seen:
                    return len(seen)
                else:
                    seen.add(new_value)

        first_cycle = cycle_length()
        cycles = set([first_cycle])

        while True:
            """
            Keep finding cycles until we have a duplicate cycle; at this point we're hoping that it
            has stabilized.
            """
            cycle = cycle_length()
            if cycle in cycles:
                print(f"stable after {sum(cycles)} with length of {cycle}")
                break
            else:
                cycles.add(cycle)

    def test_vizualization(self):
        from PIL import Image, ImageDraw
        from tqdm import tqdm

        lumber_area = LumberArea.lumber_area_from_file('input/day_18.txt')

        img = Image.new('RGB', (50, 50))

        def save_image(i):
            nonlocal img
            grid = lumber_area.grid
            img = img.point(lambda p: p * 0.9)
            draw = ImageDraw.Draw(img)
            for y in range(50):
                for x in range(50):
                    tile = grid[y][x]
                    if tile == TREES:
                        draw.point((x, y), (0, 255, 0))
                    elif tile == LUMBERYARD:
                        draw.point((x, y), (0, 0, 255))
            img.save(f'output/day_18/{i:03d}.png')

        save_image(0)
        for i in tqdm(range(1, 1000)):
            lumber_area.step()
            save_image(i)


"""
--- Day 18: Settlers of The North Pole ---
On the outskirts of the North Pole base construction project, many Elves are collecting lumber.

The lumber collection area is 50 acres by 50 acres; each acre can be either open ground (.), trees (|), or a lumberyard
(#). You take a scan of the area (your puzzle input).

Strange magic is at work here: each minute, the landscape looks entirely different. In exactly one minute, an open acre
can fill with trees, a wooded acre can be converted to a lumberyard, or a lumberyard can be cleared to open ground (the
lumber having been sent to other projects).

The change to each acre is based entirely on the contents of that acre as well as the number of open, wooded, or
lumberyard acres adjacent to it at the start of each minute. Here, "adjacent" means any of the eight acres surrounding
that acre. (Acres on the edges of the lumber collection area might have fewer than eight adjacent acres; the missing
acres aren't counted.)

In particular:

- An open acre will become filled with trees if three or more adjacent acres contained trees. Otherwise, nothing
happens.
- An acre filled with trees will become a lumberyard if three or more adjacent acres were lumberyards. Otherwise,
nothing happens.
- An acre containing a lumberyard will remain a lumberyard if it was adjacent to at least one other
lumberyard and at least one acre containing trees. Otherwise, it becomes open.

These changes happen across all acres simultaneously, each of them using the state of all acres at the beginning of the
minute and changing to their new form by the end of that same minute. Changes that happen during the minute don't affect
each other.

For example, suppose the lumber collection area is instead only 10 by 10 acres with this initial configuration:

Initial state:
.#.#...|#.
.....#|##|
.|..|...#.
..|#.....#
#.#|||#|#|
...#.||...
.|....|...
||...#|.#|
|.||||..|.
...#.|..|.

After 1 minute:
.......##.
......|###
.|..|...#.
..|#||...#
..##||.|#|
...#||||..
||...|||..
|||||.||.|
||||||||||
....||..|.

After 2 minutes:
.......#..
......|#..
.|.|||....
..##|||..#
..###|||#|
...#|||||.
|||||||||.
||||||||||
||||||||||
.|||||||||

After 3 minutes:
.......#..
....|||#..
.|.||||...
..###|||.#
...##|||#|
.||##|||||
||||||||||
||||||||||
||||||||||
||||||||||

After 4 minutes:
.....|.#..
...||||#..
.|.#||||..
..###||||#
...###||#|
|||##|||||
||||||||||
||||||||||
||||||||||
||||||||||

After 5 minutes:
....|||#..
...||||#..
.|.##||||.
..####|||#
.|.###||#|
|||###||||
||||||||||
||||||||||
||||||||||
||||||||||

After 6 minutes:
...||||#..
...||||#..
.|.###|||.
..#.##|||#
|||#.##|#|
|||###||||
||||#|||||
||||||||||
||||||||||
||||||||||

After 7 minutes:
...||||#..
..||#|##..
.|.####||.
||#..##||#
||##.##|#|
|||####|||
|||###||||
||||||||||
||||||||||
||||||||||

After 8 minutes:
..||||##..
..|#####..
|||#####|.
||#...##|#
||##..###|
||##.###||
|||####|||
||||#|||||
||||||||||
||||||||||

After 9 minutes:
..||###...
.||#####..
||##...##.
||#....###
|##....##|
||##..###|
||######||
|||###||||
||||||||||
||||||||||

After 10 minutes:
.||##.....
||###.....
||##......
|##.....##
|##.....##
|##....##|
||##.####|
||#####|||
||||#|||||
||||||||||

After 10 minutes, there are 37 wooded acres and 31 lumberyards. Multiplying the number of wooded acres by the number of
lumberyards gives the total resource value after ten minutes: 37 * 31 = 1147.

What will the total resource value of the lumber collection area be after 10 minutes?
"""
