import json
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from pathlib import Path
from traceback import print_exception


class Logexception(AbstractContextManager):
    def __exit__(
        self,
        *args,
    ) -> bool | None:
        _, value, _ = args
        if value:
            print_exception(value)
        return True


class Stateful(ABC):
    name: str
    sanitised_state: dict

    def __init__(self, cachedir: Path = Path("/tmp/")):
        self.cachef = cachedir / f"{self.name}.json"

    @abstractmethod
    def get_state(self) -> dict:
        """Get current state"""

    @abstractmethod
    def set_state(self, state: dict):
        """Get given state"""

    def sanitise(self):
        print("Sanitising", self.name)
        with Logexception():
            if not self.cachef.exists():
                self.cachef.write_text(json.dumps(self.get_state()))
            self.set_state(self.sanitised_state)

    def restore(self):
        print("Restoring", self.name)
        with Logexception():
            self.set_state(json.loads(self.cachef.read_text()))
            self.cachef.unlink()

    @property
    def sanitised(self) -> bool:
        return self.cachef.is_file()
