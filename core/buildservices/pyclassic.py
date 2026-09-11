import asyncio
import logging
from threading import Lock
import threading
import time
from core.buildservices.base import BuildService
from core.shapes.shapecatalogue import ShapeCatalogue
from core.shapes.shapesbuilder import BUILDERS
from core.shapes.schemas import Block, BlockInfo, BuildBusyError, BuildInteruptedError, BuildResult, MapResult, PaletteResult, ServerUnavailableError, ShapeCatalogueResult, ShapeSpec, UndoResult
from core.palettes.palette import BlockPalette, InvalidBlockError
from core.undoservices.base import Snapshot, UndoService
import uuid

from pyclassic import PyClassic
from pyclassic.queue import ThreadedQueue, QueueError
from pyclassic.map import ClassicMap

from core.logging import setup_logging

from api.validator import in_bounds
from config import SERVER_IP, SERVER_PORT, USERNAME

setup_logging()
logger = logging.getLogger("minecraft-buildbot-pyclassic")

class ShapeBuilderService(BuildService):
    def __init__(
            self, 
            client: PyClassic,
            undoservice: UndoService,
            palette: BlockPalette,
            catalogue: ShapeCatalogue
            ):       
        # constructed palette
        self._palette = palette
        # constructed catalogue
        self._catalogue = catalogue
        # constructed client
        self._bot = client
        # constructed undoservice
        self._undoservice = undoservice
        # flag for lazy loading of connection and map
        self._ready = False
        
        # create thread safe queue        
        self._queue = ThreadedQueue(self._bot)        
        self._lock = Lock() # lock
        self._connect_lock = Lock() # lock for connection and map loading
        
    def _is_alive(self) -> bool:
        if not self._ready or self._bot is None:
            return False

        #if self._queue.is_active():        # a build is draining — skip, it's keeping the connection busy anyway
        #    return True
         
        if self._queue.thread and self._queue.thread.is_alive():  # queue thread is alive, so the connection is likely alive
            return True
        
        try:
            self._liveness_check()
            return True
        except Exception as e:
            logger.warning(f"Connection check failed: {e}")
            return False

    def _liveness_check(self):
        players = self._bot.players.values()
        player = next((p for p in players if p.name == USERNAME), None)

        if player is not None:
            self._bot.client.move(player.x // 32, player.y // 32 + 2, player.z // 32)  # move to current position to trigger a server response
            logger.info("Keepalive check sent successfully")
        else:
            logger.warning(f"Player {USERNAME} not found in player list during liveness check.")
            self._bot.client.message("I am still here!")  # send a message to trigger a server response

    def ensure_connected(self):        
        with self._connect_lock:
            is_alive = self._is_alive()
            if self._ready and is_alive:
                return

            if self._ready and not is_alive:
                logger.warning("Connection lost, attempting to reconnect")
                self._teardown()

            self._connect()

    def _connect(self):
        # create threading event to signal when map is ready
        try:
            self._map_ready = threading.Event()
            self._register_map_ready_hook()

            # start listener
            self._listener = threading.Thread(
                target=self._run_listener,
                name="pyclassic-listener",
                daemon=True
            )

            self._listener.start()

            self._wait_for_map(timeout=20)

            # create service local map
            self._localmap: ClassicMap = self._bot.map.copy()
            self._ready = True

        except Exception as e:
            logger.error(f"Error occurred during connection: {e}")
            self._disconnect()
            self._ready = False
            raise ServerUnavailableError(f"Failed to connect and load map") from e

    def _teardown(self):
        '''
        Runs disconnect and clears snapshots to avoid stale data.
        '''
        self._disconnect()
        self._undoservice.clear_snapshots() 

    def _disconnect(self):
        '''
        Disconnects the bot and stops the queue. C
        Queue is stopped to ensure a clean shutdown and in the case a build failed mid-build it avoids a dead thread. 
        The listener thread is a daemon, so it will exit when the main thread exits (when recv() fails on the closed socket).
        '''
        self._ready = False
        try:
            self._queue.stop()
        except Exception as e:
            logger.error(f"Error occurred while stopping queue: {e}")

        try:
            self._bot.disconnect()
            # listener thread is daemon, so it will exit when main thread exits (when recv() fails on the closed socket)
            
        except Exception as e:
            logger.error(f"Error occurred while disconnecting bot: {e}")


    def _register_map_ready_hook(self):
        '''
        Has to be wrapped in function to access self
        '''
        @self._bot.event
        async def on_recv(info, _packet): # _packet is not used intentionally
            if info.name == "LEVEL_FINALIZE":
                self._map_ready.set()

    def _run_listener(self):
        try:
            # A freshly-spawned thread has no asyncio loop; run() calls
            # get_event_loop(), so give THIS thread its own loop first.
            asyncio.set_event_loop(asyncio.new_event_loop())
            # run() connects (if not already) AND runs the blocking event loop.
            self._bot.run(ip=SERVER_IP, port=SERVER_PORT)
        except Exception as e:
            # A daemon thread that raises vanishes silently — surface it.
            logger.error(f"Listener thread died: {e!r}")    

    def _wait_for_map(self, timeout=5):
        # event waits for map to load
        if not self._map_ready.wait(timeout=timeout):
            raise RuntimeError(
                "map did not load within timeout"
            )

        # set deadline for map to load
        deadline = time.time() + 2
        while self._bot.map is None and time.time() < deadline:
            time.sleep(0.05)

        if self._bot.map is None:
            raise RuntimeError(
                "LEVEL_FINALISE emitted but map not loaded"
            )
        logger.info(f"Map loaded {self._bot.map.width} x {self._bot.map.height} x {self._bot.map.length}")

    def _updatelocalmap(self, blocks: list[Block]):        
        for b in blocks:
            try:
                bid: int = int(b.bid)
                self._localmap[b.x, b.y, b.z] = bid
            except ValueError:
                logger.error(f"Not a valid block Id {b}")                    

    def _take_snapshot(self, blocks: list[Block], build_id: uuid.UUID) -> Snapshot:
                    
        map_blocks = []
        '''
        Need to convert blocks here too
        '''
        [map_blocks.append(Block(x=b.x,y=b.y,z=b.z, bid=self._get_block_type(b))) for b in blocks]
        
        return Snapshot(
            guid=build_id,
            description="",
            blocks=map_blocks
            )        

    def _get_block_type(self, block: Block) -> int:
        block_type = self._localmap[block.x,block.y,block.z]
        assert isinstance(block_type, int)
        return(block_type)

    def _add_to_queue(self, converted_blocks: list[Block]):
        try:
            self._queue.add_queue(converted_blocks)
        except QueueError as e:                
            
            if self._queue.thread and not self._queue.thread.is_alive():
                logger.error("Queue thread is not alive (connection lost midbuild); build failed")
                raise BuildInteruptedError("Failed to add build to queue; Please retry to reconnect and rebuild.")
            else:
                logger.error(f"Build rejected queue busy: {e}")
                raise BuildBusyError("A build is already in progress; pleases try again shortly")

    def build(self, shapes: list[ShapeSpec]) -> BuildResult: 
        # ensure connection and map are ready
        self.ensure_connected()
        build_id = uuid.uuid4()
        blocks = []
        shape_types = []
        
        for shape in shapes:        
            blocks_list = BUILDERS[shape.type](shape)
            blocks.extend(blocks_list)
            shape_types.append(shape.type)

        with self._lock:

            kept = [b for b in blocks if in_bounds(b.x, b.y, b.z)]

            invalid = [b.bid for b in kept if not self.is_valid_block(b.bid)]

            if  invalid:
                raise InvalidBlockError(f"Unknown block IDs: {set(invalid)}")

            converted_blocks = []
            for b in kept:
                try:
                    bid: int = int(b.bid)
                    converted_blocks.append(Block(x=b.x, y=b.y, z=b.z, bid=bid))
                except ValueError:
                    logger.error(f"Not a valid block Id {b}")

            #take snapshot of map for undo
            snapshot: Snapshot = self._take_snapshot(converted_blocks, build_id)

        
            self._add_to_queue(converted_blocks)
            
            self._queue.start_all()            

            #update local map
            self._updatelocalmap(converted_blocks)
            self._undoservice.add_snapshot(snapshot)
        return BuildResult(
            shape_types=shape_types, 
            queued=len(blocks),
            dropped=len(blocks) - len(converted_blocks),
            kept=len(kept),
            build_id=build_id)        
    
    def close(self):
        try:
            self._queue.stop()
        except Exception as e:
            logger.error(f"Error occurred while stopping queue: {e}")
        try:
            self._teardown()
        except Exception as e:
            logger.error(f"Error occurred while disconnecting bot: {e}")

    def undo(self) -> UndoResult:
        # ensure connection and map are ready
        self.ensure_connected()
        lastSnapshot: Snapshot | None = self._undoservice.get_snapshot()

        if not lastSnapshot:
            raise IndexError("No Snapshots to return")
        else:
            coords = [Block(x=b.x, y=b.y, z=b.z, bid=b.bid) for b in lastSnapshot.blocks]
            with self._lock:
                self._add_to_queue(coords)            
                self._queue.start_all()
                self._updatelocalmap(coords)

        return UndoResult(
            build_id=lastSnapshot.guid, 
            blocks_restored=len(coords)
            )

    @property
    def map_size(self) -> MapResult:
        self.ensure_connected() # ensure map is loaded and ready
        return MapResult(
            width=self._bot.map.width, 
            height=self._bot.map.height, 
            length=self._bot.map.length
            )

    @property
    def palette(self) -> PaletteResult:        
        items = [BlockInfo(id=bid, name=name) for bid, name in sorted(self._palette.as_dict().items())]
        return PaletteResult(
            source=self._palette.source,
            count=len(self._palette),
            blocks=items
    )

    @property
    def shape_catalogue(self) -> ShapeCatalogueResult:
        catalogue = self._catalogue.as_dict()
        return ShapeCatalogueResult(
            source=self._catalogue.source,
            count=len(catalogue),
            catalogue=catalogue
            )

    def is_valid_block(self, bid: int | str) -> bool:
        return self._palette.is_valid(bid)