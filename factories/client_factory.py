from config import AUTH_PROVIDER, USERNAME
from authproviders.throwaway import ThrowawayAuthProvider
from pyclassic.client import SimpleAuth

class ClientFactory:
    @staticmethod    
    def create_auth() -> SimpleAuth:
        try:                        
            return {
                "simpleauth": SimpleAuth(USERNAME, USERNAME)
            }[AUTH_PROVIDER]
        except KeyError:
            raise ValueError(f"Unsupported AUTH_PROVIDER: {AUTH_PROVIDER}")
        except Exception as e:
            raise RuntimeError(f"Failed to create client: {e}")