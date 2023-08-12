import inspect
import json
import subprocess
from abc import ABC, abstractmethod, abstractproperty
from typing import Callable

from staterestore import Stateful


def run(*cmd: str, filter: Callable = lambda x: x):
    args = " ".join(cmd).split(" ")
    res = subprocess.run(args, encoding="utf8", capture_output=True, check=True).stdout
    return filter(res)


def call(*cmd: str, filter: Callable = lambda x: x) -> dict:
    data = json.loads(run(*cmd, filter=filter))
    return {"state": data} if not isinstance(data, dict) else data


class ActionsABC(ABC):
    signals: list[int]

    def __init__(self, signals: list[int] | None = None, **kwargs) -> None:
        self.signals = signals or []
        super().__init__(**kwargs)

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

    def _exec(self, name: str):
        methods = self._public_methods()
        if name in methods:
            methods[name]()
        else:
            print("No such option:", name)
            self.help()
            exit(1)

    def _signal(self):
        """Signal waybar to update modules."""
        for signal in self.signals:
            run(f"pkill -SIGRTMIN+{signal} waybar")


class StatefulActions(ActionsABC):
    def __init__(self, statefuls: list[Stateful], **kwargs):
        self.statefuls = statefuls
        super().__init__(**kwargs)

    @property
    def engaged(self) -> bool:
        return self.statefuls[0].sanitised

    def on(self):
        for stateful in self.statefuls:
            stateful.sanitise()
        self._signal()

    def off(self):
        for stateful in self.statefuls:
            stateful.restore()
        self._signal()
