#!/usr/bin/env python3
import json
from argparse import ArgumentParser

from cli import StatefulActions, call, run
from staterestore import Stateful


class IdleInhibit(Stateful):
    name = "idle"
    sanitised_state = {"ActiveState": "active"}

    def get_state(self) -> dict:
        def _filter(msg: str):
            k, v = next(
                l for l in msg.splitlines() if l.startswith("ActiveState")
            ).split("=")
            return f'{{"{k}":"{v}"}}'

        return call(
            "systemctl --user show --no-pager wayland-idle-inhibitor", filter=_filter
        )

    def set_state(self, state: dict):
        match state:
            case {"ActiveState": "active"}:
                run("systemctl --user start wayland-idle-inhibitor")
            case {"ActiveState": "inactive"}:
                run("systemctl --user stop wayland-idle-inhibitor")
            case x:
                print(f"Unknown state for {self.name}:", x)


class Actions(StatefulActions):
    def state(self):
        state = {
            True: {
                "tooltip": "Idle Inhibited",
                "alt": "on",
            },
            False: {
                "tooltip": "Disengaged",
                "alt": "off",
            },
        }.get(self.engaged)
        print(json.dumps(state))


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("cmd")
    args = parser.parse_args()
    Actions([IdleInhibit()], signals=[9])._exec(args.cmd)
