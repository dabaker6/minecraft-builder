from typing import Protocol

class BuildService(Protocol):

    def add_shape(self, shape) -> tuple[int, int]:
        ...

    @property
    def pending(self) -> int:
        ...

    def _enqueue(self, blocks) -> tuple[int, int]:
        ...

    def execute(self) -> int:
        ...

    def close(self) -> None:
        ...

    def undo(self) -> None:
        ...