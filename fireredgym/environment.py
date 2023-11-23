from pdb import set_trace as T
from typing import Literal
import sys

import gymnasium as gym
import numpy as np
import mgba.core
import mgba.image

from fireredgym.emulator import Emulator, ACTIONS
from fireredgym import ram_map

try:
    import pygame
    from pygame import gfxdraw
except ImportError as e:
    pass


def _pil_image_to_pygame(img):
    return pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert()


class FireRed(gym.Env):
    metadata = {
        "render_modes": ["human", "rbg_array"],
        "render_fps": 60,
    }

    def __init__(
        self,
        core: Emulator,
        state_path=__file__.rstrip("environment.py") + "squirtle.state",
        obs_type: Literal["rgb", "grayscale"] = "rgb",
        render_mode="rgb_array",
        headless=True,
    ):
        self.gba = core

        # screen_size = self.gba.core.desired_video_dimensions()
        # if obs_type == "rgb":
        #     screen_size += (3,)

        screen_size = (120, 80, 3)
        self.observation_space = gym.spaces.Box(
            low=0, high=255, shape=screen_size, dtype=np.uint8
        )
        
        self._framebuffer = mgba.image.Image(*self.gba.core.desired_video_dimensions())
        self.gba.core.set_video_buffer(self._framebuffer)

        self.action_space = gym.spaces.Discrete(len(ACTIONS))
        self.initial_state = self.gba.open_state_file(state_path)

        self.obs_type = obs_type
        self.headless = headless
        self.render_mode = render_mode
        self.frameskip = 0
        self._screen = None
        self._clock = None

        # self._kwargs = kwargs
        self.reset()

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        # super().reset(seed=seed)
        
        self.gba.core.reset()
        self.gba.load_state(self.initial_state)
        self.gba.core.run_frame()
        ob = self._get_observation()[::2,::2]
        return ob, {}

    def _get_observation(self):
        img = self._framebuffer.to_pil().convert("RGB")
        # if self.obs_type == "grayscale":
        #     img = img.convert("L")
        return np.array(img).transpose(1, 0, 2)

    def render(self):
        if self.render_mode is None:
            gym.logger.warn(
                "You are calling render method without specifying any render mode. "
                "You can specify the render_mode at initialization."
            )
            return

        img = self._framebuffer.to_pil().convert("RGB")
        if self.obs_type == "grayscale":
            img = img.convert("L")

        if self.headless == False:
            if "pygame" not in sys.modules:
                raise RuntimeError(
                    "pygame is not installed, run `pip install pygame`"
                ) from e

            if self._screen is None:
                pygame.init()
                pygame.display.init()
                self._screen = pygame.display.set_mode((240, 160))
            if self._clock is None:
                self._clock = pygame.time.Clock()

            surf = _pil_image_to_pygame(img)
            self._screen.fill((0, 0, 0))
            self._screen.blit(surf, (0, 0))

            effective_fps = self.metadata["render_fps"]
            if self.frameskip:
                if isinstance(self.frameskip, tuple):
                    # average FPS is close enough
                    effective_fps /= (self.frameskip[0] + self.frameskip[1]) / 2 + 1
                else:
                    effective_fps /= self.frameskip + 1

            pygame.event.pump()
            self._clock.tick(effective_fps)
            pygame.display.flip()
        else:  # self.render_mode == "rgb_array"
            return np.array(img)

    def step(self, action):
        self.gba.run_action_on_emulator(action, self.frameskip)
        ob = self._get_observation()[::2,::2]        
        return ob, 0, False, False, {}

    def close(self):
        pass


class FireRedV1(FireRed):
    def __init__(
        self,
        core: Emulator,
        state_path=__file__.rstrip("environment.py") + "squirtle.state",
        obs_type: Literal["rgb", "grayscale"] = "rgb",
        render_mode=None,
        headless=True,
    ):
        super().__init__(core, state_path, obs_type, render_mode, headless)
        self.counts_map = np.zeros((375, 500))

    def reset(self, seed=None, options=None, max_episode_steps=20480, reward_scale=4.0):
        """Resets the game. Seeding is NOT supported"""
        self.gba.core.reset()
        self.gba.load_state(self.initial_state)
        info = {}

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

        ob = self._get_observation()[::2,::2]
        return ob, info

    def step(self, action):
        self.gba.run_action_on_emulator(action)
        self.time += 1

        # Exploration reward
        r, c, map_n = ram_map.position(self.gba)
        self.seen_coords.add((r, c, map_n))
        self.seen_maps.add(map_n)
        exploration_reward = 0.01 * len(self.seen_coords)
        # glob_x, glob_y = game_map.local_to_global(r, c, map_n)
        # try:
        #     self.counts_map[glob_y, glob_x] += 1
        # except:
        #     pass

        # Level reward
        party_size, party_levels = ram_map.party(self.gba)
        self.max_level_sum = max(self.max_level_sum, sum(party_levels))
        if self.max_level_sum < 30:
            level_reward = 4 * self.max_level_sum
        else:
            level_reward = 30 + (self.max_level_sum - 30) / 4

        # Healing and death rewards
        hp_fraction = ram_map.hp_fraction(self.gba)
        fraction_increased = hp_fraction > self.last_hp_fraction
        party_size_constant = party_size == self.last_party_size
        if fraction_increased and party_size_constant:
            if self.last_hp_fraction > 0:
                self.total_healing += hp_fraction - self.last_hp_fraction
            else:
                self.death_count += 1
        healing_reward = self.total_healing
        death_reward = 0.05 * self.death_count

        # Opponent level reward
        max_opponent_level = max(ram_map.opponent(self.gba))
        self.max_opponent_level = max(self.max_opponent_level, max_opponent_level)
        opponent_level_reward = 0.2 * self.max_opponent_level

        # Badge reward
        badges = ram_map.badges(self.gba)
        badges_reward = 5 * badges

        # Event reward
        events = ram_map.events(self.gba)
        self.max_events = max(self.max_events, events)
        event_reward = self.max_events

        money = 0 # ram_map.money(self.gba)

        reward = self.reward_scale * (
            event_reward
            + level_reward
            + opponent_level_reward
            + death_reward
            + badges_reward
            + healing_reward
            + exploration_reward
        )

        # Subtract previous reward
        # TODO: Don't record large cumulative rewards in the first place
        if self.last_reward is None:
            reward = 0
            self.last_reward = 0
        else:
            nxt_reward = reward
            reward -= self.last_reward
            self.last_reward = nxt_reward

        ob = self._get_observation()[::2,::2]
        info = {exploration_reward}
        done = self.time >= self.max_episode_steps
        if done:
            info = {
                "reward": {
                    "delta": reward,
                    "event": event_reward,
                    "level": level_reward,
                    "opponent_level": opponent_level_reward,
                    "death": death_reward,
                    "badges": badges_reward,
                    "healing": healing_reward,
                    "exploration": exploration_reward,
                },
                        'maps_explored': len(self.seen_maps),
                        'party_size': party_size,
                        'highest_pokemon_level': max(party_levels),
                        'total_party_level': sum(party_levels),
                        'deaths': self.death_count,
                #         'badge_1': float(badges == 1),
                #         'badge_2': float(badges > 1),
                #         'event': events,
                #         'money': money,
                        'exploration_map': self.counts_map,
            }

        return ob, reward, done, done, info
