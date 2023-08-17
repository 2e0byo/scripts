#!/usr/bin/env python3
import json
from argparse import ArgumentParser
from urllib import request

from cli import StatefulActions, call, run
from idle_inhibit import IdleInhibit
from staterestore import Stateful


def post(url: str, data: dict) -> dict:
    req = request.Request(
        url,
        method="POST",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req) as f:
        if f.status != 200:
            raise Exception(f"Status code is {f.status}")
        return json.load(f)


class JsonRPC:
    _id = 0

    def __init__(self, url: str):
        self.url = url

    @property
    def id(self) -> int:
        self._id += 1
        return self._id

    def call(self, method: str, params: dict | list | None = None):
        params = params or []
        data = post(
            self.url,
            {
                "jsonrpc": "2.0",
                "id": self.id,
                "method": method,
                "params": params,
            },
        )
        if data.get("error"):
            raise Exception(data)
        else:
            return data["result"]


class Notifications(Stateful):
    name = "notifications"
    sanitised_state = {"state": True}

    def get_state(self) -> dict:
        return call("dunstctl is-paused")

    def set_state(self, state: dict):
        run("dunstctl set-paused", json.dumps(state["state"]))


class Mopidy(Stateful):
    name = "mopidy"
    sanitised_state = {"state": "paused"}

    def __init__(self, *args, **kwargs):
        self.mopidy = JsonRPC("http://localhost:6680/mopidy/rpc")
        super().__init__(*args, **kwargs)

    def get_state(self) -> dict:
        return {"state": self.mopidy.call("core.playback.get_state")}

    def set_state(self, state: dict):
        self.mopidy.call(
            {
                "paused": "core.playback.pause",
                "playing": "core.playback.play",
                "stopped": "core.playback.stop",
            }[state["state"]]
        )


statefuls: list[Stateful] = [
    Notifications(),
    Mopidy(),
    IdleInhibit(),
]


class Actions(StatefulActions):
    """Sanitise the system during a video call."""

    def on(self):
        super().on()

    def off(self):
        super().off()

    def state(self):
        state = {
            True: {
                "tooltip": "System Sanitised",
                "alt": "sanitised",
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
    Actions(statefuls, signals=[8, 9])._exec(args.cmd)
