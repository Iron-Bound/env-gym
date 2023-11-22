# https://sourcegraph.com/github.com/pret/pokefirered/-/blob/include/constants/flags.h?L1320:57-1320:75
SAVE_BANK1_PTR = 0x03005D8C
SAVE_BANK2_PTR = 0x03005D90
EVENT_OBJECT_ADDR = 0x02036E38
SYS_FLAGS = 0x800

# Battle pokemon base address
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

PARTY_ADDR = [PARTY_1, PARTY_2, PARTY_3, PARTY_4, PARTY_5, PARTY_6]

# Offsets for party members
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
SEEN_POKE_ADDR = 0x08251FEE
X_POS_ADDR = 0x10
Y_POS_ADDR = 0x12
MAP_N_ADDR = 0x09

BADGE_ADDR = (0x4B0, 13)

TRAINER_FLAG_START_ADDR = 0x4FF
TRAINER_FLAG_END_ADDR = 0x7FF

EVENT_FLAGS_START_ADDR = 0xD747
EVENT_FLAGS_END_ADDR = 0xD761

MONEY = 0x0290
XOR_KEY = 0xF20
BADGE_1_ADDR = 0x20

# def bcd(num):
# return 10 * ((num >> 4) & 0x0F) + (num & 0x0F)


def bit_count(bits):
    return bin(bits).count("1")


# def read_bit(game, addr, bit) -> bool:
#     # add padding so zero will read '0b100000000' instead of '0b0'
#     return bin(256 + game.read_memory(addr))[-bit - 1] == "1"


def position(game):
    # save1_ptr = game.read_u32(SAVE_BANK1_PTRTR)
    x_pos = game.read_s16(EVENT_OBJECT_ADDR + X_POS_ADDR)
    y_pos = game.read_s16(EVENT_OBJECT_ADDR + Y_POS_ADDR)
    map_n = game.read_u8(EVENT_OBJECT_ADDR + MAP_N_ADDR)
    return x_pos, y_pos, map_n


def party(game):
    # party = [game.read_memory(addr) for addr in PARTY_ADDR]
    party_size = game.read_u8(PARTY_SIZE_ADDR)
    party_levels = [game.read_u8(addr) for addr in PARTY_LEVEL_ADDR]
    return party_size, party_levels


def opponent(game):
    return [game.read_u8(addr) for addr in OPPENENT_LEVEL_ADDR]


# def oak_parcel(game):
#     return read_bit(game, OAK_PARCEL_ADDR, 1)


# def pokedex_obtained(game):
#     return read_bit(game, OAK_POKEDEX_ADDR, 5)


def pokemon_seen(game):
    seen_bytes = game.read_memory(SEEN_POKE_ADDR, 336)
    return sum([bit_count(b) for b in seen_bytes])


def pokemon_caught(game):
    caught_bytes = [game.get_memory_value(addr) for addr in CAUGHT_POKE_ADDR]
    return sum([bit_count(b) for b in caught_bytes])


def hp_fraction(game):
    party_hp = [game.read_u16(addr) for addr in HP_ADDR]
    party_max_hp = [game.read_u16(addr) for addr in MAX_HP_ADDR]

    # Avoid division by zero if no pokemon
    sum_max_hp = sum(party_max_hp)
    if sum_max_hp == 0:
        return 1

    return sum(party_hp) / sum_max_hp


def xor_bytes(abytes, bbytes):
    return bytes([a ^ b for a, b in zip(abytes, bbytes)])


def money(game):
    save1_block_addr = game.read_u32(SAVE_BANK1_PTR)
    money = game.read_memory(save1_block_addr + MONEY, 4)
    xorKey = game.read_memory(save1_block_addr + XOR_KEY, 4)
    # if money is cone | xorKey is None:
    #     return 0
    result = xor_bytes(money, xorKey)
    return int.from_bytes(result, byteorder="little")


def badges(game):
    return 0
    # badges = game.read_memory(BADGE_1_ADDR, 1)
    # return bit_count(badges)


def events(game):
    return 0
    # """Adds up all event flags, exclude museum ticket"""
    # num_events = sum(
    #     bit_count(game.get_memory_value(i))
    #     for i in range(EVENT_FLAGS_START_ADDR, EVENT_FLAGS_END_ADDR)
    # )
    # museum_ticket = int(read_bit(game, MUSEUM_TICKET_ADDR, 0))

    # # Omit 13 events by default
    # return max(num_events - 13 - museum_ticket, 0)
