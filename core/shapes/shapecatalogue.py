import json
from pathlib import Path

from config import SHAPE_CATALOGUE, SHAPE_CATALOGUE_DIR

_REQUIRED_FIELDS = {"description", "parameters", "notes"}

class ShapeCatalogueError(Exception):
    """
    Raised when a shape description cannot be loaded or is malformed
    """

class ShapeCatalogue:

    def __init__(self, catalogue: dict[str, dict[str, str]], source: str) -> None:
        self._catalogue = catalogue
        self._source = source        

    @property
    def source(self) -> str:
        return self._source

    def as_dict(self) -> dict[str, dict[str, str]]:
        return dict(self._catalogue)

    def names(self) -> list[str] | None:
        return [name for name in self._catalogue.keys()]

    def __len__(self) -> int:
        return len(self._catalogue)

def _load_json(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        raise ShapeCatalogueError(f"shape descriptions file not found {path}")

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ShapeCatalogueError(f"shape descriptions file is not valid json ({path}): {e}")

    shapes: dict[str, dict[str, str]] = {}
    for name, entry in raw.items():
        if not isinstance(entry, dict):
            raise ShapeCatalogueError(f"shape '{name}' entry must be a dict")

        missing = _REQUIRED_FIELDS - entry.keys()
        if missing:
            raise ShapeCatalogueError(f"shape '{name}' entry is missing required fields: {missing}")
        shapes[name] = {str(k): str(v) for k, v in entry.items()}

    return shapes

def load_catalogue() -> ShapeCatalogue:

    shape_catalogue_dir = SHAPE_CATALOGUE_DIR
    base_path = shape_catalogue_dir / f"{SHAPE_CATALOGUE}.json"
    catalogue = _load_json(base_path)
    source = base_path.name

    if not catalogue:
        raise ShapeCatalogueError(f"Shape catalogue '{SHAPE_CATALOGUE}' loaded but is empty")
    return ShapeCatalogue(catalogue=catalogue, source=source)