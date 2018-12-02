from collections import deque, namedtuple
import unittest
import string


license_file = open("input/day_08.txt").read().strip()


NodeHeader = namedtuple("NodeHeader", ['num_children', 'num_metadata'])


def num_to_letter(num):
    """
    Useful for giving the nodes a friendly name. Will be A, B, C... AA, BB, CC..., AAA, BBB, CCC, etc...
    """
    return string.ascii_uppercase[num % 26] * (num // 26 + 1)


class Tree:
    """
    Rooted tree where each node can have an arbitrary number of children. Doesn't appear to need to be
    sorted in any particular way. (In fact, the value of the nodes don't matter at all.)
    """

    class Node:

        def __init__(self, data=None):
            self.data = data
            self.children = list()
            self.metadata = None

        def __repr__(self):
            return f"Node({self.data})"

        @property
        def value(self):
            if not self.children:
                return sum(self.metadata)

            total = 0
            for num in self.metadata:
                if num - 1 >= len(self.children):  # -1 because this is 1 indexed, but python is 0 indexed
                    continue

                total += self.children[num - 1].value

            return total

    def __init__(self, root=None):
        self.root = root
        self.count = 0

    def new_node(self):
        node = Tree.Node(num_to_letter(self.count))
        self.count += 1
        return node

    def all_nodes(self):
        if not self.root:
            return None

        if not self.root.children:
            return self.root

        nodes = []  # todo: this should be a generator, yield syntax wasn't working quite right though

        def visit(node):
            for child in node.children:
                visit(child)

            nodes.append(node)

        visit(self.root)

        return nodes

    def metadata_sum(self):
        return sum([sum(node.metadata) for node in self.all_nodes()])

    @classmethod
    def tree_from_headers(cls, license_input):
        """
        Expects a string license file consisting of a list of node headers.

        The navigation system's license file consists of a list of numbers (your puzzle input). The numbers define a
        structure which, when processed, produces some kind of tree that can be used to calculate the license number.

        The tree is made up of nodes; a single, outermost node forms the tree's root, and it contains all other nodes
        in the tree (or contains nodes that contain nodes, and so on).

        Sample input: "2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2"
        """
        numbers = deque([int(n) for n in license_input.split()])
        tree = Tree()

        def next_header():
            return NodeHeader(num_children=numbers.popleft(), num_metadata=numbers.popleft())

        def metadata(num):
            return [numbers.popleft() for _ in range(num)]

        def visit(header):
            node = tree.new_node()

            if header.num_children > 0:
                for _ in range(header.num_children):
                    node.children.append(
                        visit(next_header())
                    )

            node.metadata = metadata(header.num_metadata)

            return node

        tree.root = visit(next_header())

        return tree


def main():
    tree = Tree.tree_from_headers(license_file)

    print("Part 1:", tree.metadata_sum())
    print("Part 2:", tree.root.value)


if __name__ == '__main__':
    main()


class TestTree(unittest.TestCase):

    def setUp(self):
        self.sampleInput = "2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2"
        self.tree = Tree.tree_from_headers(self.sampleInput)

    def test_tree_from_license(self):
        assert len(self.tree.root.children) == 2
        assert len(self.tree.root.metadata) == 3

    def test_metadata_sum(self):
        assert self.tree.metadata_sum() == 138

    def test_node_value(self):
        print(self.tree.root.value)
        assert self.tree.root.value == 66


"""
--- Day 8: Memory Maneuver ---
The sleigh is much easier to pull than you'd expect for something its weight. Unfortunately, neither you nor the Elves
know which way the North Pole is from here.

You check your wrist device for anything that might help. It seems to have some kind of navigation system! Activating
the navigation system produces more bad news: "Failed to start navigation system. Could not read software license file."

The navigation system's license file consists of a list of numbers (your puzzle input). The numbers define a data
structure which, when processed, produces some kind of tree that can be used to calculate the license number.

The tree is made up of nodes; a single, outermost node forms the tree's root, and it contains all other nodes in the
 tree (or contains nodes that contain nodes, and so on).

Specifically, a node consists of:

A header, which is always exactly two numbers:
The quantity of child nodes.
The quantity of metadata entries.
Zero or more child nodes (as specified in the header).
One or more metadata entries (as specified in the header).
Each child node is itself a node that has its own header, child nodes, and metadata. For example:

2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2
A----------------------------------
    B----------- C-----------
                     D-----
In this example, each node of the tree is also marked with an underline starting with a letter for easier
identification. In it, there are four nodes:

A, which has 2 child nodes (B, C) and 3 metadata entries (1, 1, 2).
B, which has 0 child nodes and 3 metadata entries (10, 11, 12).
C, which has 1 child node (D) and 1 metadata entry (2).
D, which has 0 child nodes and 1 metadata entry (99).
The first check done on the license file is to simply add up all of the metadata entries. In this example, that
sum is 1+1+2+10+11+12+2+99=138.

What is the sum of all metadata entries?

--- Part Two ---
The second check is slightly more complicated: you need to find the value of the root node (A in the example above).

The value of a node depends on whether it has child nodes.

If a node has no child nodes, its value is the sum of its metadata entries. So, the value of node B is 10+11+12=33, 
and the value of node D is 99.

However, if a node does have child nodes, the metadata entries become indexes which refer to those child nodes. A 
metadata entry of 1 refers to the first child node, 2 to the second, 3 to the third, and so on. The value of this 
node is the sum of the values of the child nodes referenced by the metadata entries. If a referenced child node does 
not exist, that reference is skipped. A child node can be referenced multiple time and counts each time it is 
referenced. A metadata entry of 0 does not refer to any child node.

For example, again using the above nodes:

Node C has one metadata entry, 2. Because node C has only one child node, 2 references a child node which does not 
exist, and so the value of node C is 0.
Node A has three metadata entries: 1, 1, and 2. The 1 references node A's first child node, B, and the 2 references 
node A's second child node, C. Because node B has a value of 33 and node C has a value of 0, the value of node A 
is 33+33+0=66.

So, in this example, the value of the root node is 66.

What is the value of the root node?
"""
