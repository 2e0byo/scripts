#!/usr/bin/python3

from time import sleep, monotonic
from sys import argv


def parse_time(t):
    d = {'h': 0, 'm': 0, 's': 0}
    for unit in d:
        if unit in t:
            (d[unit], t) = t.split(unit)
        try:
            d[unit] = int(d[unit])
        except ValueError:
            print('error parsing:', d[unit], unit, t)
            d[unit] = 0

    return (d['s'] + d['m'] * 60 + d['h'] * 3600)


def count_down(tminus):
    while tminus > 0:
        start = monotonic()
        (m, s) = divmod(tminus, 60)
        (h, m) = divmod(m, 60)
        print("%d:%02d:%02d" % (h, m, s), end='\r')
        sleep(1 + start - monotonic())
        tminus -= 1


def count_up(t=0):
    while True:
        start = monotonic()
        (m, s) = divmod(t, 60)
        (h, m) = divmod(m, 60)
        print("%d:%02d:%02d" % (h, m, s), end='\r')
        sleep(1 + start - monotonic())
        t += 1


t = argv[1]
if t == "-up":
    try:
        t = parse_time(argv[2])
    except IndexError:
        t = 0
    count_up(t)
else:
    count_down(parse_time(t))
