import re
import heapq
import unittest
from string import ascii_uppercase
from collections import defaultdict, deque


log_parser = re.compile(" (.) .+ (.) ")
pairs = [log_parser.search(line.strip()).groups() for line in open("input/day_07.txt").readlines()]


BASE_COST = 60
DEBUG = True


def make_graph():
    graph = Graph()
    for a, b in pairs:
        graph.connect(a, b)
    return graph


class Graph:

    class Node:

        def __init__(self, data=None):
            self.data = data
            self.indegree = 0
            self.children = set()

        def __hash__(self):
            return hash(self.data)

        def __eq__(self, other):
            return self.data == other.data

        def __lt__(self, other):
            return self.data < other.data

        def __repr__(self):
            return f"Node(" \
                f"data={self.data}, " \
                f"indegree={self.indegree}, " \
                f"children=({''.join(n.data for n in sorted(self.children))}))"

        @property
        def cost(self):
            return ascii_uppercase.find(self.data) + 1 + BASE_COST

    def __init__(self):
        self.nodes = defaultdict(Graph.Node)

    def __getitem__(self, item):
        if not isinstance(item, str):
            raise TypeError("Expected a string")

        node = self.nodes[item]
        if node.data is None:
            node.data = item

        return node

    def connect(self, a, b):
        node_a = self[a]
        node_b = self[b]
        node_a.children.add(node_b)
        node_b.indegree += 1


class Worker:
    def __init__(self):
        self.job = None
        self.remaining_cost = 0

    def __repr__(self):
        if not self.job:
            return " . "
        return f" {self.job.data} "

    @property
    def free(self):
        return not self.job or self.remaining_cost == 0

    def set_job(self, job):
        self.job = job
        if job:
            self.remaining_cost = job.cost

    def work(self):
        if self.job and self.remaining_cost > 0:
            self.remaining_cost -= 1


def time_with_workers(graph, num_workers=5):
    workers = [Worker() for _ in range(num_workers)]
    work_queue = deque(list(find_graph_order(graph)))  # todo: after a refactor I don't think this needs to be a deque
    total_seconds = 0
    done = set()  # used for debug drawing
    in_progress = set()

    def work():
        for worker in workers:

            if not worker.free:
                worker.work()

            elif worker.free:

                if worker.job and worker.job in in_progress:
                    in_progress.remove(worker.job)
                    done.add(worker.job)

                new_job = next_job()
                if new_job:
                    in_progress.add(new_job)

                worker.set_job(new_job)
                worker.work()  # do one round of work immediately on the new job

    def next_job():
        if not work_queue:
            return None

        seen = set()
        for potential_job in work_queue:
            seen.add(potential_job)
            if node_is_ready(potential_job, blockers=seen | in_progress):
                work_queue.remove(potential_job)
                return potential_job

        return None

    def node_is_ready(potential_job, blockers):
        for node in blockers:
            if potential_job in node.children:
                return False
        return True

    work()  # example has one round of work before the 0th second. I think this is causing an off-by-one for me.

    while work_queue or in_progress:
        work()
        total_seconds += 1

    return total_seconds


def simple_graph():
    """
    Test case graph from the challenge text.
    """
    graph = Graph()
    graph.connect("C", "A")
    graph.connect("C", "F")
    graph.connect("A", "B")
    graph.connect("A", "D")
    graph.connect("B", "E")
    graph.connect("D", "E")
    graph.connect("F", "E")
    return graph


def find_graph_order(graph):
    ready = sorted([node for node in graph.nodes.values() if node.indegree == 0])

    while ready:
        node = heapq.heappop(ready)

        for child in node.children:
            child.indegree -= 1
            if child.indegree == 0:
                heapq.heappush(ready, child)

        yield node


class TestGraph(unittest.TestCase):

    def setUp(self):
        self.graph = simple_graph()

    def test_graph_order(self):
        order = find_graph_order(self.graph)
        assert ''.join([node.data for node in order]) == 'CABDFE'

    def test_time_with_workers(self):
        global BASE_COST
        BASE_COST = 0
        time = time_with_workers(self.graph, 2)
        if time != 15:
            raise Exception(f"Expected 15, got {time}")

    def test_part_1(self):
        print("Part 1:", ''.join([node.data for node in find_graph_order(make_graph())]))

    def test_part_2(self):
        print("Part 2:", time_with_workers(make_graph()))



if __name__ == '__main__':
    unittest.main()


"""
--- Day 7: The Sum of Its Parts ---
You find yourself standing on a snow-covered coastline; apparently, you landed a little off course. The region is 
too hilly to see the North Pole from here, but you do spot some Elves that seem to be trying to unpack something 
that washed ashore. It's quite cold out, so you decide to risk creating a paradox by asking them for directions.

"Oh, are you the search party?" Somehow, you can understand whatever Elves from the year 1018 speak; you assume 
it's Ancient Nordic Elvish. Could the device on your wrist also be a translator? "Those clothes don't look very 
warm; take this." They hand you a heavy coat.

"We do need to find our way back to the North Pole, but we have higher priorities at the moment. You see, believe 
it or not, this box contains something that will solve all of Santa's transportation problems - at least, that's 
what it looks like from the pictures in the instructions." It doesn't seem like they can read whatever language it's 
in, but you can: "Sleigh kit. Some assembly required."

"'Sleigh'? What a wonderful name! You must help us assemble this 'sleigh' at once!" They start excitedly pulling 
more parts out of the box.

The instructions specify a series of steps and requirements about which steps must be finished before others can 
begin (your puzzle input). Each step is designated by a single letter. For example, suppose you have the following 
instructions:

Step C must be finished before step A can begin.
Step C must be finished before step F can begin.
Step A must be finished before step B can begin.
Step A must be finished before step D can begin.
Step B must be finished before step E can begin.
Step D must be finished before step E can begin.
Step F must be finished before step E can begin.
Visually, these requirements look like this:


  -->A--->B--
 /    \      \
C      -->D----->E
 \           /
  ---->F-----
Your first goal is to determine the order in which the steps should be completed. If more than one step is ready, 
choose the step which is first alphabetically. In this example, the steps would be completed as follows:

Only C is available, and so it is done first.
Next, both A and F are available. A is first alphabetically, so it is done next.
Then, even though F was available earlier, steps B and D are now also available, and B is the first alphabetically of 
the three.
After that, only D and F are available. E is not available because only some of its prerequisites are complete. 
Therefore, D is completed next.
F is the only choice, so it is done next.
Finally, E is completed.
So, in this example, the correct order is CABDFE.

In what order should the steps in your instructions be completed?

--- Part Two ---
As you're about to begin construction, four of the Elves offer to help. "The sun will set soon; it'll go faster if
we work together." Now, you need to account for multiple people working on steps simultaneously. If multiple steps
are available, workers should still begin them in alphabetical order.

Each step takes 60 seconds plus an amount corresponding to its letter: A=1, B=2, C=3, and so on. So, step A takes
60+1=61 seconds, while step Z takes 60+26=86 seconds. No time is required between steps.

To simplify things for the example, however, suppose you only have help from one Elf (a total of two workers) and
that each step takes 60 fewer seconds (so that step A takes 1 second and step Z takes 26 seconds). Then, using the
same instructions as above, this is how each second would be spent:

Second   Worker 1   Worker 2   Done
   0        C          .
   1        C          .
   2        C          .
   3        A          F       C
   4        B          F       CA
   5        B          F       CA
   6        D          F       CAB
   7        D          F       CAB
   8        D          F       CAB
   9        D          .       CABF
  10        E          .       CABFD
  11        E          .       CABFD
  12        E          .       CABFD
  13        E          .       CABFD
  14        E          .       CABFD
  15        .          .       CABFDE
Each row represents one second of time. The Second column identifies how many seconds have passed as of the beginning
of that second. Each worker column shows the step that worker is currently doing (or . if they are idle). The Done
column shows completed steps.

Note that the order of the steps has changed; this is because steps now take time to finish and multiple workers
can begin multiple steps simultaneously.

In this example, it would take 15 seconds for two workers to complete these steps.

With 5 workers and the 60+ second step durations described above, how long will it take to complete all of the steps?

---

if DEBUG:
    drawing.draw_graph_nodes(
        nodes=graph.nodes.values(),
        in_progress=in_progress,
        done=done,
        name=f'day07-{str(total_seconds).zfill(4)}',
    )

        print(f"{total_seconds:4}", ''.join([f"{worker} " for worker in workers]))

"""
