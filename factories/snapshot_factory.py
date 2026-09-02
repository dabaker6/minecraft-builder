from config import SNAPSHOT_STORE
from undoservices.base import UndoService
from undoservices import inmemory

class UndoFactory:
    @staticmethod
    def create_service() -> UndoService:
        if SNAPSHOT_STORE == "in_memory":
            return inmemory.Undo()
        raise ValueError(f"Unsupported SNAPSHOT_STORE: {SNAPSHOT_STORE}")