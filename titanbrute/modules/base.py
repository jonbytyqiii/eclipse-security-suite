from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModule(ABC):
    def __init__(self, target: str, port: int, timeout: float, config: Dict[str, Any]):
        self.target = target
        self.port = port
        self.timeout = timeout
        self.config = config or {}
    
    @abstractmethod
    async def authenticate(self, username: str, password: str) -> bool:
        pass