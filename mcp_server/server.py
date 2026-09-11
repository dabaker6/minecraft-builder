from typing import List
import logging

from fastmcp import FastMCP
from core.buildservices.base import BuildService
from core.factories.build_factory import BuildFactory
from core.shapes.schemas import BuildResult, MapResult, PaletteResult, ShapeCatalogueResult, ShapeSpec, UndoResult

from core.logging import setup_logging

setup_logging()
logger = logging.getLogger("minecraft-buildbot-mcp")

mcp = FastMCP("Minecraft Buildbot")

def build_service() -> BuildService:
    """
    Create a shape builder service based on the configuration in the environment variables.
    """
    logger.info("Creating shape builder service")
    service = BuildFactory.create_shape_builder()
    logger.info("Shape builder service created successfully")
    return service

@mcp.tool()
def build(shapes: List[ShapeSpec]) -> BuildResult:
    """
    Build one or more shapes in the Minecraft world.

    Multiple shapes can be sent in one request. These shapes are placed in the order given, as a single build. The world uses
    (x, y, z) coordinates where y is height (up). Coordinates must be within the build zone. 
    
    For complex shapes, split the build into multiple build requests, for example if building a house, first build the walls, then the roof, then the floor. 
    This will allow for easier undoing of individual shapes.

    If you aren't confident of a shape, build it and then pause for input from the user before continuing with the next shape. 
    This will allow for easier undoing of individual components.

    The size of the map can be obtained through the map tool / resource.
    The available blocks can be obtained through the palette tool / resource.
    The available shapes can be obtained through the shape catalogue tool / resource 

    If a build looks wrong, call the undo tool to revert it.

    Returns a unique ID, a list of the names of the shapes placed, the initial number of blocks queued (queued), 
    the number of blocks dropped for being out of bounds (dropped) and the final number placed (kept)
    """
    return service.build(shapes)

@mcp.tool()
def undo() -> UndoResult:
    '''
    Undo the last build.

    When a build is requested all shapes for that build are placed on an undo stack. 
    If no builds are present an http 400 bad request is returned
    
    Returns the unique id of the build being reversed and a count of the blocks restored
    '''
    return service.undo()    
   

@mcp.resource("map://size")
def map() -> MapResult:
    '''
    Returns the size of the map in x, y and z planes as width, height and length.
    Blocks must be places within these bounds
    '''
    return service.map_size

# In case client does not support resources
@mcp.tool()
def get_map() -> MapResult:
    '''
    Returns the size of the map in x, y and z planes as width, height and length.
    Blocks must be places within these bounds
    '''
    return service.map_size

@mcp.resource("palette://blocks")
def blockids() -> PaletteResult:
    """
    Return all available blocks and their description

    Every block can be represented by a unique id, which is passed as the bid when building,
    and a human readable name. Use this method to help pick which block to use.
    Each server could have it's own list of blocks, so use this endpoint as a concrete list
    """
    return service.palette

# In case client does not support resources
@mcp.tool()
def get_blockids() -> PaletteResult:
    """
    Return all available blocks and their description

    Every block can be represented by a unique id, which is passed as the bid when building,
    and a human readable name. Use this method to help pick which block to use.
    Each server could have it's own list of blocks, so use this endpoint as a concrete list
    """
    return service.palette

@mcp.resource("catalogue://shapes")
def shape_catalogue() -> ShapeCatalogueResult:
    """
    Returns all available shapes

    All shapes that can be used to build alongside the parameters required to build them, and notes on their usage, including origin, orientation, sizes etc...
    """
    return service.shape_catalogue

# In case client does not support resources
@mcp.tool()
def get_shape_catalogue() -> ShapeCatalogueResult:
    """
    Returns all available shapes

    All shapes that can be used to build alongside the parameters required to build them, and notes on their usage, including origin, orientation, sizes etc...
    """
    return service.shape_catalogue

if __name__ == "__main__":
    logger.info("Starting Minecraft Buildbot MCP server")
    try:
        service: BuildService = build_service()       
        mcp.run()
    except Exception:
        logger.error(f"MCP server failed to start")
        raise