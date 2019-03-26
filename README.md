# Advent of Code 2018

Advent of Code is a series of 25 holiday-themed coding challenges. This repository contains my solutions for 2018, along with brief notes on each of the puzzles.

# Challenges 

### Day 1: Chronal Calibration

**Part 1**: Sum a list of numbers. 

**Part 2**: Add up a cycle of numbers until you get the same total twice. All inputs have a cycle. 

### Day 2: Inventory Management System

**Part 1**: Count the number of letters in the IDs, apply the checksum as specified. 

**Part 2**: Find a pair of IDs that differ by only one character. Return their overlap. 

Finding the difference between two equal length strings has a cute one-liner: 
```python
return sum(x != y for x, y in zip(a, b))
```

Now, I don't know that summing booleans is the most obvious way to do this, and I almost always prefer obvious code to clever code, but this one is cute. For anyone who doesn't know why this works, Python bools are pretty much just aliases for 0 and 1, so you can sum them. 

### Day 3: No Matter How You Slice It

**Part 1**: Mark up a hashmap<(x, y), visit_count>, and sum up every square that is > 1.

**Part 2**: Find the piece of fabric where every square in the counting grid is 1. 

### Day 4: Repose Record

We're only considering the midnight hour; between 12:00AM and 12:59AM. We can use the input data to create a heatmap of how many minutes each guard sleeps during a particular minute:

```python
class Guard:

    def __init__(self, guard_id):
        self.guard_id = guard_id
        self.minutes = [0] * 60  # heatmaps of which minutes they sleep throughout their one hour shift

    @property
    def time_sleeping(self):
        return sum(self.minutes)

    @property
    def favorite_minute_to_sleep(self):
        sleep_amount = 0
        minute = 0
        for i, v in enumerate(self.minutes):
            if v > sleep_amount:
                sleep_amount = v
                minute = i

        return minute, sleep_amount
```

**Part 1**: Sort the guards by the the total minutes we've seen them sleeping.

```python
sleepiest_guard = sorted(parser.guards.values(), key=lambda x: x.time_sleeping)[-1]
```

**Part 2**: Sort the guards to find the one who is most consistent in their sleeping.

```python
most_consistent_guard = sorted(parser.guards.values(), key=lambda x: x.favorite_minute_to_sleep[1])[-1]
```

### Day 5: Alchemical Reduction

This one is fun. This could be a very long string, so you don't want to actually do string manipulation directly. A stack is the right data structure here, and all you're doing is thinking about the very end of the stack. Go through the input one character at a time, and if it reacts with the head of the stack, then pop off the stack and move along. Otherwise add it to the stack. 

```python
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
```
(To be continued...)
