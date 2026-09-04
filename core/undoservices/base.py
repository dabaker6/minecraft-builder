from dataclasses import dataclass
from typing import Protocol
import uuid
from core.shapebuilders.schemas import Block

@dataclass
class Snapshot:
    guid: uuid.UUID
    description: str
    blocks: list[Block]

class UndoService(Protocol):

    #def take_snapshot(self, undodata: list[Block], build_id: uuid.UUID) -> Snapshot:
    #    ...

    def add_snapshot(self, undodata: Snapshot) -> None:
        ...

    def get_snapshot(self, ) -> Snapshot | None:
        ...    