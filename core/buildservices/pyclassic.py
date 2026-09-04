import asyncio
from threading import Lock
import threading
import time
from core.buildservices.base import BuildService

from core.palettes.palette import BlockPalette, InvalidBlockError
from core.undoservices.base import Snapshot, UndoService
import uuid

from pyclassic import PyClassic
from pyclassic.queue import ThreadedQueue, QueueError
from pyclassic.map import ClassicMap

from core.shapebuilders.schemas import Block, BlockInfo, BuildBusyError, MapResult, PaletteResult, UndoResult

from api.validator import in_bounds
from config import SERVER_IP, SERVER_PORT

class ShapeBuilderService(BuildService):
    def __init__(self, client: PyClassic, undoservice: UndoService, palette: BlockPalette):       
        # constructed palette
        self._palette = palette
        # constructed client
        self._bot = client
        # constructed undoservice
        self._undoservice = undoservice

        # create thread safe queue        
        self._queue = ThreadedQueue(self._bot)        
        self._lock = Lock() # lock
        
        # create threading event to signal when map is ready
        self._map_ready = threading.Event()
        # 
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
    
    def _register_map_ready_hook(self):
        # has to be wrapped in function to access self
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
            print(f"[LISTENER THREAD DIED] {e!r}")    

    def _wait_for_map(self, timeout=20):
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
        print(f"[MAP LOADED] {self._bot.map.width} x {self._bot.map.height} x {self._bot.map.length}")


    def build(self, blocks: list[Block], build_id: uuid.UUID) -> tuple[int, int]: 
        with self._lock:

            kept = [b for b in blocks if in_bounds(b.x, b.y, b.z)]

            invalid = [b.bid for b in kept if not self.is_valid_block(b.bid)]

            if  invalid:
                raise InvalidBlockError(f"unknow block IDs: {set(invalid)}")

            converted_blocks = []
            for b in kept:
                try:
                    bid: int = int(b.bid)
                    converted_blocks.append(Block(x=b.x, y=b.y, z=b.z, bid=bid))
                except ValueError:
                    print(f"Not a valid block Id {b}")

            #take snapshot of map for undo
            snapshot: Snapshot = self._take_snapshot(converted_blocks, build_id)

            try:
                self._queue.add_queue(converted_blocks)
            except QueueError as e:
                # internal log
                print(f"[BUILD REJECTED] queue busy: {e}")

                raise BuildBusyError("A build is already in progress; try again shortly")
            self._queue.start_all()            

            #update local map
            self._updatelocalmap(converted_blocks)
            self._undoservice.add_snapshot(snapshot)
            
        return len(kept), len(blocks) - len(converted_blocks)
    
    def close(self):
        try:
            self._queue.stop()
        except Exception as e:
            print(f"Error occurred while stopping queue: {e}")
        try:
            self._bot.disconnect()
        except Exception as e:
            print(f"Error occurred while disconnecting bot: {e}")

    def _updatelocalmap(self, blocks: list[Block]):        
        for b in blocks:
            try:
                bid: int = int()
                self._localmap[b.x, b.y, b.z] = bid
            except ValueError:
                print(f"Not a valid block Id {b}")                    

    def _take_snapshot(self, blocks: list[Block], build_id: uuid.UUID) -> Snapshot:
                    
        map_blocks = []
                
        [map_blocks.append(Block(x=b.x,y=b.y,z=b.z, bid=self._get_block_type(b))) for b in blocks]
        
        return Snapshot(
            guid=build_id,
            description="",
            blocks=map_blocks
            )        

    def _get_block_type(self, block: Block) -> str:
        block_type = str(self._localmap[block.x,block.y,block.z])
        return(block_type)

    def undo(self) -> UndoResult:
        lastSnapshot: Snapshot | None = self._undoservice.get_snapshot()

        if not lastSnapshot:
            raise IndexError("No Snapshots to return")
        else:
            coords = [Block(x=b.x, y=b.y, z=b.z, bid=b.bid) for b in lastSnapshot.blocks]
            with self._lock:
                try:    
                    self._queue.add_queue(coords)
                except QueueError as e:
                    # internal log
                    print(f"[BUILD REJECTED] queue busy: {e}")            

                self._updatelocalmap(coords)
                self._queue.start_all()

        return UndoResult(
            build_id=lastSnapshot.guid, 
            blocks_restored=len(coords)
            )

    @property
    def map_size(self) -> MapResult:
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

    def is_valid_block(self, bid: int | str) -> bool:
        return self._palette.is_valid(bid)