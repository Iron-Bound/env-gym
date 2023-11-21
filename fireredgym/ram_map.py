ENEMY_1 = 0x0202402C
ENEMY_2 = 0x02024090
ENEMY_3 = 0x020240F4
ENEMY_4 = 0x02024158
ENEMY_5 = 0x020241BC
ENEMY_6 = 0x02024220

PARTY_1 = 0x02024284
PARTY_2 = 0x020242E8
PARTY_3 = 0x0202434C
PARTY_4 = 0x020243B0
PARTY_5 = 0x02024414
PARTY_6 = 0x02024478


# Offsets for party member
STATUS_OFFSET = 80
LEVEL_OFFSET = 84
HP_OFFSET = 86
HP_TOTAL_OFFSET = 88
XP_OFFSET = 32 + 4


# Game Status
HP_ADDR = [
    (PARTY_1 + HP_OFFSET),
    (PARTY_2 + HP_OFFSET),
    (PARTY_3 + HP_OFFSET),
    (PARTY_4 + HP_OFFSET),
    (PARTY_5 + HP_OFFSET),
    (PARTY_6 + HP_OFFSET),
]
MAX_HP_ADDR = [
    (PARTY_1 + HP_TOTAL_OFFSET),
    (PARTY_2 + HP_TOTAL_OFFSET),
    (PARTY_3 + HP_TOTAL_OFFSET),
    (PARTY_4 + HP_TOTAL_OFFSET),
    (PARTY_5 + HP_TOTAL_OFFSET),
    (PARTY_6 + HP_TOTAL_OFFSET),
]
PARTY_SIZE_ADDR = 0x02024029
CAUGHT_POKE_ADDR = 0x0808A0E0
PARTY_LEVEL_ADDR = [
    (PARTY_6 + LEVEL_OFFSET),
    (PARTY_6 + LEVEL_OFFSET),
    (PARTY_6 + LEVEL_OFFSET),
    (PARTY_6 + LEVEL_OFFSET),
    (PARTY_6 + LEVEL_OFFSET),
    (PARTY_6 + LEVEL_OFFSET),
]
PARTY_XP_ADDR = [
    (PARTY_6 + XP_OFFSET),
    (PARTY_6 + XP_OFFSET),
    (PARTY_6 + XP_OFFSET),
    (PARTY_6 + XP_OFFSET),
    (PARTY_6 + XP_OFFSET),
    (PARTY_6 + XP_OFFSET),
]

OPPENENT_LEVEL_ADDR = [
    (ENEMY_1 + LEVEL_OFFSET),
    (ENEMY_2 + LEVEL_OFFSET),
    (ENEMY_3 + LEVEL_OFFSET),
    (ENEMY_4 + LEVEL_OFFSET),
    (ENEMY_5 + LEVEL_OFFSET),
    (ENEMY_6 + LEVEL_OFFSET),
]
ENEMY_COUNT_ADDR = 0x0803F5B4
SEEN_POKE_ADDR = 0x080CBDCC
Y_POS_ADDR = 0x03005068
X_POS_ADDR = 0x0300506C
MAP_N_ADDR = 0x03005010

BADGE_ADDR = (0x4B0, 13)

# addresses from https://datacrystal.romhacking.net/wiki/Pok%C3%A9mon_Red/Blue:RAM_map
# https://github.com/pret/pokered/blob/91dc3c9f9c8fd529bb6e8307b58b96efa0bec67e/constants/event_constants.asm
# HP_ADDR = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
# MAX_HP_ADDR = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]
# PARTY_SIZE_ADDR = 0xD163
# PARTY_ADDR = [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]
# PARTY_LEVEL_ADDR = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
# POKE_XP_ADDR = [0xD179, 0xD1A5, 0xD1D1, 0xD1FD, 0xD229, 0xD255]
# CAUGHT_POKE_ADDR = range(0xD2F7, 0xD309)
# SEEN_POKE_ADDR = range(0xD30A, 0xD31D)
# OPPONENT_LEVEL_ADDR = [0xD8C5, 0xD8F1, 0xD91D, 0xD949, 0xD975, 0xD9A1]
# X_POS_ADDR = 0xD362
# Y_POS_ADDR = 0xD361
# MAP_N_ADDR = 0xD35E
BADGE_1_ADDR = 0xD356
OAK_PARCEL_ADDR = 0xD74E
OAK_POKEDEX_ADDR = 0xD74B
OPPONENT_LEVEL = 0xCFF3
ENEMY_POKE_COUNT = 0xD89C
EVENT_FLAGS_START_ADDR = 0xD747
EVENT_FLAGS_END_ADDR = 0xD761
MUSEUM_TICKET_ADDR = 0xD754
MONEY_ADDR_1 = 0xD347
MONEY_ADDR_100 = 0xD348
MONEY_ADDR_10000 = 0xD349


def bcd(num):
    return 10 * ((num >> 4) & 0x0F) + (num & 0x0F)


def bit_count(bits):
    return bin(bits).count("1")


def read_bit(game, addr, bit) -> bool:
    # add padding so zero will read '0b100000000' instead of '0b0'
    return bin(256 + game.get_memory_value(addr))[-bit - 1] == "1"


def read_uint16(game, start_addr):
    """Read 2 bytes"""
    val_256 = game.get_memory_value(start_addr)
    val_1 = game.get_memory_value(start_addr + 1)
    return 256 * val_256 + val_1


def position(game):
    x_pos = game.get_memory_value(X_POS_ADDR)
    y_pos = game.get_memory_value(Y_POS_ADDR)
    map_n = game.get_memory_value(MAP_N_ADDR)
    return x_pos, y_pos, map_n


def party(game):
    party = [game.get_memory_value(addr) for addr in PARTY_ADDR]
    party_size = game.get_memory_value(PARTY_SIZE_ADDR)
    party_levels = [game.get_memory_value(addr) for addr in PARTY_LEVEL_ADDR]
    return party, party_size, party_levels


def opponent(game):
    return [game.get_memory_value(addr) for addr in OPPONENT_LEVEL_ADDR]


def oak_parcel(game):
    return read_bit(game, OAK_PARCEL_ADDR, 1)


def pokedex_obtained(game):
    return read_bit(game, OAK_POKEDEX_ADDR, 5)


def pokemon_seen(game):
    seen_bytes = [game.get_memory_value(addr) for addr in SEEN_POKE_ADDR]
    return sum([bit_count(b) for b in seen_bytes])


def pokemon_caught(game):
    caught_bytes = [game.get_memory_value(addr) for addr in CAUGHT_POKE_ADDR]
    return sum([bit_count(b) for b in caught_bytes])


def hp_fraction(game):
    party_hp = [read_uint16(game, addr) for addr in HP_ADDR]
    party_max_hp = [read_uint16(game, addr) for addr in MAX_HP_ADDR]

    # Avoid division by zero if no pokemon
    sum_max_hp = sum(party_max_hp)
    if sum_max_hp == 0:
        return 1

    return sum(party_hp) / sum_max_hp


def money(game):
    return (
        100 * 100 * bcd(game.get_memory_value(MONEY_ADDR_1))
        + 100 * bcd(game.get_memory_value(MONEY_ADDR_100))
        + bcd(game.get_memory_value(MONEY_ADDR_10000))
    )


def badges(game):
    badges = game.get_memory_value(BADGE_1_ADDR)
    return bit_count(badges)


def events(game):
    """Adds up all event flags, exclude museum ticket"""
    num_events = sum(
        bit_count(game.get_memory_value(i))
        for i in range(EVENT_FLAGS_START_ADDR, EVENT_FLAGS_END_ADDR)
    )
    museum_ticket = int(read_bit(game, MUSEUM_TICKET_ADDR, 0))

    # Omit 13 events by default
    return max(num_events - 13 - museum_ticket, 0)
