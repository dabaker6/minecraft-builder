from typing import Protocol
from core.shapes.schemas import MapResult, PaletteResult, ShapeCatalogueResult, ShapeSpec, UndoResult, BuildResult

class BuildService(Protocol):

    def ensure_connected(self) -> None:
        ...
        
    def build(self, shapes: list[ShapeSpec]) -> BuildResult:
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

    @property
    def shape_catalogue(self) -> ShapeCatalogueResult:
        ...