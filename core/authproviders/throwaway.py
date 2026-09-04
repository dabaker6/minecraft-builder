
from core.authproviders.base import AuthProvider
from pyclassic.extra import throwaway
from pyclassic.client import Client

class ThrowawayAuthProvider(AuthProvider):
    def __init__(self, username, ip: str, port: int):
        self.username = username
        self.ip = ip
        self.port = port

    def create_client(self) -> Client:
        return throwaway(username=self.username, ip=self.ip, port=self.port)
    