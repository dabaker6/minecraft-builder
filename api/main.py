from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse

from core.factories.build_factory import BuildFactory
from core.buildservices.base import BuildService
from core.shapes.schemas import BuildBatch, BuildInteruptedError, BuildResult, MapResult, ServerUnavailableError, ShapeCatalogueResult, UndoResult, BuildBusyError, PaletteResult

from core.palettes.palette import InvalidBlockError, PaletteError
from core.shapes.shapecatalogue import ShapeCatalogueError

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.service = BuildFactory.create_shape_builder()
    app.state.service.ensure_connected()  # Ensure the service is connected and ready
    yield
    app.state.service.close()

app = FastAPI(lifespan=lifespan, title="BuildBot API", description="API for Minecraft Classic BuildBot", version="0.1.0")

def get_service(request: Request) -> BuildService:
    return request.app.state.service

ServiceDep = Annotated[BuildService, Depends(get_service)]

@app.exception_handler(BuildBusyError)
async def build_busy_handler(request: Request, exc: BuildBusyError):
    return JSONResponse(status_code=409, content={"detail": str(exc)})

@app.exception_handler(BuildInteruptedError)
async def build_interrupted_handler(request: Request, exc: BuildInteruptedError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@app.exception_handler(ServerUnavailableError)
async def server_unavailable_handler(request: Request, exc: ServerUnavailableError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})

@app.exception_handler(IndexError)
async def no_undo_history_handler(request: Request, exc: IndexError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

@app.exception_handler(InvalidBlockError)
async def invalid_block_error(request: Request, exc: InvalidBlockError):
    return JSONResponse(status_code=400, content={"detail": str(exc), "hint": "please try /blockids to get a valid list of blocks"})

@app.exception_handler(PaletteError)
async def palette_error(request: Request, exc: PaletteError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.exception_handler(ShapeCatalogueError)
async def shape_description_error(request: Request, exc: ShapeCatalogueError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})

@app.post("/build")
def build(body: BuildBatch, service: ServiceDep) -> BuildResult:
    """
    Build one or more shapes in the Minecraft world.

    Multiple shapes can be sent in one request. These shapes are placed in the order given, as a single build. The world uses
    (x, y, z) coordinates where y is height (up). Coordinates must be within the build zone. 
    
    The size of the map can be obtained through the map tool.
    
    If a build looks wrong, call the undo tool to revert it.

    Returns a unique ID, a list of the names of the shapes placed, the initial number of blocks queued (queued), 
    the number of blocks dropped for being out of bounds (dropped) and the final number placed (kept)
    """    
    return service.build(body.shapes)

@app.post("/undo")
def undo(service: ServiceDep) -> UndoResult:
    '''
    Undo the last build.

    When a build is requested all shapes for that build are placed on an undo stack. 
    If no builds are present an http 400 bad request is returned

    Returns the unique id of the build being reversed and a count of the blocks restored
    '''
    return service.undo()    

@app.get("/map")
def map(service: ServiceDep) -> MapResult:
    '''    
    Returns the size of the map in x, y and z planes as width, height and length.
    Blocks must be places within these bounds
    '''
    return service.map_size

@app.get("/blockids")
def blockids(service: ServiceDep) -> PaletteResult:
    """
    Return all available blocks and their description

    Every block can be represented by a unique id, which is passed as the bid when building,
    and a human readable name. Use this method to help pick which block to use.
    Each server could have it's own list of blocks, so use this endpoint as a concrete list
    """
    return service.palette

@app.get("/shapecatalogue")
def shapecatalogue(service: ServiceDep) -> ShapeCatalogueResult:
    """
    Return all available shapes and their descriptions and notes on building

    All shapes available to build are listed, alongside parameters required and how the shape is constructed.
    For examplet the geometry of using vectors to align walls is described.
    """
    return service.shape_catalogue

if __name__ == "__main__":
    import uvicorn    
    uvicorn.run(app, host="127.0.0.1", port=8000)
    