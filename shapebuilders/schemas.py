import uuid

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Union, Literal, Annotated

# -------- exceptions ------
class BuildBusyError(Exception):
    pass

# ------ geometry --------

class Orientation(str, Enum):
    north = "north"
    south = "south"
    east = "east"
    west = "west"

class Block(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["block"] = "block"
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    z: int = Field(ge=0)
    bid: int = Field(ge=0)

# ------ requests --------

class CuboidBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["cuboid"]
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    z1: int = Field(ge=0)
    x2: int = Field(ge=0)
    y2: int = Field(ge=0)
    z2: int = Field(ge=0)
    bid: int = Field(ge=0)

class WallBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["wall"]
    length: int = Field(gt=0)
    height: int = Field(gt=0)
    orientation: Orientation
    ox: int = Field(ge=0)
    oy: int = Field(ge=0)
    oz: int = Field(ge=0)
    bid: int = Field(ge=0)

class EmptyCuboidBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["emptyCuboid"]
    xlength: int = Field(gt=0)
    zlength: int = Field(gt=0)
    height: int = Field(gt=0)
    ox: int = Field(ge=0)
    oy: int = Field(ge=0)
    oz: int = Field(ge=0)
    bid: int = Field(ge=0)

class FloorBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["floor"]
    x1: int = Field(ge=0)
    y: int = Field(ge=0)
    z1: int = Field(ge=0)
    x2: int = Field(ge=0)
    z2: int = Field(ge=0)
    bid: int = Field(ge=0)

class TriangleBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["triangle"]
    size: int = Field(ge=3)
    orientation: Orientation
    ox: int = Field(ge=0)
    oy: int = Field(ge=0)
    oz: int = Field(ge=0)
    bid: int = Field(ge=0)

class SlopeBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["slope"]
    length: int = Field(gt=0)
    height: int = Field(gt=0)
    orientation: Orientation
    ox: int = Field(ge=0)
    oy: int = Field(ge=0)
    oz: int = Field(ge=0)
    bid: int = Field(ge=0)

class PyramidBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["pyramid"]
    size: int = Field(ge=3)
    ox: int = Field(ge=0)
    oy: int = Field(ge=0)
    oz: int = Field(ge=0)
    bid: int = Field(ge=0)

# To implement
#class SphereBody(BaseModel):
#    model_config = ConfigDict(extra="forbid")
#    type: Literal["sphere"]
#    x: int
#    y: int
#    z: int
#    radius: int
#    bid: int

#Batch

ShapeSpec = Union [Block, CuboidBody, WallBody, EmptyCuboidBody, FloorBody, TriangleBody, SlopeBody, PyramidBody ]

class BuildBatch(BaseModel):
    """
    Annotated [T. x], adds metadata x to type T, in this case adds the type text to the ShapeSpec type
    """
    shapes: list[Annotated[ShapeSpec, Field(discriminator="type")]]

# ------ responses --------
class BuildResult(BaseModel):
    type: list[str]
    queued: int
    dropped: int 
    kept: int 
 
class UndoResult(BaseModel):
    build_id: uuid.UUID
    blocks_restored: int
 
class MapResult(BaseModel):
    width: int
    height: int
    length: int