import string
import unittest


data = open("input/day_05.txt").read().strip()


def reduce_polymer(polymer):
    """
    A polymer is a string of upper and lower case characters. If the upper and lower case versions of the
    same letter touch, they explode and should both be removed from the chain.
    """
    stack = list()

    for c in polymer:
        if stack and c.swapcase() == stack[-1]:
            stack.pop()
        else:
            stack.append(c)

    return ''.join(stack)


class TestPolymer(unittest.TestCase):

    def test_reduce_polymer(self):
        assert reduce_polymer('hHsSmMHhhHwWfoo') == 'foo'
        assert reduce_polymer('hHsSmMHhhHwWfoohHsSmMHaAhhHwW') == 'foo'

    def test_part_1(self):
        print("Part 1:", len(reduce_polymer(data)))

    def test_part_2(self):
        shortest = float('inf')
        for c in string.ascii_letters:
            filtered = data.replace(c, '').replace(c.swapcase(), '')
            shortest = min(
                len(reduce_polymer(polymer=filtered)),
                shortest
            )

        print("Part 2:", shortest)



if __name__ == "__main__":
    unittest.main()

"""
--- Day 5: Alchemical Reduction ---
You've managed to sneak in to the prototype suit manufacturing lab. The Elves are making decent progress,
but are still struggling with the suit's size reduction capabilities.

While the very latest in 1518 alchemical technology might have solved their problem eventually, you can do
better. You scan the chemical composition of the suit's material and discover that it is formed by extremely
long polymers (one of which is available as your puzzle input).

The polymer is formed by smaller units which, when triggered, react with each other such that two adjacent
units of the same type and opposite polarity are destroyed. Units' types are represented by letters; units'
polarity is represented by capitalization. For instance, r and R are units with the same type but opposite
polarity, whereas r and s are entirely different types and do not react.

For example:

In aA, a and A react, leaving nothing behind.
In abBA, bB destroys itself, leaving aA. As above, this then destroys itself, leaving nothing.
In abAB, no two adjacent units are of the same type, and so nothing happens.
In aabAAB, even though aa and AA are of the same type, their polarities match, and so nothing happens.
Now, consider a larger example, dabAcCaCBAcCcaDA:

dabAcCaCBAcCcaDA  The first 'cC' is removed.
dabAaCBAcCcaDA    This creates 'Aa', which is removed.
dabCBAcCcaDA      Either 'cC' or 'Cc' are removed (the result is the same).
dabCBAcaDA        No further actions can be taken.
After all possible reactions, the resulting polymer contains 10 units.

How many units remain after fully reacting the polymer you scanned?
"""

