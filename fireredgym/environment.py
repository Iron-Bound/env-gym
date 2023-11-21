from pdb import set_trace as T
from typing import Literal

import gymnasium as gym
import numpy as np
import mgba.core
import mgba.image

from .emulator import Emulator, ACTIONS


class FireRed(gym.Env):
    metadata = {"render_modes": ["rbg_array"]}

    def __init__(
        self,
        core: Emulator,
        state_path=__file__.rstrip("environment.py") + "squirtle.state",
        obs_type: Literal["rgb", "grayscale"] = "rgb",
        headless=True,
        **kwargs,
    ):
        self.gba = core

        screen_size = self.gba.core.desired_video_dimensions()
        # if obs_type == "rgb":
        #     screen_size += (3,)
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=screen_size, dtype=np.uint8
        )

        self._framebuffer = mgba.image.Image(*self.gba.core.desired_video_dimensions())
        self.gba.core.set_video_buffer(self._framebuffer)

        self.action_space = gym.spaces.Discrete(len(ACTIONS))
        self.initial_state = self.gba.open_state_file(state_path)

        self.headless = headless
        self._kwargs = kwargs
        self.reset()

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        # super().reset(seed=seed)
        self.gba.core.reset()
        self.gba.load_state(self.initial_state)
        return self.observation_space, {}

    def _get_observatio(self):
        return np.array(
            self._framebuffer.to_pil().convert("RGB"), dtype=np.uint8, copy=False
        )

    def render(self):
        return self._get_observatio()
        # return np.array(self.screen.to_pil(), dtype=np.uint8, copy=False)

    def step(self, action):
        self.gba.run_action_on_emulator(ACTIONS[action])
        return self.render(), 0, False, False, {}

    def close(self):
        pass


class FireRedV1(FireRed):
    def __init__(
        self,
        core: Emulator,
        state_path=__file__.rstrip("environment.py") + "squirtle.state",
        obs_type: Literal["rgb", "grayscale"] = "rgb",
        headless=True,
        **kwargs,
    ):
        super().__init__(core, state_path, obs_type, headless, kwargs)
        self.counts_map = np.zeros((375, 500))

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0):
        """Resets the game. Seeding is NOT supported"""
        self.gba.reset()
        load_state(self.gba, self.initial_state)

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

        # # Exploration reward
        # x, y, map_n = ram_map.position(self.gba)
        # self.seen_coords.add((x, y, map_n))
        # self.seen_maps.add(map_n)
        # exploration_reward = 0.01 * len(self.seen_coords)
        # glob_x, glob_y = game_map.local_to_global(x, y, map_n)
        # try:
        #     self.counts_map[glob_y, glob_x] += 1
        # except:
        #     pass

        # # Badge reward
        # badges = ram_map.badges(self.gba)
        # badges_reward = 5 * badges

        # # Event reward
        # events = ram_map.events(self.gba)
        # self.max_events = max(self.max_events, events)
        # event_reward = self.max_events

        info = {}
        done = self.time >= self.max_episode_steps
        # if done:
        #     info = {
        #         'reward': {
        #             'delta': reward,
        #             'event': event_reward,
        #             'level': level_reward,
        #             'opponent_level': opponent_level_reward,
        #             'death': death_reward,
        #             'badges': badges_reward,
        #             'healing': healing_reward,
        #             'exploration': exploration_reward,
        #         },
        #         'maps_explored': len(self.seen_maps),
        #         'party_size': party_size,
        #         'highest_pokemon_level': max(party_levels),
        #         'total_party_level': sum(party_levels),
        #         'deaths': self.death_count,
        #         'badge_1': float(badges == 1),
        #         'badge_2': float(badges > 1),
        #         'event': events,
        #         'money': money,
        #         'exploration_map': self.counts_map,
        #     }

        return self.render(), reward, done, done, info
