from collections import namedtuple, defaultdict
from dataclasses import dataclass
import unittest


Point = namedtuple('Point', ['x', 'y'])


@dataclass
class Unit:

    races = {"G", "E"}

    race: str
    position: Point
    attack: int = 3
    health: int = 200

    @property
    def dead(self):
        return self.health <= 0


@dataclass
class Path:

    start: Point
    goal: Point
    first_step: Point
    length: int


class Cavern:

    def __init__(self, lines, save_the_elves=False):
        self.lines = [[c for c in line] for line in lines]  # split into mutable lists
        self.width = len(self.lines[0])
        self.height = len(self.lines)
        self.units = {}
        self.save_the_elves = save_the_elves

        for y, line in enumerate(self.lines):
            for x, tile in enumerate(line):
                if tile in Unit.races:
                    unit = Unit(race=tile, position=Point(x, y))
                    if save_the_elves and unit.race == "E":
                        unit.attack = 25
                    self.units[Point(x, y)] = unit

    def __repr__(self):
        lines = []
        units = self.sorted_units()

        for y in range(self.height):
            line = ''.join(self.lines[y]).strip()
            line_units = []
            for unit in units:
                if unit.position.y == y:
                    line_units.append(f"{unit.race}({unit.health})")
            line += '   ' + (', '.join(line_units)) + '\n'
            lines.append(line)
        return ''.join(lines)

    @classmethod
    def cavern_from_file(cls, filepath, save_the_elves=False):

        with open(filepath) as f:
            lines = f.readlines()

        cavern = Cavern(lines, save_the_elves)

        return cavern

    @classmethod
    def neighbors(cls, point):
        return [
            Point(point.x, point.y - 1),  # north
            Point(point.x - 1, point.y),  # west
            Point(point.x + 1, point.y),  # east
            Point(point.x, point.y + 1),  # south
        ]

    def tile(self, point):
        return self.lines[point.y][point.x]

    def set_tile(self, point, value):
        self.lines[point.y][point.x] = value

    def try_to_move_unit(self, unit):
        """
        To move, the unit first considers the squares that are in range (of an enemy) and determines which of those
        squares it could reach in the fewest steps. A step is a single movement to any adjacent (immediately up, down,
        left, or right) open (.) square.

        Units cannot move into walls or other units. The unit does this while considering the current positions of units
        and does not do any prediction about where units will be later. If the unit cannot reach (find an open path to)
        any of the squares that are in range, it ends its turn. If multiple squares are in range and tied for being
        reachable in the fewest steps, the square which is first in reading order is chosen.
        """
        enemies = self.enemy_units(unit.race)

        paths = []
        for enemy in enemies:
            for point in Cavern.neighbors(enemy.position):
                if self.tile(point) == '.':
                    path = self.find_path(unit.position, point)
                    if path is not None:
                        paths.append(path)

        if not paths:
            return

        paths.sort(key=lambda p: p.length)  # sort by total steps first
        shortest = [path for path in paths if path.length == paths[0].length]  # find all paths of shortest length

        if len(shortest) > 1:
            shortest.sort(key=lambda p: (p.goal.y, p.goal.x))  # tie break with reading order on goal tile

        """
        At this point we know where we want to go, but not necessarily how we want to get there. 
        """
        target = shortest[0].goal
        if target in self.neighbors(unit.position):
            new_position = target
        else:
            paths = []
            for point in self.neighbors(unit.position):
                if self.tile(point) == '.':
                    candidate = self.find_path(point, target)
                    if candidate:
                        paths.append(candidate)
            paths.sort(key=lambda p: (p.length, p.start.y, p.start.x))
            new_position = paths[0].start

        if new_position in self.units:
            raise Exception("tried to move to an occupied tile")

        self.move_unit(unit, new_position)

    def enemy_units(self, race):
        return [unit for pos, unit in self.units.items() if unit.race != race]

    def attackable_enemy(self, unit):
        enemies = []
        for point in Cavern.neighbors(unit.position):
            if point in self.units:
                if self.units[point].race != unit.race:
                    enemies.append(self.units[point])

        if not enemies:
            return None

        return sorted(enemies, key=lambda enemy: enemy.health)[0]

    def move_unit(self, unit, new_position):
        self.remove_unit(unit)
        unit.position = new_position
        self.add_unit(unit)

    def remove_unit(self, unit):
        del(self.units[unit.position])
        self.lines[unit.position.y][unit.position.x] = '.'

    def add_unit(self, unit):
        self.units[unit.position] = unit
        self.lines[unit.position.y][unit.position.x] = unit.race

    def sorted_units(self):
        return sorted(self.units.values(), key=lambda u: (u.position.y, u.position.x))

    def find_path(self, start, goal):
        """
        Straight wikipedia A*
        """
        paths = []

        def reconstruct_path(came_from, current):
            total_path = [current]
            while current in came_from.keys():
                current = came_from[current]
                total_path.append(current)

            return Path(goal=goal,
                        start=start,
                        first_step=total_path[-2],  # 0 is goal, -1 is start, -2 is first step
                        length=len(total_path))

        def heuristic_cost_estimate(a, b):
            return abs(a.x - b.x) + abs(a.y - b.y)

        closed_set = set()
        open_set = {start}
        came_from = dict()
        g_score = defaultdict(lambda: 10e6)
        g_score[start] = 0
        f_score = defaultdict(lambda: 10e6)
        f_score[start] = heuristic_cost_estimate(start, goal)

        while open_set:
            lowest = None
            lowest_score = 10e6
            for point in open_set:
                if f_score[point] < lowest_score:
                    lowest = point
                    lowest_score = f_score[point]
            current = lowest

            if current == goal:
                return reconstruct_path(came_from, current)

            open_set.remove(current)
            closed_set.add(current)

            for neighbor in Cavern.neighbors(current):
                if self.tile(neighbor) != '.':
                    closed_set.add(neighbor)

                if neighbor in closed_set:
                    continue

                tentative_gscore = g_score[current] + 1

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_gscore >= g_score[neighbor]:
                    continue

                came_from[neighbor] = current
                g_score[neighbor] = tentative_gscore
                f_score[neighbor] = g_score[neighbor] + heuristic_cost_estimate(neighbor, goal)


class Battle:

    class BattleComplete(BaseException):
        pass

    def __init__(self, cavern):
        self.cavern = cavern
        self.num_rounds = 0

    def round(self):
        sorted_units = self.cavern.sorted_units()
        for unit in sorted_units:
            if unit.dead:
                continue

            if len(self.cavern.enemy_units(unit.race)) == 0:
                raise Battle.BattleComplete()

            if self.attack_nearby_enemy(unit):
                continue

            self.cavern.try_to_move_unit(unit)
            self.attack_nearby_enemy(unit)

        self.num_rounds += 1

    def attack_nearby_enemy(self, unit):
        nearby_enemy = self.cavern.attackable_enemy(unit)
        if nearby_enemy:
            nearby_enemy.health -= unit.attack
            if nearby_enemy.dead:
                self.cavern.remove_unit(nearby_enemy)

            return True

        return False

    def execute(self, limit=10e10, verbose=False):
        while self.num_rounds < limit:
            try:
                self.round()
            except Battle.BattleComplete:
                return self.num_rounds, self.num_rounds * sum([unit.health for unit in self.cavern.units.values()])

            if verbose:
                print(f"After {self.num_rounds} rounds:")
                print(self.cavern)


class TestBattle(unittest.TestCase):

    def test_sample_battle_1(self):
        self.harness("input/day_15_test.txt", 47, 27730)

    def test_sample_battle_2(self):
        self.harness("input/day_15_test_2.txt", 37, 36334)

    def test_sample_battle_3(self):
        self.harness("input/day_15_test_3.txt", 46, 39514)

    def test_sample_battle_4(self):
        self.harness("input/day_15_test_4.txt", 35, 27755)

    def test_sample_battle_5(self):
        self.harness("input/day_15_test_5.txt", 54, 28944)

    def test_sample_battle_6(self):
        self.harness("input/day_15_test_6.txt", 20, 18740)

    def test_real_battle_part_1(self):
        cavern = Cavern.cavern_from_file("input/day_15.txt")
        battle = Battle(cavern)
        num_rounds, result = battle.execute()

        print("Part 1:", num_rounds, result)

    def test_real_battle_part_2(self):
        cavern = Cavern.cavern_from_file("input/day_15.txt", save_the_elves=True)
        battle = Battle(cavern)
        num_rounds, result = battle.execute()

        print("Part 2:", num_rounds, result)

    def harness(self, path, rounds, result):
        cavern = Cavern.cavern_from_file(path)
        battle = Battle(cavern)
        num_rounds, outcome = battle.execute()

        if num_rounds != rounds or outcome != result:
            raise Exception(f"Expected {rounds}, {result}, got {num_rounds}, {outcome}")


"""
--- Day 15: Beverage Bandits ---
Having perfected their hot chocolate, the Elves have a new problem: the Goblins that live in these caves will do
 anything to steal it. Looks like they're here for a fight.

You scan the area, generating a map of the walls (#), open cavern (.), and starting position of every Goblin (G)
and Elf (E) (your puzzle input).

Combat proceeds in rounds; in each round, each unit that is still alive takes a turn, resolving all of its actions
before the next unit's turn begins. On each unit's turn, it tries to move into range of an enemy (if it isn't already)
and then attack (if it is in range).

All units are very disciplined and always follow very strict combat rules. Units never move or attack diagonally,
as doing so would be dishonorable. When multiple choices are equally valid, ties are broken in reading order:
top-to-bottom, then left-to-right. For instance, the order in which units take their turns within a round is the
reading order of their starting positions in that round, regardless of the type of unit or whether other units have
moved after the round started. For example:

                 would take their
These units:   turns in this order:
  #######           #######
  #.G.E.#           #.1.2.#
  #E.G.E#           #3.4.5#
  #.G.E.#           #.6.7.#
  #######           #######
Each unit begins its turn by identifying all possible targets (enemy units). If no targets remain, combat ends.

Then, the unit identifies all of the open squares (.) that are in range of each target; these are the squares which
are adjacent (immediately up, down, left, or right) to any target and which aren't already occupied by a wall or
another unit. Alternatively, the unit might already be in range of a target. If the unit is not already in range of a
target, and there are no open squares which are in range of a target, the unit ends its turn.

If the unit is already in range of a target, it does not move, but continues its turn with an attack. Otherwise,
since it is not in range of a target, it moves.

To move, the unit first considers the squares that are in range and determines which of those squares it could reach
in the fewest steps. A step is a single movement to any adjacent (immediately up, down, left, or right) open (.)
square. Units cannot move into walls or other units. The unit does this while considering the current positions of
units and does not do any prediction about where units will be later. If the unit cannot reach (find an open path to)
any of the squares that are in range, it ends its turn. If multiple squares are in range and tied for being reachable
in the fewest steps, the square which is first in reading order is chosen. For example:

Targets:      In range:     Reachable:    Nearest:      Chosen:
#######       #######       #######       #######       #######
#E..G.#       #E.?G?#       #E.@G.#       #E.!G.#       #E.+G.#
#...#.#  -->  #.?.#?#  -->  #.@.#.#  -->  #.!.#.#  -->  #...#.#
#.G.#G#       #?G?#G#       #@G@#G#       #!G.#G#       #.G.#G#
#######       #######       #######       #######       #######
In the above scenario, the Elf has three targets (the three Goblins):

Each of the Goblins has open, adjacent squares which are in range (marked with a ? on the map).
Of those squares, four are reachable (marked @); the other two (on the right) would require moving through a wall or
unit to reach.
Three of these reachable squares are nearest, requiring the fewest steps (only 2) to reach (marked !).
Of those, the square which is first in reading order is chosen (+).
The unit then takes a single step toward the chosen square along the shortest path to that square. If multiple steps
would put the unit equally closer to its destination, the unit chooses the step which is first in reading order.
(This requires knowing when there is more than one shortest path so that you can consider the first step of each
such path.) For example:

In range:     Nearest:      Chosen:       Distance:     Step:
#######       #######       #######       #######       #######
#.E...#       #.E...#       #.E...#       #4E212#       #..E..#
#...?.#  -->  #...!.#  -->  #...+.#  -->  #32101#  -->  #.....#
#..?G?#       #..!G.#       #...G.#       #432G2#       #...G.#
#######       #######       #######       #######       #######
The Elf sees three squares in range of a target (?), two of which are nearest (!), and so the first in reading
order is chosen (+). Under "Distance", each open square is marked with its distance from the destination square;
the two squares to which the Elf could move on this turn (down and to the right) are both equally good moves and
would leave the Elf 2 steps from being in range of the Goblin. Because the step which is first in reading order
is chosen, the Elf moves right one square.

Here's a larger example of movement:

Initially:
#########
#G..G..G#
#.......#
#.......#
#G..E..G#
#.......#
#.......#
#G..G..G#
#########

After 1 round:
#########
#.G...G.#
#...G...#
#...E..G#
#.G.....#
#.......#
#G..G..G#
#.......#
#########

After 2 rounds:
#########
#..G.G..#
#...G...#
#.G.E.G.#
#.......#
#G..G..G#
#.......#
#.......#
#########

After 3 rounds:
#########
#.......#
#..GGG..#
#..GEG..#
#G..G...#
#......G#
#.......#
#.......#
#########
Once the Goblins and Elf reach the positions above, they all are either in range of a target or cannot find any
square in range of a target, and so none of the units can move until a unit dies.

After moving (or if the unit began its turn in range of a target), the unit attacks.

To attack, the unit first determines all of the targets that are in range of it by being immediately adjacent to it.
If there are no such targets, the unit ends its turn. Otherwise, the adjacent target with the fewest hit points is
selected; in a tie, the adjacent target with the fewest hit points which is first in reading order is selected.

The unit deals damage equal to its attack power to the selected target, reducing its hit points by that amount. If
this reduces its hit points to 0 or fewer, the selected target dies: its square becomes . and it takes no further turns.

Each unit, either Goblin or Elf, has 3 attack power and starts with 200 hit points.

For example, suppose the only Elf is about to attack:

       HP:            HP:
G....  9       G....  9
..G..  4       ..G..  4
..EG.  2  -->  ..E..
..G..  2       ..G..  2
...G.  1       ...G.  1
The "HP" column shows the hit points of the Goblin to the left in the corresponding row. The Elf is in range of three
targets: the Goblin above it (with 4 hit points), the Goblin to its right (with 2 hit points), and the Goblin below it
(also with 2 hit points). Because three targets are in range, the ones with the lowest hit points are selected: the
two Goblins with 2 hit points each (one to the right of the Elf and one below the Elf). Of those, the Goblin first in
reading order (the one to the right of the Elf) is selected. The selected Goblin's hit points (2) are reduced by the
Elf's attack power (3), reducing its hit points to -1, killing it.

After attacking, the unit's turn ends. Regardless of how the unit's turn ends, the next unit in the round takes its
turn. If all units have taken turns in this round, the round ends, and a new round begins.

The Elves look quite outnumbered. You need to determine the outcome of the battle: the number of full rounds that were
completed (not counting the round in which combat ends) multiplied by the sum of the hit points of all remaining units
at the moment combat ends. (Combat only ends when a unit finds no targets during its turn.)

Below is an entire sample combat. Next to each map, each row's units' hit points are listed from left to right.

Initially:
#######
#.G...#   G(200)
#...EG#   E(200), G(200)
#.#.#G#   G(200)
#..G#E#   G(200), E(200)
#.....#
#######

After 1 round:
#######
#..G..#   G(200)
#...EG#   E(197), G(197)
#.#G#G#   G(200), G(197)
#...#E#   E(197)
#.....#
#######

After 2 rounds:
#######
#...G.#   G(200)
#..GEG#   G(200), E(188), G(194)
#.#.#G#   G(194)
#...#E#   E(194)
#.....#
#######

Combat ensues; eventually, the top Elf dies:

After 23 rounds:
#######
#...G.#   G(200)
#..G.G#   G(200), G(131)
#.#.#G#   G(131)
#...#E#   E(131)
#.....#
#######

After 24 rounds:
#######
#..G..#   G(200)
#...G.#   G(131)
#.#G#G#   G(200), G(128)
#...#E#   E(128)
#.....#
#######

After 25 rounds:
#######
#.G...#   G(200)
#..G..#   G(131)
#.#.#G#   G(125)
#..G#E#   G(200), E(125)
#.....#
#######

After 26 rounds:
#######
#G....#   G(200)
#.G...#   G(131)
#.#.#G#   G(122)
#...#E#   E(122)
#..G..#   G(200)
#######

After 27 rounds:
#######
#G....#   G(200)
#.G...#   G(131)
#.#.#G#   G(119)
#...#E#   E(119)
#...G.#   G(200)
#######

After 28 rounds:
#######
#G....#   G(200)
#.G...#   G(131)
#.#.#G#   G(116)
#...#E#   E(113)
#....G#   G(200)
#######

More combat ensues; eventually, the bottom Elf dies:

After 47 rounds:
#######
#G....#   G(200)
#.G...#   G(131)
#.#.#G#   G(59)
#...#.#
#....G#   G(200)
#######
Before the 48th round can finish, the top-left Goblin finds that there are no targets remaining, and so combat ends.
So, the number of full rounds that were completed is 47, and the sum of the hit points of all remaining units is
200+131+59+200 = 590. From these, the outcome of the battle is 47 * 590 = 27730.

Here are a few example summarized combats:

#######       #######
#G..#E#       #...#E#   E(200)
#E#E.E#       #E#...#   E(197)
#G.##.#  -->  #.E##.#   E(185)
#...#E#       #E..#E#   E(200), E(200)
#...E.#       #.....#
#######       #######

Combat ends after 37 full rounds
Elves win with 982 total hit points left
Outcome: 37 * 982 = 36334
#######       #######
#E..EG#       #.E.E.#   E(164), E(197)
#.#G.E#       #.#E..#   E(200)
#E.##E#  -->  #E.##.#   E(98)
#G..#.#       #.E.#.#   E(200)
#..E#.#       #...#.#
#######       #######

Combat ends after 46 full rounds
Elves win with 859 total hit points left
Outcome: 46 * 859 = 39514
#######       #######
#E.G#.#       #G.G#.#   G(200), G(98)
#.#G..#       #.#G..#   G(200)
#G.#.G#  -->  #..#..#
#G..#.#       #...#G#   G(95)
#...E.#       #...G.#   G(200)
#######       #######

Combat ends after 35 full rounds
Goblins win with 793 total hit points left
Outcome: 35 * 793 = 27755
#######       #######
#.E...#       #.....#
#.#..G#       #.#G..#   G(200)
#.###.#  -->  #.###.#
#E#G#G#       #.#.#.#
#...#G#       #G.G#G#   G(98), G(38), G(200)
#######       #######

Combat ends after 54 full rounds
Goblins win with 536 total hit points left
Outcome: 54 * 536 = 28944
#########       #########
#G......#       #.G.....#   G(137)
#.E.#...#       #G.G#...#   G(200), G(200)
#..##..G#       #.G##...#   G(200)
#...##..#  -->  #...##..#
#...#...#       #.G.#...#   G(200)
#.G...G.#       #.......#
#.....G.#       #.......#
#########       #########

Combat ends after 20 full rounds
Goblins win with 937 total hit points left
Outcome: 20 * 937 = 18740
What is the outcome of the combat described in your puzzle input?
"""

