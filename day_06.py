import numpy as np
from collections import deque


lines = [line.strip().split(",") for line in open("input/day_06.txt").readlines()]


class Group:

    def __init__(self, x, y, i):
        self.x = x
        self.y = y
        self.i = i
        self.is_infinite = False
        self.cell_count = 0

    def __repr__(self):
        return f"Group(" \
            f"x={self.x}, " \
            f"y={self.y}, " \
            f"i={self.i}, " \
            f"is_infinite={self.is_infinite}, " \
            f"cell_count={self.cell_count})"


def make_groups():
    group_list = []
    for i, line in enumerate(lines):
        x = int(line[0])
        y = int(line[1])
        group_list.append(Group(
            i=i,
            x=x,
            y=y
        ))

    return group_list


def mark_grid(size, groups):
    """

    :param size:
    :param groups:
    :return:
    """
    grid = (np.ones((size, size, 2)) * -1).astype(int)  # grid is [x][y](i, dist)

    seen = set()
    queue = deque()

    for group in groups:
        cell = (group.x, group.y, group.i, 0)
        queue.append(cell)
        seen.add((group.x, group.y, group.i))

    while queue:
        x, y, i, dist = queue.pop()

        if x < 0 or y < 0 or x > size - 1 or y > size - 1:
            continue

        _, prev_dist = grid[x][y]  # the previous values in the cell

        if dist < prev_dist or prev_dist == -1:  # -1 is an uninitialized cell
            grid[x][y] = (i, dist)
        elif dist == prev_dist:
            grid[x][y] = (i, dist)
        else:
            continue

        for neighbor in neighbors(x, y):
            if (*neighbor, i) not in seen:
                queue.appendleft((*neighbor, i, dist + 1))
                seen.add((*neighbor, i))

    return grid


def neighbors(x, y):
    return (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)


def biggest_non_inf_group(groups, grid, size):
    """
    Go through the grid, count the size of each group, and mark which ones are touching the edge and will thus
    expand infinitely. Sort the non-infinite groups by size and return the biggest one.
    """
    for x in range(size):
        for y in range(size):
            i, dist = grid[x][y]

            if i == 10e6:  # this is the default value; the cell was never visited
                continue

            group = groups[i]
            group.cell_count += 1

            if x == 0 or y == 0 or x == size - 1 or y == size - 1:
                group.is_infinite = True

    non_inf_groups = [group for group in groups if not group.is_infinite]
    non_inf_groups.sort(key=lambda g: g.cell_count)

    return non_inf_groups[-1]


def most_central_region(groups, size=400):
    avg_x = sum([group.x for group in groups]) // len(groups)
    avg_y = sum([group.y for group in groups]) // len(groups)
    central_cells = []

    seen = {(avg_x, avg_y)}
    queue = deque([(avg_x, avg_y)])

    while queue:
        x, y = queue.pop()

        if x < 0 or y < 0 or x > size - 1 or y > size - 1:
            continue

        if not is_within_dist_of_all(x, y, groups):
            continue

        central_cells.append((x, y))

        for point in neighbors(x, y):
            if point not in seen:
                queue.append(point)
                seen.add(point)

    return len(central_cells)


def distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def is_within_dist_of_all(x, y, groups):
    return sum([distance(x, y, group.x, group.y) for group in groups]) < 10000


def main():
    """
    We're overloading numpy a bit here; the cells will contain [distance, point_id] where distance is the
    Taxi / Manhattan distance, and point_id is the integer ID of the point, or -1 if there is a tie.
    """
    groups = make_groups()
    size = 400

    grid = mark_grid(size, groups)

    # print("Part 1:", biggest_non_inf_group(groups, grid, size))

    # print("Part 2:", most_central_region(groups))


if __name__ == '__main__':
    main()


"""
--- Day 6: Chronal Coordinates ---
The device on your wrist beeps several times, and once again you feel like you're falling.

"Situation critical," the device announces. "Destination indeterminate. Chronal interference detected. 
Please specify new target coordinates."

The device then produces a list of coordinates (your puzzle input). Are they places it thinks are safe or 
dangerous? It recommends you check manual page 729. The Elves did not give you a manual.

If they're dangerous, maybe you can minimize the danger by finding the coordinate that gives the largest 
distance from the other points.

Using only the Manhattan distance, determine the area around each coordinate by counting the number of 
integer X,Y locations that are closest to that coordinate (and aren't tied in distance to any other coordinate).

Your goal is to find the size of the largest area that isn't infinite. For example, consider the following 
list of coordinates:

1, 1
1, 6
8, 3
3, 4
5, 5
8, 9
If we name these coordinates A through F, we can draw them on a grid, putting 0,0 at the top left:

..........
.A........
..........
........C.
...D......
.....E....
.B........
..........
..........
........F.
This view is partial - the actual grid extends infinitely in all directions. Using the Manhattan distance, 
each location's closest coordinate can be determined, shown here in lowercase:

aaaaa.cccc
aAaaa.cccc
aaaddecccc
aadddeccCc
..dDdeeccc
bb.deEeecc
bBb.eeee..
bbb.eeefff
bbb.eeffff
bbb.ffffFf
Locations shown as . are equally far from two or more coordinates, and so they don't count as being closest to any.

In this example, the areas of coordinates A, B, C, and F are infinite - while not shown here, their areas extend 
forever outside the visible grid. However, the areas of coordinates D and E are finite: D is closest to 9 locations, 
and E is closest to 17 (both including the coordinate's location itself). Therefore, in this example, the size of the 
largest area is 17.

What is the size of the largest area that isn't infinite?

--- Part Two ---
On the other hand, if the coordinates are safe, maybe the best you can do is try to find a region near as many coordinates as possible.

For example, suppose you want the sum of the Manhattan distance to all of the coordinates to be less than 32. For each location, add up the distances to all of the given coordinates; if the total of those distances is less than 32, that location is within the desired region. Using the same coordinates as above, the resulting region looks like this:

..........
.A........
..........
...###..C.
..#D###...
..###E#...
.B.###....
..........
..........
........F.
In particular, consider the highlighted location 4,3 located at the top middle of the region. Its calculation is
 as follows, where abs() is the absolute value function:

Distance to coordinate A: abs(4-1) + abs(3-1) =  5
Distance to coordinate B: abs(4-1) + abs(3-6) =  6
Distance to coordinate C: abs(4-8) + abs(3-3) =  4
Distance to coordinate D: abs(4-3) + abs(3-4) =  2
Distance to coordinate E: abs(4-5) + abs(3-5) =  3
Distance to coordinate F: abs(4-8) + abs(3-9) = 10
Total distance: 5 + 6 + 4 + 2 + 3 + 10 = 30
Because the total distance to all coordinates (30) is less than 32, the location is within the region.

This region, which also includes coordinates D and E, has a total size of 16.

Your actual region will need to be much larger than this example, though, instead including all locations with a 
total distance of less than 10000.

What is the size of the region containing all locations which have a total distance to all given coordinates of 
less than 10000?
"""
