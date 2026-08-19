from threading import Lock
from buildservices.base import BuildService
from factories.client_factory import ClientFactory

from pyclassic import PyClassic
from pyclassic.queue import ThreadedQueue
from pyclassic.queue import Block
from pyclassic.map import ClassicMap

from shapebuilders.custom import BUILDERS
from validator import in_bounds
from config import SERVER_IP, SERVER_PORT

class ShapeBuilderService(BuildService):
    def __init__(self):       
        self._bot = PyClassic(ClientFactory.create_auth(), client_name="buildbot_classic_api")
        self._bot.connect(ip=SERVER_IP, port=SERVER_PORT)
        self._queue = ThreadedQueue(self._bot)
        self._pending = 0
        self._lock = Lock()       

    @property
    def pending(self):
        return self._pending

    def _enqueue(self, blocks) -> tuple[int, int]:
        kept = []#[Block(x,y,z,bid) for (x,y,z, bid = b) in blocks if in_bounds(b.x, b.y, b.z)]

        for b in blocks:
            x, y, z, bid = b
            if in_bounds(x,y,z):
                block: Block = Block(x,y,z,bid)
                kept.append(block)

        with self._lock:
            self._queue.add_queue(kept)
            self._pending += len(kept)
        return len(kept), len(blocks) - len(kept)

    def execute(self):
        #self._snapshot(self._queue.queues)
        with self._lock:            
            self._queue.start_all()
            self._pending = 0
        return self._pending
    
    def close(self):
        try:
            self._queue.stop()
        except Exception as e:
            print(f"Error occurred while stopping queue: {e}")
        try:
            self._bot.disconnect()
        except Exception as e:
            print(f"Error occurred while disconnecting bot: {e}")

    def _snapshot(self, blocks):
        # this needs to use lock to ensure it's threadsafe
        snapshot = []
       
        [snapshot.append(Block(b.x,b.y,b.z, self._get_block_type(self._bot.map, b))) for b in blocks]

        return snapshot

    def _get_block_type(self, map: ClassicMap, block: Block) -> int:
        block_type = map[block.x,block.y,block.z]
        assert isinstance(block_type,int)
        return(block_type)

    def add_shape(self, shape) -> tuple[int, int]:
        return self._enqueue(BUILDERS[shape.type](shape))

    def undo(self):
        pass