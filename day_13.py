import unittest
from collections import namedtuple


Point = namedtuple("Point", ['x', 'y'])


class Cart:
    """
    Keeps track of its own location, and makes appropriate turns based on the spec.
    """

    turn_order = ['>', '^', '<', 'v']  # left turns

    def __init__(self, char, point):
        self.char = char
        self.point = point
        self.intersections = 0  # number of "+" intersections seen by this cart

    def __repr__(self):
        return f"Cart({self.char}, {self.point})"

    def turn(self):
        """
        Each time a cart has the option to turn (by arriving at any intersection), it turns left the first
        time, goes straight the second time, turns right the third time, and then repeats...
        """
        cycle = self.intersections % 3
        curr = Cart.turn_order.index(self.char)
        delta = 0

        if cycle == 0:  # turn left
            delta = 1
        elif cycle == 1:  # go straight
            pass
        elif cycle == 2:  # turn right
            delta = -1

        self.char = Cart.turn_order[(curr + delta) % 4]
        self.intersections += 1


class MineCartMap:

    """
    Moves carts around on the track, which is represented the input text contained in MineCartMap.lines.
    The lines are basicaly a graph structure, but it's not really a helpful exercise to build a graph
    when one is provided to you from the input.
    """

    cart_chars = {"v", "^", ">", "<"}

    def __init__(self, lines):
        self.carts = list()
        self.lines = lines
        self.collisions = []

    def __repr__(self):
        ret = [line[:] for line in self.lines]
        for cart in self.carts:
            ret[cart.point.y][cart.point.x] = cart.char
        for collision in self.collisions:
            ret[collision.y][collision.x] = 'X'
        return ''.join([''.join(line) for line in ret])

    @classmethod
    def map_from_filepath(cls, filepath):
        with open(filepath) as f:
            lines = [[c for c in line] for line in f.readlines()]

        mine_cart_map = MineCartMap(lines)

        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char in mine_cart_map.cart_chars:
                    if char == ">" or char == "<":
                        track = "-"
                    elif char == "^" or char == "v":
                        track = "|"
                    else:
                        raise Exception("unknown cart character")

                    mine_cart_map.carts.append(Cart(char, Point(x, y)))
                    mine_cart_map.lines[y][x] = track  # replace the cart with appropriate track

        return mine_cart_map

    def step(self):
        ordered_carts = sorted(self.carts, key=lambda c: (c.point.y, c.point.x))  # sort by y then x

        for cart in ordered_carts:
            if cart.char == ">":
                cart.point = Point(cart.point.x + 1, cart.point.y)
            elif cart.char == "<":
                cart.point = Point(cart.point.x - 1, cart.point.y)
            elif cart.char == "^":
                cart.point = Point(cart.point.x, cart.point.y - 1)
            elif cart.char == "v":
                cart.point = Point(cart.point.x, cart.point.y + 1)

            for other in ordered_carts:
                if other is not cart and other.point == cart.point:
                    self.collisions.append(cart.point)
                    self.carts.remove(other)
                    self.carts.remove(cart)

            track = self.lines[cart.point.y][cart.point.x]

            if track == "/":
                if cart.char == "<":
                    cart.char = "v"
                elif cart.char == "^":
                    cart.char = ">"
                elif cart.char == ">":
                    cart.char = "^"
                elif cart.char == "v":
                    cart.char = "<"
            elif track == "\\":
                if cart.char == ">":
                    cart.char = "v"
                elif cart.char == "^":
                    cart.char = "<"
                elif cart.char == "<":
                    cart.char = "^"
                elif cart.char == "v":
                    cart.char = ">"
            elif track == "+":
                cart.turn()


class TestMineCart(unittest.TestCase):

    def setUp(self):
        self.testmap = MineCartMap.map_from_filepath("input/day_13_test.txt")
        self.testmap2 = MineCartMap.map_from_filepath("input/day_13_test_2.txt")

    def test_map_from_filepath(self):
        assert self.testmap is not None

    def test_collision(self):
        while not self.testmap.collisions:
            self.testmap.step()

        assert self.testmap.collisions[0] == Point(7, 3)

    def test_removal(self):
        while len(self.testmap2.carts) > 1:
            self.testmap2.step()

        assert self.testmap2.carts[0].point == Point(6, 4)

    def test_puzzle_part_1(self):
        puzzle_map = MineCartMap.map_from_filepath("input/day_13.txt")

        while not puzzle_map.collisions:
            puzzle_map.step()

        print("Part 1:", puzzle_map.collisions[0])

        assert puzzle_map.collisions[0] == Point(8, 3)

    def test_puzzle_part_2(self):
        puzzle_map = MineCartMap.map_from_filepath("input/day_13.txt")

        while len(puzzle_map.carts) > 1:
            puzzle_map.step()

        print("Part 2:", puzzle_map.carts[0].point)

        assert "Part 2:", puzzle_map.carts[0].point == Point(73, 121)


"""
--- Day 13: Mine Cart Madness ---
A crop of this size requires significant logistics to transport produce, soil, fertilizer, and so on. The Elves 
are very busy pushing things around in carts on some kind of rudimentary system of tracks they've come up with.

Seeing as how cart-and-track systems don't appear in recorded history for another 1000 years, the Elves seem to
 be making this up as they go along. They haven't even figured out how to avoid collisions yet.

You map out the tracks (your puzzle input) and see where you can help.

Tracks consist of straight paths (| and -), curves (/ and \), and intersections (+). Curves connect exactly two
 perpendicular pieces of track; for example, this is a closed loop:

/----\
|    |
|    |
\----/
Intersections occur when two perpendicular paths cross. At an intersection, a cart is capable of turning left, 
turning right, or continuing straight. Here are two loops connected by two intersections:

/-----\
|     |
|  /--+--\
|  |  |  |
\--+--/  |
   |     |
   \-----/
Several carts are also on the tracks. Carts always face either up (^), down (v), left (<), or right (>). 
(On your initial map, the track under each cart is a straight path matching the direction the cart is facing.)

Each time a cart has the option to turn (by arriving at any intersection), it turns left the first time, goes 
straight the second time, turns right the third time, and then repeats those directions starting again with 
left the fourth time, straight the fifth time, and so on. This process is independent of the particular 
intersection at which the cart has arrived - that is, the cart has no per-intersection memory.

Carts all move at the same speed; they take turns moving a single step at a time. They do this based on their 
current location: carts on the top row move first (acting from left to right), then carts on the second row move 
(again from left to right), then carts on the third row, and so on. Once each cart has moved one step, the process 
repeats; each of these loops is called a tick.

For example, suppose there are two carts on a straight track:

|  |  |  |  |
v  |  |  |  |
|  v  v  |  |
|  |  |  v  X
|  |  ^  ^  |
^  ^  |  |  |
|  |  |  |  |
First, the top cart moves. It is facing down (v), so it moves down one square. Second, the bottom cart moves. 
It is facing up (^), so it moves up one square. Because all carts have moved, the first tick ends. Then, the 
process repeats, starting with the first cart. The first cart moves down, then the second cart moves up - right 
into the first cart, colliding with it! (The location of the crash is marked with an X.) This ends the second 
and last tick.

Here is a longer example:

/->-\        
|   |  /----\
| /-+--+-\  |
| | |  | v  |
\-+-/  \-+--/
  \------/   

/-->\        
|   |  /----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \->--/
  \------/   

/---v        
|   |  /----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \-+>-/
  \------/   

/---\        
|   v  /----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \-+->/
  \------/   

/---\        
|   |  /----\
| /->--+-\  |
| | |  | |  |
\-+-/  \-+--^
  \------/   

/---\        
|   |  /----\
| /-+>-+-\  |
| | |  | |  ^
\-+-/  \-+--/
  \------/   

/---\        
|   |  /----\
| /-+->+-\  ^
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /----<
| /-+-->-\  |
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /---<\
| /-+--+>\  |
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /--<-\
| /-+--+-v  |
| | |  | |  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /-<--\
| /-+--+-\  |
| | |  | v  |
\-+-/  \-+--/
  \------/   

/---\        
|   |  /<---\
| /-+--+-\  |
| | |  | |  |
\-+-/  \-<--/
  \------/   

/---\        
|   |  v----\
| /-+--+-\  |
| | |  | |  |
\-+-/  \<+--/
  \------/   

/---\        
|   |  /----\
| /-+--v-\  |
| | |  | |  |
\-+-/  ^-+--/
  \------/   

/---\        
|   |  /----\
| /-+--+-\  |
| | |  X |  |
\-+-/  \-+--/
  \------/   
After following their respective paths for a while, the carts eventually crash. To help prevent crashes, 
you'd like to know the location of the first crash. Locations are given in X,Y coordinates, where the furthest 
left column is X=0 and the furthest top row is Y=0:

           111
 0123456789012
0/---\        
1|   |  /----\
2| /-+--+-\  |
3| | |  X |  |
4\-+-/  \-+--/
5  \------/   
In this example, the location of the first crash is 7,3.
"""
