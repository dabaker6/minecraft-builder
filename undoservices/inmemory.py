from collections import deque
from uuid import UUID

from shapebuilders.schemas import Block
from undoservices.base import Snapshot, UndoService

class Undo(UndoService):
    def __init__(self):
        self._stack = deque(maxlen=50)

    def add_snapshot(self, undodata: Snapshot) -> None:
        self._stack.append(undodata)

    def get_snapshot(self) -> Snapshot | None:
        if self._stack:
            return self._stack.pop()