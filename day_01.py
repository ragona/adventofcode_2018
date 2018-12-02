import unittest


def frequencies():
    with open("input/day_01.txt", 'r') as f:
        return [int(line.rstrip()) for line in f.readlines()]


def first_repeated_value(values, passes=200):
    """
    Depending on the sequence of values, there may not be a repeated value.

    :param values: List of positive and negative integers
    :param passes: Number of times to loop through the full list before deciding that there will be no repeated value.
    """
    total = 0
    seen = set()
    i = 0

    while i < len(values) * passes:
        if total in seen:
            return total
        else:
            seen.add(total)
            total += values[i % len(values)]
            i += 1
    return None


class TestRepeatedValue(unittest.TestCase):

    def test_first_repeated(self):
        assert first_repeated_value([+1, +1]) is None
        assert first_repeated_value([+1, -1]) == 0
        assert first_repeated_value([+3, +3, +4, -2, -4]) == 10
        assert first_repeated_value([-6, +3, +8, +5, -6]) == 5
        assert first_repeated_value([+7, +7, -2, -7, -4]) == 14

    def test_part_1(self):
        print("Part 1:", sum(frequencies()))

        assert sum(frequencies()) == 513

    def test_part_2(self):
        print("Part 2:", first_repeated_value(frequencies()))

        assert first_repeated_value(frequencies()) == 287


if __name__ == '__main__':
    unittest.main()


"""
--- Day 1: Chronal Calibration ---

A value like +6 means the current frequency increases by 6; a value like -3 means the current frequency decreases by 3.

For example, if the device displays frequency changes of +1, -2, +3, +1, then starting from a frequency of zero, the
following changes would occur:

Current frequency  0, change of +1; resulting frequency  1.
Current frequency  1, change of -2; resulting frequency -1.
Current frequency -1, change of +3; resulting frequency  2.
Current frequency  2, change of +1; resulting frequency  3.
In this example, the resulting frequency is 3.

Here are other example situations:

+1, +1, +1 results in  3
+1, +1, -2 results in  0
-1, -2, -3 results in -6
Starting with a frequency of zero, what is the resulting frequency after all of the changes in frequency have been
applied?

--- Part Two ---
You notice that the device repeats the same frequency change list over and over. To calibrate the device, you need to 
find the first frequency it reaches twice.

For example, using the same list of changes above, the device would loop as follows:

Current frequency  0, change of +1; resulting frequency  1.
Current frequency  1, change of -2; resulting frequency -1.
Current frequency -1, change of +3; resulting frequency  2.
Current frequency  2, change of +1; resulting frequency  3.
(At this point, the device continues from the start of the list.)
Current frequency  3, change of +1; resulting frequency  4.
Current frequency  4, change of -2; resulting frequency  2, which has already been seen.
In this example, the first frequency reached twice is 2. Note that your device might need to repeat its list of 
frequency changes many times before a duplicate frequency is found, and that duplicates might be found while in the 
middle of processing the list.

Here are other examples:

+1, -1 first reaches 0 twice.
+3, +3, +4, -2, -4 first reaches 10 twice.
-6, +3, +8, +5, -6 first reaches 5 twice.
+7, +7, -2, -7, -4 first reaches 14 twice.
What is the first frequency your device reaches twice?
"""
