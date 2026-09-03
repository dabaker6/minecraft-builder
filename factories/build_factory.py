from buildservices.base import BuildService
from config import SHAPE_BUILDER
from buildservices import pyclassic
from factories.client_factory import ClientFactory
from palettes.palette import load_palette
from pyclassic import PyClassic
from factories.snapshot_factory import UndoFactory

class BuildFactory:
    @staticmethod    
    def create_shape_builder() -> BuildService:
        palette = load_palette()
        undoservice = UndoFactory.create_service()
        if SHAPE_BUILDER == "pyclassic":
            client = PyClassic(ClientFactory.create_auth(), client_name="buildbot_classic_api")
            return pyclassic.ShapeBuilderService(client=client, undoservice=undoservice, palette=palette)       
        raise ValueError(f"Unsupported SHAPE_BUILDER: {SHAPE_BUILDER}")