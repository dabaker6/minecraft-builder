from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()  # Load environment variables from .env file

SERVER_IP = os.getenv("SERVER_IP", "192.168.0.205")
SERVER_PORT = int(os.getenv("SERVER_PORT", 25566))
AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "throwaway")
SHAPE_BUILDER = os.getenv("SHAPE_BUILDER", "pyclassic")
USERNAME = os.getenv("USERNAME", "buildbot")
SNAPSHOT_STORE = os.getenv("SNAPSHOT_STORE", "in_memory")
BLOCK_PALETTE = os.getenv("BLOCK_PALETTE", "classic")
PALETTE_DIR = Path(os.getenv("PALETTE_DIR", Path(__file__).parent / "core/palettes"))
KEEP_ALIVE_INTERVAL = int(os.getenv("KEEP_ALIVE_INTERVAL", 600))  # in seconds