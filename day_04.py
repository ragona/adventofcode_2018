import re
from datetime import datetime


log_parser = re.compile(r"\[(.*)\]\s(.*)")
guard_finder = re.compile(r"#(\d+)")

with open("input/day_04.txt", 'r') as input_file:
    lines = [line.strip() for line in input_file.readlines()]


class Guard:

    def __init__(self, guard_id):
        self.guard_id = guard_id
        self.minutes = [0] * 60  # heatmaps of which minutes they sleep throughout their one hour shift

    def __repr__(self):
        return f"Guard(id={self.guard_id}, time_sleeping={self.time_sleeping})"

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


class LogEntry:

    SHIFT_START = "shift_start"
    FALLS_ASLEEP = "falls_asleep"
    WAKES_UP = "wakes_up"

    def __init__(self, time, log, guard_id):
        self.time = time
        self.log = log
        self.guard_id = guard_id
        self.entry_type = None

        if self.log[0] == "G":  # "Guard #XXX begins shift"
            self.entry_type = LogEntry.SHIFT_START
        elif self.log[0] == "f":  # "falls asleep"
            self.entry_type = LogEntry.FALLS_ASLEEP
        elif self.log[0] == "w":  # "wakes up"
            self.entry_type = LogEntry.WAKES_UP

    def __repr__(self):
        return f"LogEntry(time={self.time}, log={self.log}, guard_id={self.guard_id})"

    def parse_guard_id(self):
        return int(guard_finder.search(self.log).groups()[0])


class LogParser:

    def __init__(self):
        self.entries = []
        self.guards = dict()  # map[guard_id]Guard

        self._parse_lines()
        self._sort_entries()
        self._analyze_entries()

    def _parse_lines(self):
        for line in lines:
            try:
                groups = log_parser.search(line).groups()
                time = datetime.strptime(groups[0], '%Y-%m-%d %H:%M')
                log = groups[1]

                self.entries.append(
                    LogEntry(time=time, log=log, guard_id=None)
                )
            except Exception:
                raise ValueError(f"Failed to parse: '{line}'")

    def _sort_entries(self):
        self.entries.sort(key=lambda x: x.time)

    def _analyze_entries(self):
        guard = None

        for i, entry in enumerate(self.entries):

            if entry.entry_type == LogEntry.SHIFT_START:
                guard = self._get_or_create_guard(entry.parse_guard_id())

            elif entry.entry_type == LogEntry.WAKES_UP:
                for j in range(self.entries[i - 1].time.minute, entry.time.minute):
                    guard.minutes[j] += 1

            entry.guard_id = guard.guard_id  # entries don't have guard ids yet, since they're created out of order

    def _get_or_create_guard(self, guard_id):
        if guard_id in self.guards:
            guard = self.guards[guard_id]
        else:
            guard = Guard(guard_id)
            self.guards[guard_id] = guard
        return guard


def main():

    parser = LogParser()

    sleepiest_guard = sorted(parser.guards.values(), key=lambda x: x.time_sleeping)[-1]
    favorite_minute, _ = sleepiest_guard.favorite_minute_to_sleep

    print("part 1:", sleepiest_guard.guard_id * favorite_minute)

    most_consistent_guard = sorted(parser.guards.values(), key=lambda x: x.favorite_minute_to_sleep[1])[-1]
    favorite_minute, _ = most_consistent_guard.favorite_minute_to_sleep

    print("part 2:", most_consistent_guard.guard_id * favorite_minute)


if __name__ == '__main__':
    main()
