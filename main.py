import json
import math
import os
import random
import sys
from dataclasses import dataclass, field

import pygame


WIDTH = 1280
HEIGHT = 720
FPS = 60
TILE = 32
WORLD_W = 260
WORLD_H = 110
MINIMAP_W = 220
MINIMAP_H = 92
WORLD_SEED = random.randint(0, 9999999)
GRAVITY = 2200
MOVE_ACCEL = 2800
MAX_SPEED = 360
JUMP_SPEED = 760
TERMINAL_VEL = 1800
REACH = 7 * TILE
SAVE_FILE = "savegame.json"
DAY_LENGTH = 220.0
ASSET_DIR = "generated_assets"
AUDIO_ENABLED = False


AIR = 0
DIRT = 1
STONE = 2
GRASS = 3
WOOD = 4
LEAF = 5
COAL_ORE = 6
IRON_ORE = 7
GOLD_ORE = 8
SAND = 9
TORCH = 10
WORKBENCH = 11
CHEST = 12
SLIME_KING = 13
ZOMBIE = 14
BAT = 15
EYE = 16
WATER = 17
LAVA = 18
FIBER = 19
BANDAGE = 200
LANTERN = 201
ARMOR = 202
BOMB = 203
HEAL_POTION = 204

BLOCK_COLORS = {
    AIR: (0, 0, 0),
    DIRT: (126, 87, 56),
    STONE: (110, 110, 122),
    GRASS: (75, 160, 74),
    WOOD: (133, 96, 60),
    LEAF: (58, 149, 72),
    COAL_ORE: (72, 72, 82),
    IRON_ORE: (140, 111, 90),
    GOLD_ORE: (185, 160, 70),
    SAND: (214, 198, 126),
    TORCH: (245, 190, 60),
    WORKBENCH: (151, 104, 62),
    CHEST: (124, 76, 43),
    SLIME_KING: (96, 215, 120),
    ZOMBIE: (116, 170, 90),
    BAT: (85, 85, 105),
    EYE: (200, 80, 200),
    WATER: (60, 120, 220),
    LAVA: (240, 90, 40),
    FIBER: (120, 185, 90),
}

BLOCK_NAME = {
    DIRT: "Dirt",
    STONE: "Stone",
    GRASS: "Grass",
    WOOD: "Wood",
    LEAF: "Leaves",
    COAL_ORE: "Coal Ore",
    IRON_ORE: "Iron Ore",
    GOLD_ORE: "Gold Ore",
    SAND: "Sand",
    TORCH: "Torch",
    WORKBENCH: "Workbench",
    CHEST: "Chest",
    SLIME_KING: "Slime King",
    ZOMBIE: "Zombie",
    BAT: "Bat",
    EYE: "Eye",
    WATER: "Water",
    LAVA: "Lava",
    FIBER: "Fiber",
}

SOLID = {DIRT, STONE, GRASS, WOOD, LEAF, COAL_ORE, IRON_ORE, GOLD_ORE, SAND, WORKBENCH, CHEST}
LIQUIDS = {WATER, LAVA}
PLACEABLE = {DIRT, STONE, GRASS, WOOD, LEAF, TORCH, WORKBENCH, CHEST, SAND}
MINABLE = {DIRT, STONE, GRASS, WOOD, LEAF, COAL_ORE, IRON_ORE, GOLD_ORE, SAND, WORKBENCH, CHEST}
USEABLE = {BANDAGE, LANTERN, ARMOR, BOMB, HEAL_POTION}

ITEM_NAME = {
    DIRT: "Dirt",
    STONE: "Stone",
    WOOD: "Wood",
    LEAF: "Leaves",
    COAL_ORE: "Coal",
    IRON_ORE: "Iron",
    GOLD_ORE: "Gold",
    SAND: "Sand",
    TORCH: "Torch",
    WORKBENCH: "Workbench",
    CHEST: "Chest",
    100: "Stick",
    101: "Wood Sword",
    102: "Wood Pickaxe",
    103: "Stone Pickaxe",
    104: "Iron Pickaxe",
    FIBER: "Fiber",
    BANDAGE: "Bandage",
    LANTERN: "Lantern",
    ARMOR: "Armor",
    BOMB: "Bomb",
    HEAL_POTION: "Heal Potion",
    SLIME_KING: "Slime King",
    ZOMBIE: "Zombie",
    BAT: "Bat",
    EYE: "Eye",
}

TOOL_POWER = {
    100: 1,
    101: 2,
    102: 2,
    103: 3,
    104: 4,
}

INVENTORY_CAPACITY = 24
HOTBAR_SIZE = 7
INVENTORY_COLUMNS = 8
INVENTORY_ROWS = 3
HELP_LINES = [
    "Move: A/D or arrows",
    "Jump: Space",
    "Mine: LMB",
    "Attack: RMB",
    "Place: MMB",
    "Craft: Tab",
    "Chest: T",
    "Inventory: I",
    "Use item: U",
    "Help: H",
    "Save/Load: F5 / F9",
]

RECIPES = [
    {"name": "Stick", "result": 100, "amount": 4, "requires": {WOOD: 1}, "station": None},
    {"name": "Torch", "result": TORCH, "amount": 8, "requires": {WOOD: 1, COAL_ORE: 1}, "station": None},
    {"name": "Workbench", "result": WORKBENCH, "amount": 1, "requires": {WOOD: 8}, "station": None},
    {"name": "Wood Sword", "result": 101, "amount": 1, "requires": {WOOD: 7, 100: 2}, "station": WORKBENCH},
    {"name": "Wood Pickaxe", "result": 102, "amount": 1, "requires": {WOOD: 10, 100: 3}, "station": WORKBENCH},
    {"name": "Stone Pickaxe", "result": 103, "amount": 1, "requires": {STONE: 12, 100: 3}, "station": WORKBENCH},
    {"name": "Iron Pickaxe", "result": 104, "amount": 1, "requires": {IRON_ORE: 10, 100: 4}, "station": WORKBENCH},
    {"name": "Fiber", "result": FIBER, "amount": 4, "requires": {LEAF: 4}, "station": None},
    {"name": "Bandage", "result": BANDAGE, "amount": 2, "requires": {FIBER: 2, 100: 1}, "station": None},
    {"name": "Lantern", "result": LANTERN, "amount": 1, "requires": {TORCH: 4, IRON_ORE: 2}, "station": WORKBENCH},
    {"name": "Armor", "result": ARMOR, "amount": 1, "requires": {IRON_ORE: 6, LEAF: 4}, "station": WORKBENCH},
    {"name": "Bomb", "result": BOMB, "amount": 2, "requires": {STONE: 3, COAL_ORE: 2}, "station": WORKBENCH},
    {"name": "Heal Potion", "result": HEAL_POTION, "amount": 1, "requires": {FIBER: 2, GOLD_ORE: 1, TORCH: 1}, "station": None},
]


def recipe_name(recipe):
    return f"{recipe['name']} x{recipe['amount']}"


@dataclass
class Player:
    x: float
    y: float
    w: int = 24
    h: int = 44
    vx: float = 0
    vy: float = 0
    on_ground: bool = False
    facing: int = 1
    health: float = 100
    mana: int = 0
    selected: int = DIRT
    inventory: dict = field(default_factory=dict)
    equipped: int = 102
    attack_timer: float = 0
    attack_cooldown: float = 0
    chest_open: str = ""
    inventory_open: bool = True

    def __post_init__(self):
        if not self.inventory:
            self.inventory = {
                DIRT: 18,
                STONE: 0,
                WOOD: 12,
                LEAF: 0,
                COAL_ORE: 0,
                IRON_ORE: 0,
                GOLD_ORE: 0,
                SAND: 0,
                TORCH: 6,
                WORKBENCH: 1,
                CHEST: 0,
                100: 6,
                101: 1,
                102: 1,
                103: 0,
                104: 0,
            }

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


@dataclass
class Enemy:
    x: float
    y: float
    kind: str = "slime"
    vx: float = 0
    vy: float = 0
    w: int = 28
    h: int = 20
    dir: int = 1
    timer: float = 0
    health: int = 20
    hurt_timer: float = 0
    boss: bool = False
    phase: int = 0
    spawn_timer: float = 0
    shoot_timer: float = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


@dataclass
class Drop:
    x: float
    y: float
    item: int
    amount: int = 1
    vx: float = 0
    vy: float = 0
    w: int = 16
    h: int = 16
    life: float = 30.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)


def new_world():
    rnd = random.Random(WORLD_SEED)
    world = [[AIR for _ in range(WORLD_H)] for _ in range(WORLD_W)]
    surface = []
    h = WORLD_H // 2 + 8
    for x in range(WORLD_W):
        h += rnd.choice([-2, -1, 0, 0, 1, 1, 2]) if x else 0
        h = max(18, min(WORLD_H - 16, h))
        surface.append(h)
        biome = "forest" if x < WORLD_W * 0.4 else "desert" if x < WORLD_W * 0.7 else "mountain"
        for y in range(h, WORLD_H):
            if y == h:
                world[x][y] = SAND if biome == "desert" else GRASS
            elif y < h + 4:
                world[x][y] = SAND if biome == "desert" else DIRT
            else:
                world[x][y] = STONE

    for x in range(2, WORLD_W - 2):
        if rnd.random() < 0.06:
            depth = rnd.randint(1, 5)
            for y in range(surface[x] + depth, WORLD_H):
                if y < WORLD_H - 18 or rnd.random() > 0.5:
                    world[x][y] = AIR

    for _ in range(22):
        cx = rnd.randint(10, WORLD_W - 11)
        cy = rnd.randint(28, WORLD_H - 18)
        radius = rnd.randint(4, 10)
        carve_cave(world, cx, cy, radius, rnd.randint(24, 48))

    for _ in range(260):
        x = rnd.randint(4, WORLD_W - 5)
        y = rnd.randint(25, WORLD_H - 6)
        if world[x][y] == STONE:
            roll = rnd.random()
            if roll < 0.07:
                world[x][y] = COAL_ORE
            elif roll < 0.10:
                world[x][y] = IRON_ORE
            elif roll < 0.105:
                world[x][y] = GOLD_ORE

    for _ in range(8):
        x = rnd.randint(8, WORLD_W - 8)
        y = rnd.randint(26, WORLD_H - 10)
        for dx in range(-3, 4):
            for dy in range(-2, 3):
                tx, ty = x + dx, y + dy
                if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H and world[tx][ty] == STONE:
                    world[tx][ty] = WATER if rnd.random() < 0.7 else LAVA

    for _ in range(10):
        x = rnd.randint(8, WORLD_W - 9)
        y = surface[x]
        if world[x][y] in (GRASS, SAND) and rnd.random() < 0.35:
            world[x][y - 1] = CHEST

    for _ in range(22):
        x = rnd.randint(8, WORLD_W - 9)
        if 0 < surface[x] < WORLD_H - 8 and rnd.random() < 0.5:
            top = surface[x]
            trunk_h = rnd.randint(4, 7)
            for i in range(1, trunk_h + 1):
                if top - i >= 0:
                    world[x][top - i] = WOOD
            crown_y = top - trunk_h - 2
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    ax = x + dx
                    ay = crown_y + dy
                    if 0 <= ax < WORLD_W and 0 <= ay < WORLD_H and abs(dx) + abs(dy) < 4:
                        if world[ax][ay] == AIR:
                            world[ax][ay] = LEAF

    for _ in range(5):
        x = rnd.randint(6, WORLD_W - 7)
        y = surface[x]
        if rnd.random() < 0.4 and y + 1 < WORLD_H:
            world[x][y + 1] = SAND
            for dy in range(2, 6):
                if y + dy < WORLD_H and world[x][y + dy] == DIRT:
                    world[x][y + dy] = SAND

    return world, surface


def carve_cave(world, cx, cy, radius, steps):
    x, y = cx, cy
    for _ in range(steps):
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    tx = x + dx
                    ty = y + dy
                    if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
                        if ty > 18:
                            world[tx][ty] = AIR
        x += random.choice([-1, 0, 0, 1])
        y += random.choice([-1, 0, 0, 1])
        x = max(2, min(WORLD_W - 3, x))
        y = max(20, min(WORLD_H - 3, y))
        radius = max(3, min(10, radius + random.choice([-1, 0, 0, 1, 1])))


def spawn_enemies(world, surface):
    enemies = []
    for _ in range(16):
        x = random.randint(8, WORLD_W - 9)
        y = surface[x]
        kind = "slime" if x < WORLD_W * 0.4 else "zombie" if x < WORLD_W * 0.7 else "bat"
        if kind == "slime":
            enemies.append(Enemy(x * TILE, (y - 1) * TILE, kind="slime"))
        elif kind == "zombie":
            enemies.append(Enemy(x * TILE, (y - 1) * TILE, kind="zombie", w=26, h=42, health=38))
        else:
            enemies.append(Enemy(x * TILE, max(6, (y - 8)) * TILE, kind="bat", w=24, h=16, health=14))
    for _ in range(6):
        x = random.randint(10, WORLD_W - 11)
        y = surface[x]
        enemies.append(Enemy(x * TILE, (y - 1) * TILE, kind="zombie", w=26, h=42, health=38))
    for _ in range(5):
        x = random.randint(15, WORLD_W - 16)
        y = random.randint(WORLD_H // 2, WORLD_H - 8)
        if get_block(world, x, y) == AIR:
            enemies.append(Enemy(x * TILE, y * TILE, kind="bat", w=24, h=16, health=14))
    enemies.append(Enemy((WORLD_W - 30) * TILE, 18 * TILE, kind="eye", w=30, h=30, health=60))
    enemies.append(Enemy((WORLD_W // 2) * TILE, 12 * TILE, kind="slime_king", w=60, h=40, health=240, boss=True))
    return enemies


def get_block(world, tx, ty):
    if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
        return world[tx][ty]
    return STONE


def set_block(world, tx, ty, value):
    if 0 <= tx < WORLD_W and 0 <= ty < WORLD_H:
        world[tx][ty] = value


def rect_collides_world(world, rect):
    left = rect.left // TILE
    right = rect.right // TILE
    top = rect.top // TILE
    bottom = rect.bottom // TILE
    for tx in range(left, right + 1):
        for ty in range(top, bottom + 1):
            if get_block(world, tx, ty) in SOLID:
                if rect.colliderect(pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)):
                    return True
    return False


def move_entity(world, x, y, w, h, vx, vy, dt):
    rect = pygame.Rect(int(x), int(y), w, h)
    rect.x += int(vx * dt)
    for tx in range(rect.left // TILE, rect.right // TILE + 1):
        for ty in range(rect.top // TILE, rect.bottom // TILE + 1):
            if get_block(world, tx, ty) in SOLID:
                block = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
                if rect.colliderect(block):
                    if vx > 0:
                        rect.right = block.left
                    elif vx < 0:
                        rect.left = block.right
                    vx = 0
    rect.y += int(vy * dt)
    on_ground = False
    for tx in range(rect.left // TILE, rect.right // TILE + 1):
        for ty in range(rect.top // TILE, rect.bottom // TILE + 1):
            if get_block(world, tx, ty) in SOLID:
                block = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
                if rect.colliderect(block):
                    if vy > 0:
                        rect.bottom = block.top
                        on_ground = True
                    elif vy < 0:
                        rect.top = block.bottom
                    vy = 0
    return rect.x, rect.y, vx, vy, on_ground


def world_to_screen(camera_x, camera_y, x, y):
    return int(x - camera_x), int(y - camera_y)


def draw_text(surface, font, text, x, y, color=(255, 255, 255)):
    surface.blit(font.render(text, True, color), (x, y))


def make_texture(size, base, accent=None, seed=0, border=True):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill(base)
    rnd = random.Random(seed)
    for _ in range(max(4, size // 3)):
        px = rnd.randrange(size)
        py = rnd.randrange(size)
        radius = rnd.randint(1, max(1, size // 7))
        color = accent if accent and rnd.random() > 0.35 else tuple(max(0, min(255, c + rnd.randint(-18, 18))) for c in base)
        pygame.draw.circle(surf, color, (px, py), radius)
    for _ in range(max(2, size // 5)):
        x = rnd.randrange(size)
        pygame.draw.line(surf, tuple(max(0, min(255, c - 25)) for c in base), (x, 0), (x + rnd.randint(-1, 1), size), 1)
    if border:
        pygame.draw.rect(surf, (0, 0, 0, 90), (0, 0, size, size), 1)
    return surf


def make_liquid_texture(size, base, accent=None, seed=0):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rnd = random.Random(seed)
    for y in range(size):
        blend = y / max(1, size - 1)
        c = tuple(int(base[i] * (1 - blend * 0.15) + (accent[i] if accent else base[i]) * (blend * 0.15)) for i in range(3))
        pygame.draw.line(surf, c, (0, y), (size, y))
    for _ in range(max(3, size // 4)):
        px = rnd.randrange(size)
        py = rnd.randrange(size)
        radius = rnd.randint(1, 2)
        pygame.draw.circle(surf, accent or (255, 255, 255), (px, py), radius)
    pygame.draw.rect(surf, (255, 255, 255, 25), (0, 0, size, size), 1)
    return surf


def make_block_textures():
    return {
        DIRT: make_texture(TILE, (126, 87, 56), (150, 105, 66), 11),
        STONE: make_texture(TILE, (110, 110, 122), (140, 140, 150), 12),
        GRASS: make_texture(TILE, (75, 160, 74), (95, 190, 85), 13),
        WOOD: make_texture(TILE, (133, 96, 60), (160, 115, 70), 14),
        LEAF: make_texture(TILE, (58, 149, 72), (90, 180, 95), 15),
        COAL_ORE: make_texture(TILE, (72, 72, 82), (32, 32, 34), 16),
        IRON_ORE: make_texture(TILE, (140, 111, 90), (190, 150, 120), 17),
        GOLD_ORE: make_texture(TILE, (185, 160, 70), (235, 210, 120), 18),
        SAND: make_texture(TILE, (214, 198, 126), (230, 220, 155), 19),
        TORCH: make_texture(TILE, (245, 190, 60), (255, 230, 120), 20),
        WORKBENCH: make_texture(TILE, (151, 104, 62), (180, 124, 72), 21),
        CHEST: make_texture(TILE, (124, 76, 43), (160, 100, 56), 22),
    }


def make_item_textures():
    textures = {}

    fiber = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    for i in range(7):
        pygame.draw.arc(fiber, (120, 190, 95), (3 + i, 6, 22, 18), 0.5, 3.8, 2)
    pygame.draw.circle(fiber, (185, 230, 150), (16, 11), 3)
    textures[FIBER] = fiber

    stick = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.line(stick, (155, 110, 70), (6, 22), (24, 8), 4)
    pygame.draw.line(stick, (120, 82, 46), (7, 23), (25, 9), 2)
    textures[100] = stick

    sword = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.polygon(sword, (225, 225, 235), [(8, 5), (22, 11), (8, 17), (5, 15), (6, 10)])
    pygame.draw.rect(sword, (160, 115, 70), (5, 11, 5, 6), border_radius=2)
    pygame.draw.rect(sword, (105, 70, 40), (9, 8, 4, 10), border_radius=2)
    textures[101] = sword

    pickaxe_wood = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.line(pickaxe_wood, (140, 95, 55), (10, 24), (18, 6), 4)
    pygame.draw.line(pickaxe_wood, (210, 210, 220), (9, 8), (21, 14), 4)
    pygame.draw.line(pickaxe_wood, (170, 170, 180), (10, 8), (22, 14), 2)
    textures[102] = pickaxe_wood

    pickaxe_stone = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.line(pickaxe_stone, (145, 100, 60), (10, 24), (18, 6), 4)
    pygame.draw.line(pickaxe_stone, (160, 170, 180), (9, 8), (21, 14), 5)
    pygame.draw.line(pickaxe_stone, (100, 105, 115), (9, 8), (21, 14), 2)
    textures[103] = pickaxe_stone

    pickaxe_iron = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.line(pickaxe_iron, (150, 103, 60), (10, 24), (18, 6), 4)
    pygame.draw.line(pickaxe_iron, (205, 215, 225), (9, 8), (21, 14), 5)
    pygame.draw.line(pickaxe_iron, (130, 140, 150), (9, 8), (21, 14), 2)
    textures[104] = pickaxe_iron

    bandage = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.rect(bandage, (230, 220, 205), (7, 12, 18, 8), border_radius=3)
    pygame.draw.rect(bandage, (200, 185, 170), (10, 5, 8, 22), border_radius=3)
    pygame.draw.line(bandage, (170, 155, 145), (7, 16), (24, 16), 2)
    textures[BANDAGE] = bandage

    lantern = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.rect(lantern, (120, 85, 45), (13, 4, 4, 6), border_radius=2)
    pygame.draw.rect(lantern, (155, 110, 55), (10, 9, 10, 13), border_radius=4)
    pygame.draw.circle(lantern, (255, 214, 95), (15, 16), 6)
    pygame.draw.circle(lantern, (255, 245, 190), (15, 16), 3)
    pygame.draw.rect(lantern, (95, 70, 40), (8, 20, 14, 4), border_radius=2)
    textures[LANTERN] = lantern

    armor = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.polygon(armor, (110, 125, 145), [(16, 4), (23, 9), (20, 24), (8, 24), (5, 9)])
    pygame.draw.polygon(armor, (175, 190, 210), [(16, 6), (21, 10), (19, 21), (13, 21), (10, 10)])
    pygame.draw.line(armor, (85, 95, 110), (12, 8), (12, 23), 2)
    pygame.draw.line(armor, (85, 95, 110), (20, 8), (20, 23), 2)
    textures[ARMOR] = armor

    bomb = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.circle(bomb, (60, 60, 66), (15, 16), 8)
    pygame.draw.circle(bomb, (95, 95, 104), (12, 13), 3)
    pygame.draw.line(bomb, (120, 95, 50), (18, 8), (22, 4), 3)
    pygame.draw.line(bomb, (255, 220, 90), (22, 4), (25, 2), 2)
    textures[BOMB] = bomb

    potion = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.rect(potion, (225, 225, 235), (11, 5, 8, 4), border_radius=2)
    pygame.draw.polygon(potion, (180, 70, 90), [(12, 8), (20, 8), (22, 22), (10, 22)])
    pygame.draw.circle(potion, (240, 120, 150), (16, 16), 6)
    pygame.draw.circle(potion, (255, 200, 210), (13, 13), 2)
    textures[HEAL_POTION] = potion

    return textures


def item_surface(item, block_textures, item_textures):
    return item_textures.get(item) or block_textures.get(item)


def ensure_asset_dir():
    if not os.path.exists(ASSET_DIR):
        os.makedirs(ASSET_DIR, exist_ok=True)


def save_texture_sheet(name, textures):
    ensure_asset_dir()
    sheet = pygame.Surface((TILE * len(textures), TILE), pygame.SRCALPHA)
    for idx, tex in enumerate(textures):
        sheet.blit(tex, (idx * TILE, 0))
    pygame.image.save(sheet, os.path.join(ASSET_DIR, f"{name}.png"))


def make_player_sprite():
    surf = pygame.Surface((24, 44), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 216, 170), (4, 0, 16, 12), border_radius=4)
    pygame.draw.rect(surf, (230, 190, 135), (2, 10, 20, 10), border_radius=5)
    pygame.draw.rect(surf, (56, 92, 204), (2, 16, 20, 24), border_radius=5)
    pygame.draw.rect(surf, (40, 60, 150), (2, 30, 20, 6), border_radius=3)
    pygame.draw.rect(surf, (160, 105, 72), (0, 18, 4, 18), border_radius=2)
    pygame.draw.rect(surf, (160, 105, 72), (20, 18, 4, 18), border_radius=2)
    pygame.draw.rect(surf, (110, 72, 42), (6, 40, 6, 4), border_radius=2)
    pygame.draw.rect(surf, (110, 72, 42), (12, 40, 6, 4), border_radius=2)
    return surf


def make_sword_sprite():
    surf = pygame.Surface((36, 12), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (220, 220, 230), [(6, 1), (28, 4), (6, 7), (2, 6), (4, 3)])
    pygame.draw.rect(surf, (170, 120, 70), (0, 4, 8, 4), border_radius=2)
    pygame.draw.rect(surf, (110, 70, 40), (5, 2, 5, 8), border_radius=2)
    return surf


def make_parallax_layers():
    far = pygame.Surface((WIDTH * 2, HEIGHT // 2), pygame.SRCALPHA)
    mid = pygame.Surface((WIDTH * 2, HEIGHT // 2), pygame.SRCALPHA)
    for x in range(0, far.get_width(), 120):
        h = random.randint(20, 70)
        pygame.draw.polygon(far, (55, 90, 140), [(x, far.get_height()), (x + 40, far.get_height() - h), (x + 90, far.get_height())])
    for x in range(0, mid.get_width(), 80):
        h = random.randint(35, 120)
        pygame.draw.polygon(mid, (80, 120, 80), [(x, mid.get_height()), (x + 30, mid.get_height() - h), (x + 65, mid.get_height())])
    return far, mid


def make_sound(freq=440, duration=0.12, volume=0.35, wave="sine"):
    try:
        import numpy as np
    except Exception:
        return None
    sample_rate = 44100
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples, False)
    if wave == "square":
        audio = np.sign(np.sin(freq * t * 2 * np.pi))
    elif wave == "triangle":
        audio = 2 * np.arcsin(np.sin(freq * t * 2 * np.pi)) / np.pi
    else:
        audio = np.sin(freq * t * 2 * np.pi)
    envelope = np.linspace(1.0, 0.0, samples)
    audio = (audio * envelope * volume * 32767).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)


def make_audio():
    sounds = {
        "mine": make_sound(220, 0.05, 0.2),
        "place": make_sound(330, 0.05, 0.18),
        "swing": make_sound(520, 0.06, 0.16),
        "hit": make_sound(140, 0.08, 0.25, "square"),
        "craft": make_sound(660, 0.12, 0.2),
        "pickup": make_sound(880, 0.05, 0.12),
        "boss": make_sound(90, 0.18, 0.25, "square"),
        "music_forest": make_sound(220, 1.2, 0.035, "triangle"),
        "music_desert": make_sound(176, 1.2, 0.03, "sine"),
        "music_cave": make_sound(110, 1.4, 0.04, "square"),
        "music_boss": make_sound(88, 1.4, 0.05, "square"),
    }
    return sounds


def make_enemy_sprite(kind, boss=False):
    if kind == "slime" or kind == "slime_king":
        surf = pygame.Surface((60 if boss else 28, 40 if boss else 20), pygame.SRCALPHA)
        w, h = surf.get_size()
        body = (92, 214, 126) if boss else (118, 224, 118)
        shade = tuple(max(0, c - 42) for c in body)
        highlight = tuple(min(255, c + 34) for c in body)
        eye = (26, 30, 28)
        pygame.draw.ellipse(surf, (0, 0, 0, 35), (3, h - 5, w - 6, 6))
        pygame.draw.ellipse(surf, body, (0, 2, w, h - 2))
        pygame.draw.ellipse(surf, shade, (2, 6, w - 4, h - 6))
        pygame.draw.ellipse(surf, highlight, (4, 2, w - 10, h // 2))
        pygame.draw.arc(surf, shade, (2, 2, w - 4, h - 4), math.pi * 0.08, math.pi * 0.92, 2)
        pygame.draw.arc(surf, (255, 255, 255, 90), (5, 4, w - 16, h // 2), math.pi * 1.1, math.pi * 1.9, 2)
        if boss:
            crown = [(w // 2 - 16, 7), (w // 2 - 10, 0), (w // 2 - 4, 8), (w // 2 + 4, 0), (w // 2 + 10, 8), (w // 2 + 16, 1), (w // 2 + 22, 7)]
            pygame.draw.polygon(surf, (255, 228, 100), crown)
            pygame.draw.polygon(surf, (180, 120, 30), [(p[0], p[1] + 2) for p in crown], 2)
            pygame.draw.circle(surf, (255, 255, 255), (w // 2 - 5, h // 4), 5)
            pygame.draw.circle(surf, eye, (w // 2 - 5, h // 4), 2)
            pygame.draw.circle(surf, (255, 255, 255), (w // 2 + 6, h // 4 + 1), 4)
            pygame.draw.circle(surf, eye, (w // 2 + 6, h // 4 + 1), 2)
        else:
            pygame.draw.circle(surf, eye, (w // 3, h // 2), 2)
            pygame.draw.circle(surf, eye, (w * 2 // 3, h // 2), 2)
            pygame.draw.arc(surf, eye, (w // 4, h // 2 - 1, w // 2, 8), math.pi, math.pi * 2, 2)
            pygame.draw.line(surf, shade, (4, h - 4), (w // 2, h - 1), 2)
        if boss:
            pygame.draw.circle(surf, (255, 245, 130), (w // 2, h // 3), 5)
            pygame.draw.circle(surf, (255, 180, 60), (w // 2 + 7, h // 3 + 4), 3)
        return surf
    if kind == "zombie":
        surf = pygame.Surface((28, 44), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 35), (3, 34, 22, 6))
        pygame.draw.rect(surf, (122, 168, 96), (5, 1, 18, 11), border_radius=4)
        pygame.draw.rect(surf, (100, 142, 80), (3, 10, 22, 16), border_radius=4)
        pygame.draw.rect(surf, (84, 108, 64), (1, 22, 26, 12), border_radius=4)
        pygame.draw.rect(surf, (58, 78, 48), (0, 31, 28, 12), border_radius=4)
        pygame.draw.circle(surf, (235, 220, 160), (10, 7), 2)
        pygame.draw.circle(surf, (235, 220, 160), (18, 7), 2)
        pygame.draw.circle(surf, (15, 15, 15), (11, 8), 1)
        pygame.draw.circle(surf, (15, 15, 15), (18, 8), 1)
        pygame.draw.line(surf, (68, 55, 34), (7, 14), (21, 14), 2)
        pygame.draw.line(surf, (75, 95, 55), (4, 28), (7, 42), 3)
        pygame.draw.line(surf, (75, 95, 55), (19, 28), (23, 42), 3)
        pygame.draw.line(surf, (130, 95, 70), (0, 20), (6, 23), 2)
        return surf
    if kind == "bat":
        surf = pygame.Surface((30, 20), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (0, 0, 0, 25), [(2, 16), (9, 12), (15, 17), (21, 12), (28, 16), (15, 19)])
        pygame.draw.polygon(surf, (100, 100, 130), [(0, 9), (9, 4), (12, 10), (9, 15)])
        pygame.draw.polygon(surf, (74, 74, 96), [(30, 9), (21, 4), (18, 10), (21, 15)])
        pygame.draw.ellipse(surf, (62, 62, 84), (10, 5, 10, 9))
        pygame.draw.circle(surf, (255, 255, 255), (13, 9), 1)
        pygame.draw.circle(surf, (255, 255, 255), (17, 9), 1)
        pygame.draw.line(surf, (35, 35, 45), (14, 14), (12, 18), 1)
        pygame.draw.line(surf, (35, 35, 45), (16, 14), (18, 18), 1)
        return surf
    if kind == "eye":
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 0, 0, 40), (17, 19), 14)
        pygame.draw.circle(surf, (165, 70, 190), (16, 16), 14)
        pygame.draw.circle(surf, (215, 120, 235), (12, 12), 10)
        pygame.draw.circle(surf, (255, 255, 255), (16, 16), 8)
        pygame.draw.circle(surf, (35, 30, 35), (16, 16), 4)
        pygame.draw.circle(surf, (255, 255, 255), (13, 13), 1)
        pygame.draw.arc(surf, (120, 40, 130), (4, 4, 24, 24), 0, math.tau, 2)
        pygame.draw.line(surf, (210, 130, 230), (7, 23), (11, 27), 2)
        pygame.draw.line(surf, (210, 130, 230), (25, 23), (21, 27), 2)
        return surf
    return pygame.Surface((16, 16), pygame.SRCALPHA)


def tint_sprite(sprite, color, alpha=96):
    tinted = sprite.copy()
    overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


def save_game(world, player, enemies, drops, surface):
    data = {
        "player": {
            "x": player.x,
            "y": player.y,
            "vx": player.vx,
            "vy": player.vy,
            "health": player.health,
            "selected": player.selected,
            "equipped": player.equipped,
            "chest_open": player.chest_open,
            "inventory": {str(k): v for k, v in player.inventory.items()},
        },
        "world": world,
        "surface": surface,
        "world_seed": WORLD_SEED,
        "time_of_day": time_of_day if "time_of_day" in globals() else 0.0,
        "enemies": [
            {
                "x": e.x,
                "y": e.y,
                "kind": e.kind,
                "vx": e.vx,
                "vy": e.vy,
                "health": e.health,
                "dir": e.dir,
                "timer": e.timer,
                "boss": e.boss,
            }
            for e in enemies
        ],
        "drops": [
            {"x": d.x, "y": d.y, "item": d.item, "amount": d.amount, "vx": d.vx, "vy": d.vy, "life": d.life}
            for d in drops
        ],
        "chests": chest_storage if "chest_storage" in globals() else {},
        "title_screen": False,
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    world = data["world"]
    surface = data.get("surface")
    if "world_seed" in data:
        globals()["WORLD_SEED"] = data["world_seed"]
    p = data["player"]
    inventory = {int(k): v for k, v in p["inventory"].items()}
    player = Player(p["x"], p["y"], vx=p["vx"], vy=p["vy"], health=p["health"], selected=p["selected"], equipped=p.get("equipped", 102), inventory=inventory)
    player.chest_open = p.get("chest_open", "")
    enemies = [
        Enemy(e["x"], e["y"], kind=e.get("kind", "slime"), vx=e.get("vx", 0), vy=e.get("vy", 0), health=e.get("health", 20), dir=e.get("dir", 1), timer=e.get("timer", 0), boss=e.get("boss", False))
        for e in data.get("enemies", [])
    ]
    drops = [
        Drop(d["x"], d["y"], d["item"], d.get("amount", 1), d.get("vx", 0), d.get("vy", 0), life=d.get("life", 30.0))
        for d in data.get("drops", [])
    ]
    return world, surface, player, enemies, drops, data.get("time_of_day", 0.0), data.get("chests", {}), data.get("world_seed", WORLD_SEED)


def count_inventory(player, item):
    return player.inventory.get(item, 0)


def has_station(world, player, station_item):
    if station_item is None:
        return True
    area = pygame.Rect(player.rect.x - REACH, player.rect.y - REACH, player.w + REACH * 2, player.h + REACH * 2)
    left = max(0, area.left // TILE)
    right = min(WORLD_W - 1, area.right // TILE)
    top = max(0, area.top // TILE)
    bottom = min(WORLD_H - 1, area.bottom // TILE)
    for tx in range(left, right + 1):
        for ty in range(top, bottom + 1):
            if get_block(world, tx, ty) == station_item:
                return True
    return False


def item_mining_power(player):
    return TOOL_POWER.get(player.equipped, 1)


def armor_reduction(player):
    return 0.10 if player.inventory.get(ARMOR, 0) > 0 else 0.0


def give_item(player, item, amount):
    player.inventory[item] = player.inventory.get(item, 0) + amount


def use_inventory_item(player, item):
    if player.inventory.get(item, 0) <= 0:
        return False
    if item == BANDAGE:
        player.health = min(100, player.health + 18)
        player.inventory[item] -= 1
        return True
    if item == HEAL_POTION:
        player.health = min(100, player.health + 35)
        player.inventory[item] -= 1
        return True
    if item == BOMB:
        player.inventory[item] -= 1
        return True
    if item == LANTERN:
        player.equipped = LANTERN
        return True
    return False


def compact_inventory(inv):
    return {k: v for k, v in inv.items() if v > 0}


def inventory_items(inv):
    return [item for item, amount in inv.items() if amount > 0]


def inventory_slot_rect(index, x, y, slot_size=44, gap=6, columns=INVENTORY_COLUMNS):
    col = index % columns
    row = index // columns
    return pygame.Rect(x + col * (slot_size + gap), y + row * (slot_size + gap), slot_size, slot_size)


def inventory_slot_at(pos, x, y, count, slot_size=44, gap=6, columns=INVENTORY_COLUMNS):
    for idx in range(count):
        if inventory_slot_rect(idx, x, y, slot_size, gap, columns).collidepoint(pos):
            return idx
    return None


def swap_slot_amounts(inv_a, item_a, inv_b, item_b, amount=None):
    if item_a is None or item_b is None:
        return
    if amount is None:
        amount = inv_a.get(item_a, 0)
    move = min(amount, inv_a.get(item_a, 0))
    if move <= 0:
        return
    inv_a[item_a] -= move
    inv_b[item_b] = inv_b.get(item_b, 0) + move


def move_stack(src, dst, item, amount=None):
    if item is None:
        return 0
    if amount is None:
        amount = src.get(item, 0)
    move = min(amount, src.get(item, 0))
    if move <= 0:
        return 0
    src[item] -= move
    dst[item] = dst.get(item, 0) + move
    return move


def play_sound(sounds, key):
    if not AUDIO_ENABLED:
        return
    sound = sounds.get(key)
    if sound:
        try:
            sound.play()
        except Exception:
            pass


def play_music_track(sounds, key, loops=-1):
    if not AUDIO_ENABLED:
        return
    sound = sounds.get(key)
    if sound:
        try:
            pygame.mixer.fadeout(500)
            sound.play(loops=loops, fade_ms=500)
        except Exception:
            pass


def slot_item(inv, index):
    items = inventory_items(inv)
    if 0 <= index < len(items):
        return items[index]
    return None


def chest_panel_rect():
    return pygame.Rect(120, 100, 1040, 470)


def inventory_panel_rect():
    return pygame.Rect(18, HEIGHT - 170, 360, 152)


def world_biome_for_x(x):
    ratio = x / max(1, WORLD_W * TILE)
    if ratio < 0.4:
        return "forest"
    if ratio < 0.7:
        return "desert"
    return "mountain"


def cave_depth_for_y(y):
    return y / max(1, WORLD_H * TILE)


def select_music_track(sounds, biome, in_cave=False, boss=False):
    if boss:
        return "music_boss"
    if in_cave:
        return "music_cave"
    return "music_forest" if biome == "forest" else "music_desert" if biome == "desert" else "music_cave"


def try_craft(player, world, recipe):
    if not has_station(world, player, recipe["station"]):
        return False
    for item, amount in recipe["requires"].items():
        if count_inventory(player, item) < amount:
            return False
    for item, amount in recipe["requires"].items():
        player.inventory[item] -= amount
    give_item(player, recipe["result"], recipe["amount"])
    return True


def auto_stack_inventory(inv, max_slots=INVENTORY_CAPACITY):
    stacked = {}
    for item, amount in inv.items():
        if amount > 0:
            stacked[item] = stacked.get(item, 0) + amount
    limited = {}
    for item in list(stacked.keys())[:max_slots]:
        limited[item] = stacked[item]
    return limited


def chest_key(tx, ty):
    return f"{tx},{ty}"


def nearby_chest(world, player):
    area = pygame.Rect(player.rect.x - REACH, player.rect.y - REACH, player.w + REACH * 2, player.h + REACH * 2)
    left = max(0, area.left // TILE)
    right = min(WORLD_W - 1, area.right // TILE)
    top = max(0, area.top // TILE)
    bottom = min(WORLD_H - 1, area.bottom // TILE)
    for tx in range(left, right + 1):
        for ty in range(top, bottom + 1):
            if get_block(world, tx, ty) == CHEST:
                return tx, ty
    return None


def transfer_inventory(src, dst, item, amount=None):
    if amount is None:
        amount = src.get(item, 0)
    move = min(amount, src.get(item, 0))
    if move <= 0:
        return 0
    src[item] = src.get(item, 0) - move
    dst[item] = dst.get(item, 0) + move
    return move


def chest_inventory(chest_storage, tx, ty):
    key = chest_key(tx, ty)
    if key not in chest_storage:
        chest_storage[key] = {}
    return chest_storage[key]


def main():
    pygame.init()
    pygame.display.set_caption("TerraForge")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    big = pygame.font.SysFont("consolas", 30, bold=True)
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    except Exception:
        pass
    sounds = make_audio()
    block_textures = make_block_textures()
    item_textures = make_item_textures()
    player_sprite = make_player_sprite()
    sword_sprite = make_sword_sprite()
    far_parallax, mid_parallax = make_parallax_layers()
    save_texture_sheet("blocks", list(block_textures.values()))
    save_texture_sheet("items", list(item_textures.values()))
    save_texture_sheet("sprites", [player_sprite, sword_sprite])
    slime_sprite = make_enemy_sprite("slime", False)
    slime_king_sprite = make_enemy_sprite("slime_king", True)
    enemy_sprites = {
        ("slime", False): slime_sprite,
        ("slime_king", True): slime_king_sprite,
        ("zombie", False): make_enemy_sprite("zombie", False),
        ("bat", False): make_enemy_sprite("bat", False),
        ("eye", False): make_enemy_sprite("eye", False),
        ("slime_forest", False): tint_sprite(slime_sprite, (40, 30, 20), 35),
        ("slime_desert", False): tint_sprite(slime_sprite, (235, 200, 110), 35),
        ("zombie_desert", False): tint_sprite(make_enemy_sprite("zombie", False), (220, 180, 80), 45),
        ("bat_cave", False): tint_sprite(make_enemy_sprite("bat", False), (130, 110, 170), 35),
    }

    loaded = load_game()
    if loaded:
        world, surface, player, enemies, drops, time_of_day, chest_storage, loaded_seed = loaded
        globals()["WORLD_SEED"] = loaded_seed
    else:
        world, surface = new_world()
        player = Player(12 * TILE, 10 * TILE)
        enemies = spawn_enemies(world, surface)
        drops = []
        chest_storage = {}
        time_of_day = 0.0

    camera_x = 0.0
    camera_y = 0.0
    bg = (130, 190, 255)
    selected_order = [DIRT, STONE, WOOD, TORCH, WORKBENCH, CHEST, SAND]
    running = True
    action_cooldown = 0.0
    attack_flash = 0.0
    craft_panel_open = False
    craft_scroll = 0
    chest_panel_open = False
    chest_target = None
    chest_pickup_all = False
    help_open = False
    drag_source = None
    drag_item = None
    drag_from = None
    inventory_open = True
    hotbar_locked = False
    boss_spawned = any(e.boss for e in enemies)
    title_screen = True
    current_music = None
    current_biome = None

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 1 / 30)
        time_of_day = (time_of_day + dt / DAY_LENGTH) % 1.0
        action_cooldown = max(0.0, action_cooldown - dt)
        player.attack_timer = max(0.0, player.attack_timer - dt)
        player.attack_cooldown = max(0.0, player.attack_cooldown - dt)
        attack_flash = max(0.0, attack_flash - dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if title_screen:
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    title_screen = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    title_screen = False
                continue
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F5:
                    save_game(world, player, enemies, drops, surface)
                elif event.key == pygame.K_F9:
                    loaded = load_game()
                    if loaded:
                        world, surface, player, enemies, drops, time_of_day, chest_storage = loaded
                elif event.key == pygame.K_r:
                    world, surface = new_world()
                    player = Player(12 * TILE, 10 * TILE)
                    enemies = spawn_enemies(world, surface)
                    drops = []
                    chest_storage = {}
                    time_of_day = 0.0
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7):
                    idx = event.key - pygame.K_1
                    if idx < len(selected_order):
                        player.selected = selected_order[idx]
                elif event.key == pygame.K_e:
                    if player.equipped == 101:
                        player.equipped = 102
                    elif player.equipped == 102:
                        player.equipped = 103 if count_inventory(player, 103) > 0 else 102
                    elif player.equipped == 103 and count_inventory(player, 104) > 0:
                        player.equipped = 104
                    else:
                        player.equipped = 101 if count_inventory(player, 101) > 0 else player.equipped
                elif event.key == pygame.K_c:
                    craft_panel_open = not craft_panel_open
                elif event.key == pygame.K_t:
                    chest_panel_open = not chest_panel_open
                elif event.key == pygame.K_TAB:
                    craft_panel_open = not craft_panel_open
                    chest_panel_open = False
                elif event.key == pygame.K_h:
                    help_open = not help_open
                elif event.key == pygame.K_i:
                    inventory_open = not inventory_open
                elif event.key == pygame.K_u:
                    use_inventory_item(player, player.selected)
            elif event.type == pygame.MOUSEWHEEL and craft_panel_open:
                craft_scroll = max(0, min(max(0, len(RECIPES) - 6), craft_scroll - event.y))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if craft_panel_open:
                        panel_x = WIDTH - 360
                        panel_y = 120
                        if pygame.Rect(panel_x, panel_y, 320, 420).collidepoint(event.pos):
                            idx = (event.pos[1] - (panel_y + 72)) // 48 + craft_scroll
                            if 0 <= idx < len(RECIPES):
                                recipe = RECIPES[idx]
                                if try_craft(player, world, recipe):
                                    action_cooldown = 0.1
                    elif inventory_open:
                        inv_panel = inventory_panel_rect()
                        if inv_panel.collidepoint(event.pos):
                            idx = inventory_slot_at(event.pos, inv_panel.x + 12, inv_panel.y + 40, INVENTORY_CAPACITY, slot_size=28, gap=3, columns=INVENTORY_COLUMNS)
                            if idx is not None:
                                drag_item = slot_item(player.inventory, idx)
                                drag_from = "player" if drag_item is not None else None
                    elif chest_panel_open and chest_target:
                        tx, ty = chest_target
                        chest = chest_inventory(chest_storage, tx, ty)
                        chest_panel = chest_panel_rect()
                        if chest_panel.collidepoint(event.pos):
                            idx = inventory_slot_at(event.pos, chest_panel.x + 24, chest_panel.y + 78, INVENTORY_CAPACITY, columns=INVENTORY_COLUMNS)
                            if idx is not None:
                                chest_items = inventory_items(chest)
                                if idx < len(chest_items):
                                    drag_item = chest_items[idx]
                                    drag_from = "chest"
                elif event.button == 3 and chest_panel_open and chest_target:
                    tx, ty = chest_target
                    chest = chest_inventory(chest_storage, tx, ty)
                    panel = chest_panel_rect()
                    if panel.collidepoint(event.pos):
                        left_grid = pygame.Rect(panel.x + 24, panel.y + 78, 360, 290)
                        right_grid = pygame.Rect(panel.x + 560, panel.y + 78, 360, 290)
                        if left_grid.collidepoint(event.pos):
                            idx = inventory_slot_at(event.pos, left_grid.x, left_grid.y, INVENTORY_CAPACITY, columns=INVENTORY_COLUMNS)
                            chest_items = inventory_items(chest)
                            if idx is not None and idx < len(chest_items):
                                item = chest_items[idx]
                                transfer_inventory(chest, player.inventory, item, chest[item])
                        elif right_grid.collidepoint(event.pos):
                            idx = inventory_slot_at(event.pos, right_grid.x, right_grid.y, INVENTORY_CAPACITY, columns=INVENTORY_COLUMNS)
                            inv_items = inventory_items(player.inventory)
                            if idx is not None and idx < len(inv_items):
                                item = inv_items[idx]
                                transfer_inventory(player.inventory, chest, item, player.inventory[item])
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if drag_item is not None and drag_from is not None:
                    mx, my = event.pos
                    if chest_panel_open and chest_target:
                        tx, ty = chest_target
                        chest = chest_inventory(chest_storage, tx, ty)
                        panel = chest_panel_rect()
                        chest_rect = pygame.Rect(panel.x + 24, panel.y + 78, 360, 290)
                        inv_rect = pygame.Rect(panel.x + 560, panel.y + 78, 360, 290)
                        if drag_from == "player" and chest_rect.collidepoint(mx, my):
                            move_stack(player.inventory, chest, drag_item, player.inventory.get(drag_item, 0))
                        elif drag_from == "chest" and inv_rect.collidepoint(mx, my):
                            move_stack(chest, player.inventory, drag_item, chest.get(drag_item, 0))
                    drag_item = None
                    drag_from = None

        keys = pygame.key.get_pressed()
        if title_screen:
            screen.fill((18, 22, 38))
            for y in range(HEIGHT):
                t = y / HEIGHT
                c = (18 + int(30 * t), 22 + int(45 * t), 38 + int(75 * t))
                pygame.draw.line(screen, c, (0, y), (WIDTH, y))
            draw_text(screen, big, "TerraForge", WIDTH // 2 - 70, HEIGHT // 2 - 80, (245, 230, 200))
            draw_text(screen, font, "Press Enter or click to start", WIDTH // 2 - 95, HEIGHT // 2 - 30, (230, 230, 230))
            draw_text(screen, font, "Mining, crafting, combat, bosses, caves, and liquids", WIDTH // 2 - 160, HEIGHT // 2 + 10, (200, 200, 210))
            pygame.display.flip()
            continue

        biome = world_biome_for_x(player.x + player.w / 2)
        in_cave = cave_depth_for_y(player.y + player.h / 2) > 0.55
        desired_music = select_music_track(sounds, biome, in_cave=in_cave, boss=any(e.boss and e.health > 0 for e in enemies))
        if desired_music != current_music:
            play_music_track(sounds, desired_music)
            current_music = desired_music
            current_biome = biome
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player.vx -= MOVE_ACCEL * dt
            player.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player.vx += MOVE_ACCEL * dt
            player.facing = 1
        if not (keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            player.vx *= 0.82
            if abs(player.vx) < 5:
                player.vx = 0
        player.vx = max(-MAX_SPEED, min(MAX_SPEED, player.vx))
        if keys[pygame.K_SPACE] and player.on_ground:
            player.vy = -JUMP_SPEED
            player.on_ground = False

        player.vy = min(player.vy + GRAVITY * dt, TERMINAL_VEL)
        player.x, player.y, player.vx, player.vy, player.on_ground = move_entity(
            world, player.x, player.y, player.w, player.h, player.vx, player.vy, dt
        )

        if player.y > WORLD_H * TILE:
            player.health -= 10 * (1 - armor_reduction(player)) * dt
            player.x, player.y = 12 * TILE, 10 * TILE
            player.vx = player.vy = 0

        center_tx = int((player.x + player.w / 2) // TILE)
        center_ty = int((player.y + player.h / 2) // TILE)
        feet_ty = int((player.y + player.h - 1) // TILE)
        in_water = get_block(world, center_tx, center_ty) == WATER or get_block(world, center_tx, feet_ty) == WATER
        in_lava = get_block(world, center_tx, center_ty) == LAVA or get_block(world, center_tx, feet_ty) == LAVA
        if in_water:
            player.vx *= 0.92
            player.vy *= 0.90
        if in_lava:
            player.health -= 18 * (1 - armor_reduction(player)) * dt
            player.vx *= 0.85

        mouse = pygame.mouse.get_pos()
        cam_target_x = player.x + player.w / 2 - WIDTH / 2
        cam_target_y = player.y + player.h / 2 - HEIGHT / 2
        camera_x += (cam_target_x - camera_x) * min(1, 6 * dt)
        camera_y += (cam_target_y - camera_y) * min(1, 6 * dt)
        camera_x = max(0, min(camera_x, WORLD_W * TILE - WIDTH))
        camera_y = max(0, min(camera_y, WORLD_H * TILE - HEIGHT))

        world_mouse = (mouse[0] + camera_x, mouse[1] + camera_y)
        tx = int(world_mouse[0] // TILE)
        ty = int(world_mouse[1] // TILE)
        target_rect = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
        dist = math.hypot((player.x + player.w / 2) - world_mouse[0], (player.y + player.h / 2) - world_mouse[1])
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_world_rect = pygame.Rect(int(world_mouse[0] - 2), int(world_mouse[1] - 2), 4, 4)
        chest_target = nearby_chest(world, player)
        if chest_target is None:
            chest_panel_open = False
            player.chest_open = ""
        else:
            player.chest_open = chest_key(*chest_target)

        clicked_enemy = None
        if mouse_buttons[0]:
            for enemy in enemies:
                if enemy.health > 0 and mouse_world_rect.colliderect(enemy.rect):
                    clicked_enemy = enemy
                    break

        if mouse_buttons[0] and action_cooldown <= 0 and clicked_enemy is not None:
            enemy = clicked_enemy
            player.attack_timer = 0.15
            if player.equipped == 101:
                player.attack_cooldown = 0.22
                attack_flash = 0.18
                attack_rect = pygame.Rect(enemy.rect.x - 12, enemy.rect.y - 6, enemy.rect.w + 24, enemy.rect.h + 12)
            else:
                player.attack_cooldown = 0.3
                attack_flash = 0.10
                attack_rect = pygame.Rect(enemy.rect.x - 8, enemy.rect.y - 8, enemy.rect.w + 16, enemy.rect.h + 16)
            damage = 18 if player.equipped == 101 else 20 if player.equipped in (103, 104) else 10
            if enemy.boss:
                damage = max(4, damage // 2)
            enemy.health -= damage
            enemy.vx += (240 if player.equipped == 101 else 140) * (1 if player.x < enemy.x else -1)
            enemy.vy -= 240 if player.equipped == 101 else 160
            play_sound(sounds, "swing")
            if enemy.health <= 0:
                drop_table = [WOOD, STONE, COAL_ORE, IRON_ORE, 100, TORCH, FIBER]
                if enemy.kind == "zombie":
                    drop_table += [SAND, STONE, 100, FIBER]
                if enemy.kind == "eye":
                    drop_table += [GOLD_ORE, GOLD_ORE, IRON_ORE, HEAL_POTION]
                if enemy.boss:
                    drop_table += [GOLD_ORE, GOLD_ORE, IRON_ORE, 101, 102, 103, 104, CHEST, WORKBENCH, TORCH, ARMOR, LANTERN, BOMB]
                drops.append(Drop(enemy.x, enemy.y, random.choice(drop_table), random.randint(3, 8 if enemy.boss else 4), random.uniform(-80, 80), -160, life=60 if enemy.boss else 30))
                play_sound(sounds, "hit")
                if enemy.boss:
                    play_sound(sounds, "boss")
            action_cooldown = player.attack_cooldown
        elif mouse_buttons[0] and action_cooldown <= 0 and dist <= REACH:
            block = get_block(world, tx, ty)
            if block in MINABLE:
                power = item_mining_power(player)
                if block == STONE and power < 2:
                    pass
                elif block in {COAL_ORE, IRON_ORE, GOLD_ORE} and power < 3:
                    pass
                else:
                    set_block(world, tx, ty, AIR)
                    if block in player.inventory:
                        give_item(player, block, 1)
                    if block == WOOD:
                        give_item(player, 100, 1)
                    if block == LEAF and random.random() < 0.2:
                        give_item(player, 100, 1)
                    if block == LEAF and random.random() < 0.35:
                        give_item(player, FIBER, 1)
                    if block == COAL_ORE:
                        give_item(player, COAL_ORE, 1)
                    if block == IRON_ORE:
                        give_item(player, IRON_ORE, 1)
                    if block == GOLD_ORE:
                        give_item(player, GOLD_ORE, 1)
                    action_cooldown = 0.12
                    play_sound(sounds, "mine")
                    if random.random() < 0.15:
                        drops.append(Drop(tx * TILE + 8, ty * TILE + 8, block, 1, random.uniform(-40, 40), -80))

        if mouse_buttons[2] and action_cooldown <= 0 and dist <= REACH:
            if get_block(world, tx, ty) == AIR and player.inventory.get(player.selected, 0) > 0:
                if not rect_collides_world(world, target_rect):
                    set_block(world, tx, ty, player.selected)
                    player.inventory[player.selected] -= 1
                    action_cooldown = 0.12
                    play_sound(sounds, "place")

        if chest_panel_open and chest_target is None:
            chest_panel_open = False
        if mouse_buttons[1] and action_cooldown <= 0 and not craft_panel_open and not chest_panel_open:
            player.attack_timer = 0.15
            if player.equipped == 101:
                player.attack_cooldown = 0.26
                attack_flash = 0.18
                attack_rect = pygame.Rect(player.rect.x + (player.w if player.facing == 1 else -52), player.rect.y + 2, 52, player.h - 4)
            else:
                player.attack_cooldown = 0.35
                attack_flash = 0.12
                attack_rect = pygame.Rect(player.rect.x + (player.w if player.facing == 1 else -42), player.rect.y + 6, 42, player.h - 12)
            for enemy in enemies:
                if enemy.health > 0 and attack_rect.colliderect(enemy.rect):
                    damage = 18 if player.equipped == 101 else 20 if player.equipped in (103, 104) else 10
                    if enemy.boss:
                        damage = max(4, damage // 2)
                    enemy.health -= damage
                    enemy.vx += (220 if player.equipped == 101 else 140) * player.facing
                    enemy.vy -= 220 if player.equipped == 101 else 160
                    play_sound(sounds, "swing")
                    if enemy.health <= 0:
                        drop_table = [WOOD, STONE, COAL_ORE, IRON_ORE, 100, TORCH, FIBER]
                        if enemy.kind == "zombie":
                            drop_table += [SAND, STONE, 100, FIBER]
                        if enemy.kind == "eye":
                            drop_table += [GOLD_ORE, GOLD_ORE, IRON_ORE, HEAL_POTION]
                        if enemy.boss:
                            drop_table += [GOLD_ORE, GOLD_ORE, IRON_ORE, 101, 102, 103, 104, CHEST, WORKBENCH, TORCH, ARMOR, LANTERN, BOMB]
                        drops.append(Drop(enemy.x, enemy.y, random.choice(drop_table), random.randint(3, 8 if enemy.boss else 4), random.uniform(-80, 80), -160, life=60 if enemy.boss else 30))
                        play_sound(sounds, "hit")
                        if enemy.boss:
                            play_sound(sounds, "boss")
            action_cooldown = player.attack_cooldown

        for enemy in enemies:
            if enemy.health <= 0:
                continue
            enemy.hurt_timer = max(0.0, enemy.hurt_timer - dt)
            enemy.timer -= dt
            if enemy.kind == "slime":
                if abs(player.x - enemy.x) < 420:
                    enemy.dir = 1 if player.x > enemy.x else -1
                elif enemy.timer <= 0:
                    enemy.dir = random.choice([-1, 1])
                    enemy.timer = random.uniform(1.0, 2.4)
                enemy.vx = enemy.dir * 90
                enemy.vy = min(enemy.vy + GRAVITY * dt, TERMINAL_VEL)
            elif enemy.kind == "zombie":
                if abs(player.x - enemy.x) < 620:
                    enemy.dir = 1 if player.x > enemy.x else -1
                enemy.vx = enemy.dir * 120
                if abs(player.x - enemy.x) < 90 and abs(player.y - enemy.y) < 36 and enemy.timer <= 0:
                    enemy.vy = -680
                    enemy.timer = 1.0
                enemy.vy = min(enemy.vy + GRAVITY * dt, TERMINAL_VEL)
            elif enemy.kind == "bat":
                enemy.vx = math.cos(pygame.time.get_ticks() * 0.004 + enemy.x * 0.01) * 160
                enemy.vy = math.sin(pygame.time.get_ticks() * 0.006 + enemy.y * 0.01) * 40
            elif enemy.kind == "eye":
                dx = player.x - enemy.x
                dy = player.y - enemy.y
                distp = max(1.0, math.hypot(dx, dy))
                enemy.vx = dx / distp * (240 if enemy.boss else 190)
                enemy.vy = dy / distp * (180 if enemy.boss else 140)
            elif enemy.kind == "slime_king":
                enemy.phase = 2 if enemy.health < 100 else 1 if enemy.health < 170 else 0
                if abs(player.x - enemy.x) < 900:
                    enemy.dir = 1 if player.x > enemy.x else -1
                dash_speed = 120 + 30 * enemy.phase
                enemy.vx = enemy.dir * dash_speed
                enemy.vy = min(enemy.vy + GRAVITY * (0.85 - 0.1 * enemy.phase) * dt, TERMINAL_VEL)
                enemy.spawn_timer -= dt
                enemy.shoot_timer -= dt
                if enemy.phase >= 1 and enemy.spawn_timer <= 0:
                    enemies.append(Enemy(enemy.x + random.randint(-90, 90), enemy.y - 10, kind="slime", health=20, w=28, h=20))
                    enemy.spawn_timer = 3.0 - enemy.phase * 0.7
                if enemy.phase >= 2 and enemy.shoot_timer <= 0:
                    enemies.append(Enemy(enemy.x + random.randint(-60, 60), enemy.y - 60, kind="eye", health=18, w=24, h=24))
                    enemy.shoot_timer = 2.2
            else:
                if player.y < enemy.y:
                    enemy.vy -= 40 * dt
                enemy.vx = max(-110, min(110, (player.x - enemy.x) * 0.8))
                enemy.vy = max(-220, min(220, enemy.vy + math.sin(pygame.time.get_ticks() * 0.004) * 4))
            enemy.x, enemy.y, enemy.vx, enemy.vy, _ = move_entity(world, enemy.x, enemy.y, enemy.w, enemy.h, enemy.vx, enemy.vy, dt)
            if enemy.rect.colliderect(player.rect):
                player.health -= 24 * (1 - armor_reduction(player)) * dt
                push = 220 if player.x < enemy.x else -220
                player.vx += push * dt

        for drop in drops:
            drop.life -= dt
            drop.vy = min(drop.vy + GRAVITY * 0.7 * dt, TERMINAL_VEL)
            drop.x, drop.y, drop.vx, drop.vy, _ = move_entity(world, drop.x, drop.y, drop.w, drop.h, drop.vx, drop.vy, dt)
            if drop.rect.colliderect(player.rect):
                give_item(player, drop.item, drop.amount)
                drop.life = 0
                play_sound(sounds, "pickup")

        drops = [d for d in drops if d.life > 0]
        enemies = [e for e in enemies if e.health > 0 or random.random() < 0.995]

        screen.fill(bg)
        daylight = math.cos(time_of_day * math.tau)
        sky_top = (
            int(30 + 80 * max(0, daylight)),
            int(50 + 90 * max(0, daylight)),
            int(90 + 100 * max(0, daylight)),
        )
        sky_bottom = (
            int(10 + 60 * max(0, daylight)),
            int(20 + 80 * max(0, daylight)),
            int(35 + 120 * max(0, daylight)),
        )
        for y in range(HEIGHT):
            t = y / HEIGHT
            c = (
                int(sky_top[0] * (1 - t) + sky_bottom[0] * t),
                int(sky_top[1] * (1 - t) + sky_bottom[1] * t),
                int(sky_top[2] * (1 - t) + sky_bottom[2] * t),
            )
            pygame.draw.line(screen, c, (0, y), (WIDTH, y))
        draw_sun_x = int((camera_x * 0.06 + time_of_day * WIDTH) % (WIDTH + 200) - 100)
        sun_y = 110 + int(35 * math.sin(time_of_day * math.tau))
        if daylight > -0.2:
            pygame.draw.circle(screen, (255, 235, 120), (draw_sun_x, sun_y), 38)
        else:
            pygame.draw.circle(screen, (220, 225, 255), (draw_sun_x, sun_y), 24)
            pygame.draw.circle(screen, (120, 130, 180), (draw_sun_x + 10, sun_y - 8), 4)

        far_x = int(-camera_x * 0.08) % far_parallax.get_width()
        mid_x = int(-camera_x * 0.18) % mid_parallax.get_width()
        parallax_tint = (90, 150, 100) if biome == "forest" else (200, 180, 110) if biome == "desert" else (100, 110, 135)
        parallax_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        parallax_overlay.fill((*parallax_tint, 14))
        screen.blit(parallax_overlay, (0, 0))
        screen.blit(far_parallax, (-far_x, HEIGHT // 4 - far_parallax.get_height() // 2))
        screen.blit(far_parallax, (-far_x + far_parallax.get_width(), HEIGHT // 4 - far_parallax.get_height() // 2))
        screen.blit(mid_parallax, (-mid_x, HEIGHT // 2 - mid_parallax.get_height() // 2))
        screen.blit(mid_parallax, (-mid_x + mid_parallax.get_width(), HEIGHT // 2 - mid_parallax.get_height() // 2))

        start_tx = max(0, int(camera_x // TILE) - 1)
        end_tx = min(WORLD_W, int((camera_x + WIDTH) // TILE) + 2)
        start_ty = max(0, int(camera_y // TILE) - 1)
        end_ty = min(WORLD_H, int((camera_y + HEIGHT) // TILE) + 2)
        for x in range(start_tx, end_tx):
            for y in range(start_ty, end_ty):
                block = world[x][y]
                if block != AIR:
                    sx, sy = world_to_screen(camera_x, camera_y, x * TILE, y * TILE)
                    if block in (WATER, LAVA):
                        wave = int(math.sin((pygame.time.get_ticks() * 0.008) + x * 0.4 + y * 0.2) * 4)
                        liquid_color = (52, 128, 235) if block == WATER else (240, 104, 36)
                        highlight = (160, 220, 255) if block == WATER else (255, 190, 90)
                        pygame.draw.rect(screen, liquid_color, (sx, sy + wave, TILE, TILE))
                        pygame.draw.circle(screen, highlight, (sx + 8, sy + 8 + wave), 3)
                        pygame.draw.circle(screen, highlight, (sx + 20, sy + 14 + wave), 2)
                    else:
                        tex = block_textures.get(block)
                        if tex:
                            screen.blit(tex, (sx, sy))
                        else:
                            pygame.draw.rect(screen, BLOCK_COLORS[block], (sx, sy, TILE, TILE))
                    if block == GRASS:
                        pygame.draw.rect(screen, (95, 190, 86), (sx, sy, TILE, 5))
                    elif block == TORCH:
                        pygame.draw.circle(screen, (255, 210, 120), (sx + 16, sy + 14), 6)
                        pygame.draw.circle(screen, (255, 160, 40), (sx + 16, sy + 14), 10, 2)
                    elif block == WORKBENCH:
                        pygame.draw.rect(screen, (115, 80, 48), (sx + 4, sy + 6, 24, 20), 1, border_radius=2)
                    elif block == CHEST:
                        pygame.draw.line(screen, (190, 140, 80), (sx + 6, sy + 12), (sx + 26, sy + 12), 2)
                    pygame.draw.rect(screen, (0, 0, 0), (sx, sy + (wave if block in (WATER, LAVA) else 0), TILE, TILE), 1)

        if daylight < 0.15:
            darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(min(170, 170 * (-daylight)))
            darkness.fill((0, 0, 20))
            darkness.set_alpha(alpha)
            screen.blit(darkness, (0, 0))

        for drop in drops:
            sx, sy = world_to_screen(camera_x, camera_y, drop.x, drop.y)
            color = BLOCK_COLORS.get(drop.item, (255, 255, 255))
            glow = pygame.Surface((drop.w + 12, drop.h + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (*color, 60), (0, 0, drop.w + 12, drop.h + 12))
            screen.blit(glow, (sx - 6, sy - 6))
            tex = item_surface(drop.item, block_textures, item_textures)
            if tex:
                screen.blit(pygame.transform.smoothscale(tex, (drop.w, drop.h)), (sx, sy))
            else:
                pygame.draw.rect(screen, color, (sx, sy, drop.w, drop.h), border_radius=4)
            pygame.draw.rect(screen, (0, 0, 0), (sx, sy, drop.w, drop.h), 1, border_radius=4)

        for enemy in enemies:
            if enemy.health <= 0:
                continue
            sx, sy = world_to_screen(camera_x, camera_y, enemy.x, enemy.y)
            biome_sprite_key = enemy.kind
            if enemy.kind == "slime":
                biome_sprite_key = "slime_forest" if biome == "forest" else "slime_desert" if biome == "desert" else "slime"
            elif enemy.kind == "zombie":
                biome_sprite_key = "zombie_desert" if biome == "desert" else "zombie"
            elif enemy.kind == "bat":
                biome_sprite_key = "bat_cave" if in_cave else "bat"
            sprite = enemy_sprites.get((biome_sprite_key, enemy.boss)) or enemy_sprites.get((biome_sprite_key, False)) or enemy_sprites.get((enemy.kind, enemy.boss)) or enemy_sprites.get((enemy.kind, False))
            if sprite:
                if enemy.kind == "eye":
                    bob = int(math.sin(pygame.time.get_ticks() * 0.005 + enemy.x * 0.01) * 2)
                    pulse = 1 + (math.sin(pygame.time.get_ticks() * 0.01) * 0.03)
                    screen.blit(pygame.transform.smoothscale(sprite, (int(sprite.get_width() * pulse), int(sprite.get_height() * pulse))), (sx - 1, sy + bob - 1))
                else:
                    flicker = int(math.sin(pygame.time.get_ticks() * 0.008 + enemy.x * 0.05) * 1)
                    screen.blit(sprite, (sx, sy + flicker))
            else:
                pygame.draw.ellipse(screen, (120, 220, 110), (sx, sy, enemy.w, enemy.h))

        px, py = world_to_screen(camera_x, camera_y, player.x, player.y)
        flip = player.facing == -1
        player_img = pygame.transform.flip(player_sprite, flip, False) if flip else player_sprite
        screen.blit(player_img, (px, py))
        hand_x = px + (player.w - 4 if player.facing == 1 else -8)
        pygame.draw.rect(screen, (140, 96, 56), (hand_x, py + 22, 10, 4))
        if attack_flash > 0:
            if player.equipped == 101:
                sword_img = pygame.transform.flip(sword_sprite, True, False) if player.facing == -1 else sword_sprite
                sword_x = px + (player.w + 6 if player.facing == 1 else -sword_img.get_width() - 6)
                sword_y = py + 16
                screen.blit(sword_img, (sword_x, sword_y))
                arc = pygame.Rect(px + (player.w if player.facing == 1 else -56), py + 6, 56, player.h - 8)
                pygame.draw.arc(screen, (255, 230, 140), arc, 0.2, 1.4, 3)
            else:
                attack_rect = pygame.Rect(px + (player.w if player.facing == 1 else -42), py + 6, 42, player.h - 12)
                pygame.draw.rect(screen, (255, 225, 120), attack_rect, 2)

        pygame.draw.rect(screen, (20, 20, 20), (18, 18, 240, 20), border_radius=6)
        pygame.draw.rect(screen, (200, 60, 60), (18, 18, 240 * max(0, player.health) / 100, 20), border_radius=6)

        hotbar_y = HEIGHT - 64
        pygame.draw.rect(screen, (18, 18, 18), (WIDTH // 2 - 260, hotbar_y - 10, 520, 58), border_radius=12)
        for i, block in enumerate(selected_order):
            x = WIDTH // 2 - 235 + i * 72
            box = pygame.Rect(x, hotbar_y, 60, 36)
            pygame.draw.rect(screen, (48, 42, 36), box, border_radius=6)
            tex = item_surface(block, block_textures, item_textures)
            if tex:
                scaled = pygame.transform.smoothscale(tex, (28, 20))
                screen.blit(scaled, (box.x + 16, box.y + 8))
            else:
                pygame.draw.rect(screen, BLOCK_COLORS[block], box.inflate(-16, -16))
            if player.selected == block:
                pygame.draw.rect(screen, (255, 240, 100), box, 3, border_radius=6)
            qty = player.inventory.get(block, 0)
            draw_text(screen, font, str(qty), x + 4, hotbar_y + 15, (255, 255, 255))
            draw_text(screen, font, str(i + 1), x + 42, hotbar_y + 2, (220, 220, 220))

        if inventory_open:
            inv_panel = inventory_panel_rect()
            pygame.draw.rect(screen, (18, 18, 20), inv_panel, border_radius=16)
            pygame.draw.rect(screen, (200, 170, 110), inv_panel, 2, border_radius=16)
            title_bar = pygame.Rect(inv_panel.x, inv_panel.y, inv_panel.w, 32)
            pygame.draw.rect(screen, (28, 24, 22), title_bar, border_radius=16)
            inv_items = inventory_items(player.inventory)
            draw_text(screen, font, "Inventory", inv_panel.x + 14, inv_panel.y + 7, (245, 230, 200))
            draw_text(screen, font, "Drag items", inv_panel.x + 120, inv_panel.y + 7, (180, 180, 180))
            for idx in range(INVENTORY_CAPACITY):
                slot = inventory_slot_rect(idx, inv_panel.x + 12, inv_panel.y + 40, slot_size=28, gap=3, columns=INVENTORY_COLUMNS)
                pygame.draw.rect(screen, (52, 48, 44), slot, border_radius=8)
                if idx < len(inv_items):
                    item = inv_items[idx]
                    tex = item_surface(item, block_textures, item_textures)
                    if tex:
                        screen.blit(pygame.transform.smoothscale(tex, (15, 15)), (slot.x + 6, slot.y + 6))
                    else:
                        pygame.draw.rect(screen, BLOCK_COLORS.get(item, (255, 255, 255)), slot.inflate(-16, -16))
                    draw_text(screen, font, str(player.inventory[item]), slot.x + 1, slot.y + 14, (255, 255, 255))
                    if player.inventory[item] > 1:
                        pygame.draw.circle(screen, (255, 255, 255), (slot.right - 7, slot.top + 7), 3)
                pygame.draw.rect(screen, (0, 0, 0), slot, 1, border_radius=8)

        # Minimap
        mmx = WIDTH - MINIMAP_W - 18
        mmy = 18
        mini = pygame.Surface((MINIMAP_W, MINIMAP_H))
        mini.fill((12, 14, 20))
        for x in range(0, WORLD_W, 2):
            for y in range(0, WORLD_H, 2):
                block = world[x][y]
                if block != AIR:
                    mx = x * MINIMAP_W // WORLD_W
                    my = y * MINIMAP_H // WORLD_H
                    color = BLOCK_COLORS.get(block, (255, 255, 255))
                    if block in {STONE, COAL_ORE, IRON_ORE, GOLD_ORE}:
                        color = tuple(min(255, c + 20) for c in color)
                    mini.set_at((mx, my), color)
                    if y > WORLD_H // 2 and block in {STONE, COAL_ORE, IRON_ORE, GOLD_ORE}:
                        mini.set_at((mx, my), tuple(max(0, c - 10) for c in color))
        pxm = int(player.x / (WORLD_W * TILE) * MINIMAP_W)
        pym = int(player.y / (WORLD_H * TILE) * MINIMAP_H)
        pygame.draw.circle(mini, (255, 255, 255), (pxm, pym), 2)
        for enemy in enemies:
            if enemy.health > 0:
                ex = int(enemy.x / (WORLD_W * TILE) * MINIMAP_W)
                ey = int(enemy.y / (WORLD_H * TILE) * MINIMAP_H)
                icon = (255, 70, 70)
                if enemy.kind == "bat":
                    icon = (120, 120, 255)
                elif enemy.kind == "eye":
                    icon = (230, 120, 255)
                elif enemy.kind == "zombie":
                    icon = (120, 200, 120)
                if enemy.boss:
                    icon = (255, 180, 40)
                pygame.draw.circle(mini, icon, (max(0, min(MINIMAP_W - 1, ex)), max(0, min(MINIMAP_H - 1, ey))), 2 if not enemy.boss else 3)
        screen.blit(mini, (mmx, mmy))
        pygame.draw.rect(screen, (0, 0, 0), (mmx, mmy, MINIMAP_W, MINIMAP_H), 2)

        if player.health <= 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

        if craft_panel_open:
            panel = pygame.Rect(WIDTH - 390, 120, 350, 420)
            pygame.draw.rect(screen, (18, 18, 20), panel, border_radius=14)
            pygame.draw.rect(screen, (220, 190, 120), panel, 2, border_radius=14)
            pygame.draw.rect(screen, (30, 28, 26), (panel.x, panel.y, panel.w, 38), border_radius=14)
            draw_text(screen, big, "Crafting", panel.x + 16, panel.y + 7, (245, 230, 200))
            draw_text(screen, font, "Click an item to craft", panel.x + 16, panel.y + 42, (220, 220, 220))
            draw_text(screen, font, "Scroll: mouse wheel", panel.x + 166, panel.y + 42, (180, 180, 180))
            visible = RECIPES[craft_scroll:craft_scroll + 7]
            for i, recipe in enumerate(visible):
                yy = panel.y + 72 + i * 48
                can_make = all(count_inventory(player, item) >= amt for item, amt in recipe["requires"].items()) and has_station(world, player, recipe["station"])
                row = pygame.Rect(panel.x + 12, yy, 326, 40)
                pygame.draw.rect(screen, (58, 54, 50) if can_make else (42, 40, 38), row, border_radius=8)
                if can_make:
                    pygame.draw.rect(screen, (90, 160, 90), row, 2, border_radius=8)
                draw_text(screen, font, recipe["name"], row.x + 10, row.y + 7, (255, 255, 255))
                req = ", ".join(f"{ITEM_NAME.get(k, str(k))}x{v}" for k, v in recipe["requires"].items())
                draw_text(screen, font, req, row.x + 10, row.y + 22, (220, 220, 220))
                draw_text(screen, font, ITEM_NAME.get(recipe["result"], str(recipe["result"])), row.right - 110, row.y + 12, (255, 220, 120))
                if not can_make:
                    reason = "Need workbench" if recipe["station"] and not has_station(world, player, recipe["station"]) else "Missing items"
                    draw_text(screen, font, reason, row.right - 150, row.y + 24, (255, 120, 120))

        if chest_panel_open and chest_target:
            txc, tyc = chest_target
            chest = chest_inventory(chest_storage, txc, tyc)
            panel = chest_panel_rect()
            pygame.draw.rect(screen, (14, 14, 16), panel, border_radius=14)
            pygame.draw.rect(screen, (170, 120, 70), panel, 2, border_radius=12)
            pygame.draw.rect(screen, (32, 26, 22), (panel.x, panel.y, panel.w, 38), border_radius=14)
            draw_text(screen, big, "Chest", panel.x + 16, panel.y + 7, (245, 230, 200))
            draw_text(screen, font, "Left click = move stack   Right click = quick transfer", panel.x + 16, panel.y + 42, (220, 220, 220))
            chest_items = inventory_items(chest)
            inv_items = inventory_items(player.inventory)
            left_grid = pygame.Rect(panel.x + 24, panel.y + 78, 460, 318)
            right_grid = pygame.Rect(panel.x + 556, panel.y + 78, 460, 318)
            pygame.draw.rect(screen, (22, 18, 16), left_grid, border_radius=12)
            pygame.draw.rect(screen, (22, 18, 16), right_grid, border_radius=12)
            pygame.draw.rect(screen, (105, 75, 45), left_grid, 2, border_radius=12)
            pygame.draw.rect(screen, (105, 75, 45), right_grid, 2, border_radius=12)
            draw_text(screen, font, "Chest Storage", left_grid.x + 10, left_grid.y - 24, (245, 230, 200))
            draw_text(screen, font, "Inventory", right_grid.x + 10, right_grid.y - 24, (245, 230, 200))
            for idx in range(INVENTORY_CAPACITY):
                slot = inventory_slot_rect(idx, left_grid.x + 12, left_grid.y + 12, slot_size=46, gap=6, columns=INVENTORY_COLUMNS)
                pygame.draw.rect(screen, (58, 58, 58), slot, border_radius=8)
                if idx < len(chest_items):
                    item = chest_items[idx]
                    tex = item_surface(item, block_textures, item_textures)
                    if tex:
                        screen.blit(pygame.transform.smoothscale(tex, (26, 26)), (slot.x + 10, slot.y + 10))
                    else:
                        pygame.draw.rect(screen, BLOCK_COLORS.get(item, (255, 255, 255)), slot.inflate(-14, -14))
                    draw_text(screen, font, str(chest[item]), slot.x + 4, slot.y + 26, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), slot, 1, border_radius=8)
            for idx in range(INVENTORY_CAPACITY):
                slot = inventory_slot_rect(idx, right_grid.x + 12, right_grid.y + 12, slot_size=46, gap=6, columns=INVENTORY_COLUMNS)
                pygame.draw.rect(screen, (58, 58, 58), slot, border_radius=8)
                if idx < len(inv_items):
                    item = inv_items[idx]
                    tex = item_surface(item, block_textures, item_textures)
                    if tex:
                        screen.blit(pygame.transform.smoothscale(tex, (26, 26)), (slot.x + 10, slot.y + 10))
                    else:
                        pygame.draw.rect(screen, BLOCK_COLORS.get(item, (255, 255, 255)), slot.inflate(-14, -14))
                    draw_text(screen, font, str(player.inventory[item]), slot.x + 4, slot.y + 26, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), slot, 1, border_radius=8)
            draw_text(screen, font, "Drag and drop items between the two panels", panel.x + 16, panel.y + 446, (220, 220, 220))

        if help_open:
            help_panel = pygame.Rect(18, 52, 250, 210)
            pygame.draw.rect(screen, (18, 18, 18), help_panel, border_radius=12)
            pygame.draw.rect(screen, (180, 180, 180), help_panel, 2, border_radius=12)
            for i, line in enumerate(HELP_LINES):
                draw_text(screen, font, line, help_panel.x + 12, help_panel.y + 10 + i * 18, (240, 240, 240))

        if drag_item is not None:
            mx, my = pygame.mouse.get_pos()
            pygame.draw.rect(screen, BLOCK_COLORS.get(drag_item, (255, 255, 255)), (mx - 16, my - 16, 32, 32), border_radius=6)

        # Lighting vignette
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for radius, alpha in ((260, 20), (360, 35), (520, 50)):
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (WIDTH // 2, HEIGHT // 2), radius)
        screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

        pygame.display.flip()

    save_game(world, player, enemies, drops, surface)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
