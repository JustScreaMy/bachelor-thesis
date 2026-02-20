from dataclasses import dataclass
from enum import StrEnum


class ServerStatus(StrEnum):
    """
    Enum representing the status of a server.

    Attributes:
        Running (str): Indicates the server is currently running.
        Stopped (str): Indicates the server is currently stopped.
    """

    Running = 'running'
    Stopped = 'stopped'


class ServerType(StrEnum):
    """
    Enum representing the type of a server.

    Attributes:
        VM (str): Virtual Machine (QEMU).
        LXC (str): Linux Container.
    """

    VM = 'vm'
    LXC = 'lxc'


@dataclass
class ServerBrief:
    """
    Data class representing a brief overview of a server.

    Attributes:
        server_id (int): Unique identifier for the server - represents VMID in Proxmox.
        name (str): Name of the server.
        node (str): Name of the node where the server is located.
        type (ServerType): Type of the server (VM or LXC).
        status (ServerStatus): Current status of the server.
        cpus (int): Number of CPUs allocated to the server.
        cpu_usage (int): Current CPU usage percentage.
        memory (int): Total memory allocated to the server in Bytes.
        memory_used (int): Current memory usage in Bytes.
        uptime (int): Uptime of the server in seconds.
    """

    server_id: int
    name: str
    node: str
    type: ServerType
    status: ServerStatus

    cpus: int
    cpu_usage: float

    memory: int
    memory_used: int

    uptime: int


class ServerArch(StrEnum):
    """
    Enum representing the architecture of a server.

    Attributes:
        AMD64 (str): AMD64 architecture (x86-64).
        ARM64 (str): ARM64 architecture (aarch64).
        I386 (str): i386 architecture (x86).
        ARMHF (str): ARMHF architecture (armhf).
        RISCV32 (str): RISC-V 32-bit architecture.
        RISCV64 (str): RISC-V 64-bit architecture.
        UNKNOWN (str): Unknown architecture.
    """

    AMD64 = 'amd64'
    ARM64 = 'arm64'
    I386 = 'i386'
    ARMHF = 'armhf'
    RISCV32 = 'riscv32'
    RISCV64 = 'riscv64'
    UNKNOWN = 'unknown'


@dataclass
class ServerBase:
    brief: ServerBrief

    arch: ServerArch

    cpu_limit: int
    cpu_units: int

    on_boot: bool


@dataclass
class ServerQEMU(ServerBase):
    cpu_type: str

    baloon: int


@dataclass
class ServerLXC(ServerBase):
    disk: int
    max_disk: int
