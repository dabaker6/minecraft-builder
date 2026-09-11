from core.buildservices.base import BuildService
from config import SHAPE_BUILDER
from core.buildservices import pyclassic
from core.factories.client_factory import ClientFactory
from core.palettes.palette import load_palette
from pyclassic import PyClassic
from core.factories.snapshot_factory import UndoFactory
from core.shapes.shapecatalogue import load_catalogue

class BuildFactory:
    @staticmethod    
    def create_shape_builder() -> BuildService:
        palette = load_palette()
        catalogue = load_catalogue()
        undoservice = UndoFactory.create_service()
        if SHAPE_BUILDER == "pyclassic":
            client = PyClassic(ClientFactory.create_auth(), client_name="buildbot_classic_api")
            return pyclassic.ShapeBuilderService(client=client, undoservice=undoservice, palette=palette, catalogue=catalogue)       
        raise ValueError(f"Unsupported SHAPE_BUILDER: {SHAPE_BUILDER}")