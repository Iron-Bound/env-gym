from pdb import set_trace as T

# import gymnasium as gym
from gymnasium import Env, spaces
import numpy as np

from fireredgym.core import (
    make_env,
    open_state_file,
    load_state,
    ACTIONS,
)


class FireRed:
    metadata = {"render_modes": ["rbg_array"]}

    def __init__(
        self,
        rom_path="pokemon_firered.gba",
        state_path=__file__.rstrip("environment.py") + "squirtle.state",
        headless=True,
        quiet=True,
    ):
        self.game, self.screen = make_env(rom_path, headless, quiet)

        self.memory = self.game.memory
        self.initial_state = open_state_file(state_path)
        self.headless = headless

        self.observation_space = spaces.Box(
            low=0, high=255, shape=(240, 160, 4), dtype=np.uint8
        )
        self.action_space = spaces.Discrete(len(ACTIONS))

        self._prev_pressed_inputs: int = 0
        self._pressed_inputs: int = 0
        self._held_inputs: int = 0

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        # super().reset(seed=seed)

        self.game.reset()
        load_state(self.game, self.initial_state)

        return self.observation_space, {}

    def render(self):
        return np.asarray(self.screen.to_pil(), dtype=np.uint8)

    def step(self, action):
        self.run_action_on_emulator(ACTIONS[action])
        return self.render(), 0, False, False, {}

    def close(self):
        pass

    def set_inputs(self, inputs: int):
        self.game._core.setKeys(self.game._core, inputs)

    def run_action_on_emulator(self, action, frame_skip=24):
        press = action.PRESS
        self.set_inputs(press)

        for i in range(frame_skip):
            if i == 8:
                self.set_inputs(0)
            self.game.run_frame()


class FireRedV1(FireRed):
    def __init__(
        self,
        rom_path="pokemon_firered.gba",
        state_path=__file__.rstrip("environment.py") + "squirtle.state",
        headless=True,
        quiet=True,
    ):
        super().__init__(rom_path, state_path, headless, quiet)
        self.counts_map = np.zeros((375, 500))

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0):
        """Resets the game. Seeding is NOT supported"""
        self.game.reset()
        load_state(self.game, self.initial_state)

        self.time = 0
        self.max_episode_steps = max_episode_steps
        self.reward_scale = reward_scale

        self.max_events = 0
        self.max_level_sum = 0
        self.max_opponent_level = 0

        self.seen_coords = set()
        self.seen_maps = set()

        self.death_count = 0
        self.total_healing = 0
        self.last_hp_fraction = 1.0
        self.last_party_size = 1
        self.last_reward = None

        return self.render(), {}

    def step(self, action):
        self.run_action_on_emulator(ACTIONS[action])
        self.time += 1
