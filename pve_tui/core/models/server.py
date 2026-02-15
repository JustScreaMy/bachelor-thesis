from dataclasses import dataclass
from enum import StrEnum

from pve_tui.core.models import ServerBrief


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
