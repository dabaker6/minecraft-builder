from buildservices.base import BuildService
from config import SHAPE_BUILDER
from buildservices import buildbot

class BuildFactory:
    @staticmethod
    def create_shape_builder() -> BuildService:
        if SHAPE_BUILDER == "pyclassic":
            return buildbot.ShapeBuilderService()       
        raise ValueError(f"Unsupported SHAPE_BUILDER: {SHAPE_BUILDER}")