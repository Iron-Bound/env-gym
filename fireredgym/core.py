from pdb import set_trace as T
import os
import numpy as np

import mgba.audio
import mgba.core
import mgba.gba
import mgba.image
import mgba.log
import mgba.png
import mgba.vfs
from mgba import ffi, lib, libmgba_version_string

# input_map = {
#     "A": 0x1,
#     "B": 0x2,
#     # "Select": 0x4,
#     # "Start": 0x8,
#     "Right": 0x10,
#     "Left": 0x20,
#     "Up": 0x40,
#     "Down": 0x80,
#     # "R": 0x100,
#     # "L": 0x200,
# }


class NOOP:
    PRESS = 0x0


class A:
    PRESS = 0x1


class B:
    PRESS = 0x2


class SELECT:
    PRESS = 0x4


class START:
    PRESS = 0x8


class RIGHT:
    PRESS = 0x10


class LEFT:
    PRESS = 0x20


class UP:
    PRESS = 0x40


class DOWN:
    PRESS = 0x80


class R:
    PRESS = 0x100


class L:
    PRESS = 0x200


ACTIONS = (RIGHT, LEFT, UP, DOWN, A, B)


def make_env(rom_path, headless=True, quiet=True):
    if quiet:
        mgba.log.silence()

    game = mgba.core.load_path(rom_path)
    if not game:
        raise RuntimeError(f"Could not load ROM file {str(rom_path)}")

    screen = mgba.image.Image(*game.desired_video_dimensions())
    game.set_video_buffer(screen)

    return game, screen


def open_state_file(path):
    # Load state file and cache it
    if os.path.exists(path):
        with open(path, "rb") as state_file:
            state = state_file.read()
    else:
        raise ValueError("cannot open state file")
    return state


def load_state(game, state: bytes) -> None:
    """
    Loads a serialised emulator state (i.e. a save state in mGBA parlance)
    :param state: The raw save state data
    """
    vfile = mgba.vfs.VFile.fromEmpty()
    vfile.write(state, len(state))
    vfile.seek(0, whence=0)
    game.load_state(vfile)


# def run_action_on_emulator(
#     game, screen, action, headless=True, fast_video=True, frame_skip=24
# ):
#     """Sends actions to PyBoy"""
#     press, release = action.PRESS, action.RELEASE
#     ._core.setKeys(game, press)

#     if headless or fast_video:
#         pyboy._rendering(False)

#     frames = []
#     for i in range(frame_skip):
#         if i == 8:  # Release button after 8 frames
#             pyboy.send_input(release)
#         if not fast_video:  # Save every frame
#             frames.append(screen.screen_ndarray())
#         if i == frame_skip - 1:
#             pyboy._rendering(True)
#         pyboy.tick()

#     if fast_video:  # Save only the last frame
#         frames.append(screen.screen_ndarray())
