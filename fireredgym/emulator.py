from pdb import set_trace as T
import os
import numpy as np

import mgba.core
import mgba.log
import mgba.vfs

from mgba.gba import GBA
from mgba import ffi, lib

ACTIONS = (GBA.KEY_DOWN, GBA.KEY_LEFT, GBA.KEY_RIGHT, GBA.KEY_UP, GBA.KEY_A, GBA.KEY_B)


class Emulator:
    @staticmethod
    def load(rom_path: str, quiet: bool = True) -> "Emulator":
        if quiet:
            mgba.log.silence()

        if not os.path.exists(rom_path):
            raise ValueError(f"File does not exist: {str(rom_path)}")

        game = mgba.core.load_path(rom_path)
        if game is None:
            raise ValueError(f"Could not load ROM file: {str(rom_path)}")
        game.reset()
        return Emulator(game)

    def __init__(self, core: mgba.core.Core):
        self.core = core
        self._mem_cache = {}

    def open_state_file(self, path) -> bytes:
        # Load state file and cache it
        if os.path.exists(path):
            with open(path, "rb") as state_file:
                state = state_file.read()
        else:
            raise ValueError("cannot open state file")
        return state

    def load_state(self, state: bytes) -> None:
        """
        Loads a serialised emulator state (i.e. a save state in mGBA parlance)
        :param state: The raw save state data
        """
        vfile = mgba.vfs.VFile.fromEmpty()
        vfile.write(state, len(state))
        vfile.seek(0, whence=0)
        self.core.load_state(vfile)

    def run_action_on_emulator(self, action, frame_skip=5):
        key = ACTIONS[action]
        self.core.set_keys(key)

        for i in range(frame_skip):
            self.core.run_frame()
            if i == 2:
                self.core.clear_keys(key)
        self._invalidate_mem_cache()

    def _invalidate_mem_cache(self):
        self._mem_cache = {}

    def _get_memory_region(self, region_id: int):
        if region_id not in self._mem_cache:
            mem_core = self.core.memory.u8._core
            size = ffi.new("size_t *")
            ptr = ffi.cast(
                "uint8_t *", mem_core.getMemoryBlock(mem_core, region_id, size)
            )
            self._mem_cache[region_id] = ffi.buffer(ptr, size[0])[:]
        return self._mem_cache[region_id]

    def read_memory(self, address: int, size: int = 1):
        region_id = address >> lib.BASE_OFFSET
        mem_region = self._get_memory_region(region_id)
        mask = len(mem_region) - 1
        address &= mask
        return mem_region[address : address + size]

    def read_s8(self, address: int):
        return int.from_bytes(
            self.read_memory(address, 1), byteorder="little", signed=True
        )

    def read_s16(self, address: int):
        return int.from_bytes(
            self.read_memory(address, 2), byteorder="little", signed=True
        )

    def read_s32(self, address: int):
        return int.from_bytes(
            self.read_memory(address, 4), byteorder="little", signed=True
        )

    def read_u8(self, address: int):
        return int.from_bytes(
            self.read_memory(address, 1), byteorder="little", signed=False
        )

    def read_u16(self, address: int):
        return int.from_bytes(
            self.read_memory(address, 2), byteorder="little", signed=False
        )

    def read_u32(self, address: int):
        return int.from_bytes(
            self.read_memory(address, 4), byteorder="little", signed=False
        )
