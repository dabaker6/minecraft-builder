from buildservices.base import BuildService
from config import SHAPE_BUILDER
from buildservices import pyclassic
from palettes.palette import load_palette

class BuildFactory:
    @staticmethod    
    def create_shape_builder() -> BuildService:
        palette = load_palette()
        if SHAPE_BUILDER == "pyclassic":
            return pyclassic.ShapeBuilderService(palette=palette)       
        raise ValueError(f"Unsupported SHAPE_BUILDER: {SHAPE_BUILDER}")