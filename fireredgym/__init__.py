from .emulator import Emulator
from .environment import FireRed, FireRedV1

from gymnasium.envs.registration import register

__all__ = [
    "FireRed",
    "FireRedV1",
    "Emulator",
]

register(id="FireRed-V1", entry_point="emulator:FireRedV1")
