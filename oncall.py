#!/usr/bin/env python3
import json
from argparse import ArgumentParser
from pathlib import Path
from urllib import request

from cli import StatefulActions, call, run
from idle_inhibit import IdleInhibit
from staterestore import Stateful


def _req(method: str, url: str, data: dict, headers: dict) -> dict:
    kwargs = {"method": method, "headers": headers}
    if data:
        kwargs["data"] = json.dumps(data).encode()
        kwargs["headers"] |= {"Content-Type": "application/json"}
    req = request.Request(url, **kwargs)
    with request.urlopen(req) as f:
        if f.status != 200:
            raise Exception(f"Status code is {f.status}")
        return json.load(f)


def post(url: str, data: dict, headers: dict | None = None) -> dict:
    return _req("POST", url, data=data, headers=headers or {})


def get(url: str, headers: dict | None = None) -> dict:
    return _req("GET", url, headers=headers or {}, data={})


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


class OnCallSensor(Stateful):
    name = "oncall"
    sanitised_state = {"state": "true"}
    url = "https://home.2e0byo.co.uk/api/states/binary_sensor.on_call"

    def __init__(self):
        token = Path("~/.pass/on-call").expanduser().read_text().strip()
        self.headers = {"Authorization": f"Bearer {token}"}
        super().__init__()

    def get_state(self) -> dict:
        return {"state": get(self.url, headers=self.headers)["state"]}

    def set_state(self, state: dict):
        post(self.url, state, self.headers)


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
        self.mopidy.call("core.playback.set_state", params=[state["state"]])


statefuls: list[Stateful] = [
    Notifications(),
    Mopidy(),
    IdleInhibit(),
    OnCallSensor(),
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
