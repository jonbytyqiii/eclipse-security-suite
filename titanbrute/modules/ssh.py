import asyncio
import asyncssh
from modules.base import BaseModule

class SSHModule(BaseModule):
    """
    High-performance asynchronous SSH transport engine leveraging asyncssh.
    Engineered to handle transient connections and server socket degradation.
    """
    async def authenticate(self, username: str, password: str) -> str:
        # Sanitize common carriage returns or byte order marks (BOM) from files
        username = username.strip().replace('\ufeff', '')
        password = password.strip().replace('\ufeff', '')
        
        try:
            # Establish explicit parameters to bypass local authentication agent overhead
            async with asyncssh.connect(
                host=self.target,
                port=self.port,
                username=username,
                password=password,
                known_hosts=None,
                login_timeout=self.timeout,
                connect_timeout=self.timeout,
                preferred_auth=['password'],
                client_keys=[],
                agent_path=None,
                gss_auth=False,
            ) as conn:
                if conn is not None and not conn.is_closed():
                    return "SUCCESS"
                return "FAILURE"

        except asyncssh.PermissionDenied:
            return "FAILURE"
        except (asyncssh.Error, asyncio.TimeoutError, ConnectionRefusedError, OSError):
            # Trap network disconnects (MaxStartups drops) to trigger engine-level backoff
            return "THROTTLED"
        except Exception:
            return "ERROR"