from dataclasses import dataclass
from enum import Enum

class ServerStatus(Enum):
    Running = "running"
    Stopped = "stopped"

@dataclass
class ServerBrief:
    server_id: int
    name: str
    status: ServerStatus

    cpus: int
    cpu_usage: int

    memory: int
    memory_used: int

    uptime: int