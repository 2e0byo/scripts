#!/usr/bin/python3
import sqlite3
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

parser = ArgumentParser()
parser.add_argument(
    "--dbfile",
    type=Path,
    default=Path("~/.local/share/qutebrowser/history.sqlite").expanduser(),
)
parser.add_argument("--keep-months", type=int, default=6)
args = parser.parse_args()
cutoff = round((datetime.now() - timedelta(days=30 * args.keep_months)).timestamp())
con = sqlite3.connect(args.dbfile)
cur = con.cursor()
cur.execute("DELETE FROM history WHERE atime < ?", (cutoff,))
cur.execute("DELETE FROM CompletionHistory WHERE last_atime < ?", (cutoff,))
con.commit()
con.close()
