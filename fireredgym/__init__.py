from fireredgym.emulator import Emulator
from fireredgym.environment import FireRed, FireRedV1

from gymnasium.envs.registration import register

__all__ = [
    "FireRed",
    "FireRedV1",
    "Emulator",
]

register(id="FireRed-V1", entry_point="emulator:FireRedV1")
