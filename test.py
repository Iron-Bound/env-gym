from pdb import set_trace as T
import gymnasium

from fireredgym import Emulator, FireRed, FireRedV1
import time


# TODO add video output
def play_game(rom_path, steps=10000):
    gba = Emulator.load(rom_path)
    game = FireRedV1(gba, headless=False)
    game.reset()

    # obs, reward, done, truncated, info = env.step(2)
    # print(obs.shape, reward, done, truncated, info)

    for _ in range(steps):
        game.render()
        game.gba.core.run_frame()
        obs, reward, done, truncated, info = game.step(game.action_space.sample())
        print(info)


def performance_test(rom_path, env: FireRed, steps=10000):
    gba = Emulator.load(rom_path)
    game = FireRed(gba, headless=True)
    game.reset()

    for _ in range(1000):
        game.step(0)  # game.action_space.sample())

    start = time.time()
    for _ in range(steps):
        game.step(0)  # game.action_space.sample())

    game.close()
    end = time.time()
    print("Steps per second: {}".format(steps / (end - start)))


if __name__ == "__main__":
    play_game("pokemon_firered.gba")
    # performance_test("pokemon_firered.gba", 100)
