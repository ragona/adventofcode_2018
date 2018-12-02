import re


def number_grabber(string):
    return [int(s) for s in re.findall(r"(-?\d+)", string)]
