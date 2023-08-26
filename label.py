#!/usr/bin/env python3

from argparse import ArgumentParser
from itertools import chain
from subprocess import run
from textwrap import wrap

LINE_LENGTH = 12
MAX_LINES = 3
PRINT_CMD = "enscript -#{} -fCourier-Bold16 --no-header -r"


def format_msg(msg, multipage=False):
    lines = (wrap(x, LINE_LENGTH) for x in msg.splitlines())
    lines = list(chain.from_iterable(lines))
    if not multipage and len(lines) > MAX_LINES:
        raise ValueError("Too many lines in input to fit on page.")

    # centre vertically
    while len(lines) < MAX_LINES:
        if len(lines) < MAX_LINES:
            lines.insert(0, "")
        if len(lines) < MAX_LINES:
            lines.append("")

    return "\n".join("{x:^{len}}".format(x=x, len=LINE_LENGTH) for x in lines)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--multipage", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-n", help="Number of copies.", type=int, default=1)
    parser.add_argument("MSG", nargs="+")
    args = parser.parse_args()
    msg = format_msg(" ".join(args.MSG), multipage=args.multipage)
    if not args.dry_run:
        run(PRINT_CMD.format(args.n).split(" "), input=msg, encoding="utf8")
    else:
        print(msg)
