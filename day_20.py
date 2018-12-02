from collections import defaultdict, namedtuple
import unittest


class Point(namedtuple('Point', ['x', 'y'])):

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)


class RegularMap:

    def __init__(self, regex):
        self.regex = regex
        self.costs = None
        self.explore()

    def explore(self):
        directions = {
            'N': Point(0, -1),
            'S': Point(0, 1),
            'E': Point(1, 0),
            'W': Point(-1, 0),
        }

        stack = []
        pos = Point(0, 0)
        costs = defaultdict(lambda: float('inf'))
        costs[pos] = 0

        for c in self.regex:
            if c in directions:
                new_pos = pos + directions[c]
                costs[new_pos] = min(costs[pos] + 1, costs[new_pos])
                pos = new_pos
            elif c == '(':
                stack.append(pos)
            elif c == ')':
                pos = stack.pop()
            elif c == '|':
                pos = stack[-1]

        self.costs = costs

    @property
    def highest_cost(self):
        return max(self.costs.values())

    def paths_above_n(self, n):
        return len([i for i in self.costs.values() if i >= n])


class TestMap(unittest.TestCase):

    def test_sample_cases(self):
        assert RegularMap("^WNE$").highest_cost == 3
        assert RegularMap("^ENWWW(NEEE|SSE(EE|N))$").highest_cost == 10
        assert RegularMap("^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$").highest_cost == 18
        assert RegularMap("^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$").highest_cost == 23
        assert RegularMap("^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))$").highest_cost == 31

    def test_main(self):
        with open("input/day_20.txt") as f:
            regex = f.read()

        m = RegularMap(regex)
        print("Part 1:", m.highest_cost)
        print("Part 2:", m.paths_above_n(1000))


