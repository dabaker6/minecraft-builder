from typing import Protocol
import uuid
from shapebuilders.schemas import Block, MapResult, PaletteResult, UndoResult

class BuildService(Protocol):

    def build(self, blocks: list[Block], build_id: uuid.UUID) -> tuple[int, int]:
        ...

    def close(self) -> None:
        ...

    def undo(self) -> UndoResult:
        ...

    def is_valid_block(self, bid: str) -> bool:
        ...

    @property
    def palette(self) -> PaletteResult:
        ...

    @property
    def map_size(self) -> MapResult:
        ...        