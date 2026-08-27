from typing import Protocol
import uuid
from shapebuilders.schemas import Block, MapResult, UndoResult

class BuildService(Protocol):

    def build(self, blocks: list[Block], build_id: uuid.UUID) -> tuple[int, int]:
        ...

    @property
    def map_size(self) -> MapResult:
        ...

    def close(self) -> None:
        ...

    def undo(self) -> UndoResult:
        ...