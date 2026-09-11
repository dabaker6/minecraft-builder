import json
from pathlib import Path

from config import BLOCK_PALETTE, PALETTE_DIR

class PaletteError(Exception):
    """
    Raised when a palette cannot be loaded or is malformed
    """

class InvalidBlockError(Exception):
    """
    Raised when an invalid block is requested
    """

class BlockPalette:

    def __init__(self, blocks: dict[str, str], source: str) -> None:
        self._blocks = blocks
        self._source = source

    @property
    def source(self) -> str:
        return self._source

    def as_dict(self) -> dict[str, str]:
        return dict(self._blocks)

    def name(self, bid: str) -> str | None:
        return self._blocks.get(bid)

    def is_valid(self, bid: int | str) -> bool:
        return bid in self._blocks

    def __len__(self) -> int:
        return len(self._blocks)

def _load_json(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise PaletteError(f"palette file not found {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise PaletteError(f"palette file is not valid json ({path}): {e}")

    return {str(k): str(v) for k, v in raw.items()} 

def load_palette() -> BlockPalette:

    palette_dir: Path = PALETTE_DIR
    base_path = palette_dir / f"{BLOCK_PALETTE}.json"
    blocks = _load_json(base_path)
    source = base_path.name

    if not blocks:
        raise PaletteError(f"palette '{BLOCK_PALETTE}' loaded but is empty")
    return BlockPalette(blocks=blocks, source=source)