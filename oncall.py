#!/usr/bin/env python3
import inspect
import json
import subprocess
from abc import ABC, abstractmethod, abstractproperty
from argparse import ArgumentParser
from typing import Callable
from urllib import request

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


def run(*cmd: str, filter: Callable = lambda x: x):
    args = " ".join(cmd).split(" ")
    res = subprocess.run(args, encoding="utf8", capture_output=True, check=True).stdout
    return filter(res)


def call(*cmd: str, filter: Callable = lambda x: x) -> dict:
    data = json.loads(run(*cmd, filter=filter))
    return {"state": data} if not isinstance(data, dict) else data


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


statefuls: list[Stateful] = [
    Notifications(),
    Mopidy(),
    IdleInhibit(),
]


class ActionsABC(ABC):
    @abstractproperty
    def engaged(self) -> bool:
        """Current state"""

    @abstractmethod
    def on(self):
        """Engage."""

    @abstractmethod
    def off(self):
        """Disengage."""

    def toggle(self):
        if self.engaged:
            self.off()
        else:
            self.on()

    def _public_methods(self) -> dict[str, Callable]:
        return {
            m: meth
            for m in dir(self)
            if not m.startswith("_") and callable(meth := getattr(self, m))
        }

    def help(self):
        """Display this message and exit."""

        doc = """
{overall}

Commands:
	{commands}
        """.format(
            overall=inspect.getdoc(self),
            commands="\n\t".join(
                f"{k}:\t{inspect.getdoc(v)}" for k, v in self._public_methods().items()
            ),
        )
        print(doc)


class Actions(ActionsABC):
    """Sanitise the system during a video call."""

    def __init__(self, statefuls: list[Stateful]):
        self.statefuls = statefuls

    @property
    def engaged(self) -> bool:
        return self.statefuls[0].sanitised

    def on(self):
        for stateful in self.statefuls:
            stateful.sanitise()

    def off(self):
        for stateful in self.statefuls:
            stateful.restore()

    def _exec(self, name: str):
        methods = self._public_methods()
        if name in methods:
            methods[name]()
        else:
            print("No such option:", name)
            self.help()
            exit(1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("cmd")
    args = parser.parse_args()
    Actions(statefuls)._exec(args.cmd)
