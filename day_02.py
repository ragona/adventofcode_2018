from collections import Counter
from itertools import permutations
from collections import namedtuple

import unittest


def box_ids():
    with open("input/day_02.txt", 'r') as f:
        return [line.rstrip() for line in f.readlines()]


def has_n(string, n):
    return n in Counter(string).values()


def checksum(ids):
    twos = 0
    threes = 0

    for string in ids:
        twos += has_n(string, 2)
        threes += has_n(string, 3)

    return twos * threes


def char_difference(a, b):
    """
    Number of characters that differ between two equal length strings
    """
    if len(a) != len(b):
        return ValueError("Expecting equal length strings")

    return sum(x != y for x, y in zip(a, b))


class Match(namedtuple('Match', ['a', 'b', 'diff'])):

    @property
    def overlap(self):
        overlap_len = len(self.a) - self.diff
        for i in range(self.diff + 1):
            substr = self.a[i: overlap_len + 1]
            if substr in self.b:
                return substr


def closest_match(words):
    closest = Match(None, None, 100)

    for a, b in permutations(words, 2):
        match = Match(
            a=a,
            b=b,
            diff=char_difference(a, b)
        )
        if match.diff < closest.diff:
            closest = match

    return closest


class TestBoxScan(unittest.TestCase):

    def test_has_n(self):
        assert has_n("foo", 2)
        assert not has_n("bar", 2)
        assert not has_n("bababac", 2)
        assert has_n("bababc", 3)
        assert not has_n("foo", 3)

    def test_char_difference(self):
        assert char_difference("foo", "bar") == 3
        assert char_difference("foo", "for") == 1

    def test_part_1(self):
        print("Part 1", checksum(box_ids()))

        assert checksum(box_ids()) == 7904

    def test_part_2(self):
        match = closest_match(box_ids())

        print("Part 2:", match.overlap)

        assert match.overlap == "wugbihckpoymcpaxefotvdzns"


if __name__ == '__main__':
    unittest.main()


"""
--- Part One ---

To make sure you didn't miss any, you scan the likely candidate boxes again, counting the number that have an ID 
containing exactly two of any letter and then separately counting those with exactly three of any letter. You can 
multiply those two counts together to get a rudimentary checksum and compare it to what your device predicts.

For example, if you see the following box IDs:

abcdef contains no letters that appear exactly two or three times.
bababc contains two a and three b, so it counts for both.
abbcde contains two b, but no letter appears exactly three times.
abcccd contains three c, but no letter appears exactly two times.
aabcdd contains two a and two d, but it only counts once.
abcdee contains two e.
ababab contains three a and three b, but it only counts once.
Of these box IDs, four of them contain a letter which appears exactly twice, and three of them contain a letter which 
appears exactly three times. Multiplying these together produces a checksum of 4 * 3 = 12.

What is the checksum for your list of box IDs?


--- Part Two ---
Confident that your list of box IDs is complete, you're ready to find the boxes full of prototype fabric.

The boxes will have IDs which differ by exactly one character at the same position in both strings. For example, 
given the following box IDs:

abcde
fghij
klmno
pqrst
fguij
axcye
wvxyz
The IDs abcde and axcye are close, but they differ by two characters (the second and fourth). However, the IDs fghij 
and fguij differ by exactly one character, the third (h and u). Those must be the correct boxes.

What letters are common between the two correct box IDs? (In the example above, this is found by removing the differing 
character from either ID, producing fgij.)
"""
