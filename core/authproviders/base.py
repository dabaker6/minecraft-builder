from typing import Protocol
from pyclassic.client import Client

class AuthProvider(Protocol):
    def create_client(self) -> Client:
        ...