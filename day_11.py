from collections import namedtuple
import numpy as np
import unittest


Point = namedtuple("Point", ["x", "y"])


puzzle_serial_number = 3613


class FuelCells:

    def __init__(self, serial_number, size=300):
        self.serial_number = serial_number
        self.size = size

        self.cells = np.zeros((size, size))
        self.summed = None

        self.set_cell_power_levels()
        self.summed = self.cells.cumsum(axis=0).cumsum(axis=1)  # See wikipedia summed-area table

    @staticmethod
    def serial_to_power_level(serial, x, y):
        """
        The power level in a given fuel cell can be found through the following process:

        - Find the fuel cell's rack ID, which is its X coordinate plus 10.
        - Begin with a power level of the rack ID times the Y coordinate.
        - Increase the power level by the value of the grid serial number (your puzzle input).
        - Set the power level to itself multiplied by the rack ID.
        - Keep only the hundreds digit of the power level (so 12345 becomes 3; numbers with no hundreds digit become 0).
        - Subtract 5 from the power level.
        """
        rack_id = x + 10
        power_level = rack_id * y + serial
        power_level *= rack_id
        power_level = power_level // 100 % 10

        return power_level - 5

    def set_cell_power_levels(self):
        for x in range(self.size):
            for y in range(self.size):
                self.cells[x][y] = self.serial_to_power_level(self.serial_number, x, y)

    def find_highest_total_power(self, size=3):
        point = None
        highest = 0
        for x in range(self.size - size):
            for y in range(self.size - size):
                total = self.total_in_square(x, y, size)
                if total > highest:
                    point = Point(x + 1, y + 1)  # +1 translates from 0 based to 1 based as per requirements
                    highest = total

        return point, highest

    def find_highest_any_size(self):
        """
        Yikes, this is slow as shit. Should find a way to refactor.
        """
        size = 1
        point = None
        highest = 0
        for i in range(1, self.size - 1):
            location, power = self.find_highest_total_power(size=i)
            if power > highest:
                highest = power
                point = location
                size = i

        return point, size, highest

    def total_in_square(self, x, y, size):
        """
        # See wikipedia summed-area table
        """
        a = self.summed[x][y]
        b = self.summed[x + size][y]
        c = self.summed[x][y + size]
        d = self.summed[x + size][y + size]

        return d - b - c + a


class TestFuelCells(unittest.TestCase):

    """
    Fuel cell at  122,79, grid serial number 57: power level -5.
    Fuel cell at 217,196, grid serial number 39: power level  0.
    Fuel cell at 101,153, grid serial number 71: power level  4.
    """
    def test_serial_to_power_level(self):
        assert FuelCells.serial_to_power_level(8, 3, 5) == 4
        assert FuelCells.serial_to_power_level(57, 122, 79) == -5
        assert FuelCells.serial_to_power_level(39, 217, 196) == 0
        assert FuelCells.serial_to_power_level(71, 101, 153) == 4

    def test_fuel_cells(self):
        """
        For grid serial number 18, the largest total 3x3 square has a top-left corner of 33,45 (with a total power of
        29); these fuel cells appear in the middle of this 5x5 region:

        -2  -4   4   4   4
        -4   4   4   4  -5
         4   3   3   4  -4
         1   1   2   4  -3
        -1   0   2  -5  -2
        """
        point, power = FuelCells(18).find_highest_total_power(size=3)
        assert point == Point(33, 45)
        assert power == 29

    def test_find_highest_any_size(self):
        """
        For grid serial number 18, the largest total square (with a total power of 113) is 16x16 and has a top-left
        corner of 90,269, so its identifier is 90,269,16.
        :return:
        """
        point, size, power = FuelCells(18).find_highest_any_size()
        assert point == Point(90, 269)
        assert size == 16
        assert power == 113

    def test_main_puzzle_part_1(self):
        point, power = FuelCells(puzzle_serial_number).find_highest_total_power(size=3)
        assert point == Point(20, 54)
        assert power == 30

    def test_main_puzzle_part_2(self):
        print(
            FuelCells(puzzle_serial_number).find_highest_any_size()
        )


"""
--- Day 11: Chronal Charge ---
You watch the Elves and their sleigh fade into the distance as they head toward the North Pole.

Actually, you're the one fading. The falling sensation returns.

The low fuel warning light is illuminated on your wrist-mounted device. Tapping it once causes it to project a hologram
 of the situation: a 300x300 grid of fuel cells and their current power levels, some negative. You're not sure what 
 negative power means in the context of time travel, but it can't be good.

Each fuel cell has a coordinate ranging from 1 to 300 in both the X (horizontal) and Y (vertical) direction. In X,Y 
notation, the top-left cell is 1,1, and the top-right cell is 300,1.

The interface lets you select any 3x3 square of fuel cells. To increase your chances of getting to your destination, 
you decide to choose the 3x3 square with the largest total power.

The power level in a given fuel cell can be found through the following process:

Find the fuel cell's rack ID, which is its X coordinate plus 10.
Begin with a power level of the rack ID times the Y coordinate.
Increase the power level by the value of the grid serial number (your puzzle input).
Set the power level to itself multiplied by the rack ID.
Keep only the hundreds digit of the power level (so 12345 becomes 3; numbers with no hundreds digit become 0).
Subtract 5 from the power level.
For example, to find the power level of the fuel cell at 3,5 in a grid with serial number 8:

The rack ID is 3 + 10 = 13.
The power level starts at 13 * 5 = 65.
Adding the serial number produces 65 + 8 = 73.
Multiplying by the rack ID produces 73 * 13 = 949.
The hundreds digit of 949 is 9.
Subtracting 5 produces 9 - 5 = 4.
So, the power level of this fuel cell is 4.

Here are some more example power levels:

Fuel cell at  122,79, grid serial number 57: power level -5.
Fuel cell at 217,196, grid serial number 39: power level  0.
Fuel cell at 101,153, grid serial number 71: power level  4.
Your goal is to find the 3x3 square which has the largest total power. The square must be entirely within the 300x300 
grid. Identify this square using the X,Y coordinate of its top-left fuel cell. For example:

For grid serial number 18, the largest total 3x3 square has a top-left corner of 33,45 (with a total power of 29); 
these fuel cells appear in the middle of this 5x5 region:

-2  -4   4   4   4
-4   4   4   4  -5
 4   3   3   4  -4
 1   1   2   4  -3
-1   0   2  -5  -2

For grid serial number 42, the largest 3x3 square's top-left is 21,61 (with a total power of 30); they are in the 
middle of this region:

-3   4   2   2   2
-4   4   3   3   4
-5   3   3   4  -4
 4   3   3   4  -3
 3   3   3  -5  -1
 
What is the X,Y coordinate of the top-left fuel cell of the 3x3 square with the largest total power?

Your puzzle input is 3613.

--- Part Two ---
You discover a dial on the side of the device; it seems to let you select a square of any size, not just 3x3. Sizes 
from 1x1 to 300x300 are supported.

Realizing this, you now must find the square of any size with the largest total power. Identify this square by 
including its size as a third parameter after the top-left coordinate: a 9x9 square with a top-left corner of 3,5 is 
identified as 3,5,9.

For example:

For grid serial number 18, the largest total square (with a total power of 113) is 16x16 and has a top-left corner of 
90,269, so its identifier is 90,269,16.
For grid serial number 42, the largest total square (with a total power of 119) is 12x12 and has a top-left corner of 
232,251, so its identifier is 232,251,12.
What is the X,Y,size identifier of the square with the largest total power?
"""
