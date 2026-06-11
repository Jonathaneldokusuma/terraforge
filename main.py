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
GRAVITY = 2200
MOVE_ACCEL = 2800
MAX_SPEED = 360
JUMP_SPEED = 760
TERMINAL_VEL = 1800
REACH = 7 * TILE
SAVE_FILE = "savegame.json"
DAY_LENGTH = 220.0


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
}

SOLID = {DIRT, STONE, GRASS, WOOD, LEAF, COAL_ORE, IRON_ORE, GOLD_ORE, SAND, WORKBENCH, CHEST}
PLACEABLE = {DIRT, STONE, GRASS, WOOD, LEAF, TORCH, WORKBENCH, CHEST, SAND}
MINABLE = {DIRT, STONE, GRASS, WOOD, LEAF, COAL_ORE, IRON_ORE, GOLD_ORE, SAND, WORKBENCH, CHEST}

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
    world = [[AIR for _ in range(WORLD_H)] for _ in range(WORLD_W)]
    surface = []
    h = WORLD_H // 2 + 8
    for x in range(WORLD_W):
        h += random.choice([-2, -1, 0, 0, 1, 1, 2]) if x else 0
        h = max(18, min(WORLD_H - 16, h))
        surface.append(h)
        for y in range(h, WORLD_H):
            if y == h:
                world[x][y] = GRASS
            elif y < h + 4:
                world[x][y] = DIRT
            else:
                world[x][y] = STONE

    for x in range(2, WORLD_W - 2):
        if random.random() < 0.06:
            depth = random.randint(1, 5)
            for y in range(surface[x] + depth, WORLD_H):
                if y < WORLD_H - 18 or random.random() > 0.5:
                    world[x][y] = AIR

    for _ in range(22):
        cx = random.randint(10, WORLD_W - 11)
        cy = random.randint(28, WORLD_H - 18)
        radius = random.randint(4, 10)
        carve_cave(world, cx, cy, radius, random.randint(24, 48))

    for _ in range(260):
        x = random.randint(4, WORLD_W - 5)
        y = random.randint(25, WORLD_H - 6)
        if world[x][y] == STONE:
            roll = random.random()
            if roll < 0.07:
                world[x][y] = COAL_ORE
            elif roll < 0.10:
                world[x][y] = IRON_ORE
            elif roll < 0.105:
                world[x][y] = GOLD_ORE

    for _ in range(10):
        x = random.randint(8, WORLD_W - 9)
        y = surface[x]
        if world[x][y] == GRASS and random.random() < 0.35:
            world[x][y - 1] = CHEST

    for _ in range(22):
        x = random.randint(8, WORLD_W - 9)
        if 0 < surface[x] < WORLD_H - 8 and random.random() < 0.5:
            top = surface[x]
            trunk_h = random.randint(4, 7)
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
        x = random.randint(6, WORLD_W - 7)
        y = surface[x]
        if random.random() < 0.4 and y + 1 < WORLD_H:
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
        enemies.append(Enemy(x * TILE, (y - 1) * TILE, kind="slime"))
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
    return world, surface, player, enemies, drops, data.get("time_of_day", 0.0), data.get("chests", {})


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


def give_item(player, item, amount):
    player.inventory[item] = player.inventory.get(item, 0) + amount


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


def slot_item(inv, index):
    items = inventory_items(inv)
    if 0 <= index < len(items):
        return items[index]
    return None


def chest_panel_rect():
    return pygame.Rect(120, 100, 1040, 470)


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
    pygame.display.set_caption("TerraLite")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    big = pygame.font.SysFont("consolas", 30, bold=True)

    loaded = load_game()
    if loaded:
        world, surface, player, enemies, drops, time_of_day, chest_storage = loaded
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
    inventory_order = [DIRT, STONE, WOOD, LEAF, COAL_ORE, IRON_ORE, GOLD_ORE, SAND, TORCH, WORKBENCH, CHEST, 100, 101, 102, 103, 104]
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
                        inv_panel = pygame.Rect(WIDTH // 2 - 230, HEIGHT - 290, 460, 220)
                        if inv_panel.collidepoint(event.pos):
                            idx = inventory_slot_at(event.pos, inv_panel.x + 12, inv_panel.y + 44, INVENTORY_CAPACITY, columns=INVENTORY_COLUMNS)
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
            player.health -= 10 * dt
            player.x, player.y = 12 * TILE, 10 * TILE
            player.vx = player.vy = 0

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
        chest_target = nearby_chest(world, player)
        if chest_target is None:
            chest_panel_open = False
            player.chest_open = ""
        else:
            player.chest_open = chest_key(*chest_target)

        if mouse_buttons[0] and action_cooldown <= 0 and dist <= REACH:
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
                    if block == COAL_ORE:
                        give_item(player, COAL_ORE, 1)
                    if block == IRON_ORE:
                        give_item(player, IRON_ORE, 1)
                    if block == GOLD_ORE:
                        give_item(player, GOLD_ORE, 1)
                    action_cooldown = 0.12
                    if random.random() < 0.15:
                        drops.append(Drop(tx * TILE + 8, ty * TILE + 8, block, 1, random.uniform(-40, 40), -80))

        if mouse_buttons[2] and action_cooldown <= 0 and dist <= REACH:
            if get_block(world, tx, ty) == AIR and player.inventory.get(player.selected, 0) > 0:
                if not rect_collides_world(world, target_rect):
                    set_block(world, tx, ty, player.selected)
                    player.inventory[player.selected] -= 1
                    action_cooldown = 0.12

        if chest_panel_open and chest_target is None:
            chest_panel_open = False
        if mouse_buttons[1] and action_cooldown <= 0 and not craft_panel_open and not chest_panel_open:
            player.attack_timer = 0.15
            player.attack_cooldown = 0.35
            attack_flash = 0.12
            attack_rect = pygame.Rect(player.rect.x + (player.w if player.facing == 1 else -42), player.rect.y + 6, 42, player.h - 12)
            for enemy in enemies:
                if enemy.health > 0 and attack_rect.colliderect(enemy.rect):
                    damage = 14 if player.equipped == 101 else 20 if player.equipped in (103, 104) else 10
                    if enemy.boss:
                        damage = max(4, damage // 2)
                    enemy.health -= damage
                    enemy.vx += 140 * player.facing
                    enemy.vy -= 160
                    if enemy.health <= 0:
                        drop_table = [WOOD, STONE, COAL_ORE, IRON_ORE, 100, TORCH]
                        if enemy.kind == "zombie":
                            drop_table += [SAND, STONE, 100]
                        if enemy.kind == "eye":
                            drop_table += [GOLD_ORE, GOLD_ORE, IRON_ORE]
                        if enemy.boss:
                            drop_table += [GOLD_ORE, GOLD_ORE, IRON_ORE, 101, 102, 103, 104, CHEST, WORKBENCH, TORCH]
                        drops.append(Drop(enemy.x, enemy.y, random.choice(drop_table), random.randint(3, 8 if enemy.boss else 4), random.uniform(-80, 80), -160, life=60 if enemy.boss else 30))
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
                player.health -= 24 * dt
                push = 220 if player.x < enemy.x else -220
                player.vx += push * dt

        for drop in drops:
            drop.life -= dt
            drop.vy = min(drop.vy + GRAVITY * 0.7 * dt, TERMINAL_VEL)
            drop.x, drop.y, drop.vx, drop.vy, _ = move_entity(world, drop.x, drop.y, drop.w, drop.h, drop.vx, drop.vy, dt)
            if drop.rect.colliderect(player.rect):
                give_item(player, drop.item, drop.amount)
                drop.life = 0

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
        pygame.draw.rect(screen, sky_top, (0, 0, WIDTH, HEIGHT // 2))
        pygame.draw.rect(screen, sky_bottom, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
        draw_sun_x = int((camera_x * 0.06 + time_of_day * WIDTH) % (WIDTH + 200) - 100)
        sun_y = 110 + int(35 * math.sin(time_of_day * math.tau))
        if daylight > -0.2:
            pygame.draw.circle(screen, (255, 235, 120), (draw_sun_x, sun_y), 38)
        else:
            pygame.draw.circle(screen, (220, 225, 255), (draw_sun_x, sun_y), 24)
            pygame.draw.circle(screen, (120, 130, 180), (draw_sun_x + 10, sun_y - 8), 4)

        start_tx = max(0, int(camera_x // TILE) - 1)
        end_tx = min(WORLD_W, int((camera_x + WIDTH) // TILE) + 2)
        start_ty = max(0, int(camera_y // TILE) - 1)
        end_ty = min(WORLD_H, int((camera_y + HEIGHT) // TILE) + 2)
        for x in range(start_tx, end_tx):
            for y in range(start_ty, end_ty):
                block = world[x][y]
                if block != AIR:
                    sx, sy = world_to_screen(camera_x, camera_y, x * TILE, y * TILE)
                    pygame.draw.rect(screen, BLOCK_COLORS[block], (sx, sy, TILE, TILE))
                    if block == GRASS:
                        pygame.draw.rect(screen, (90, 180, 80), (sx, sy, TILE, 6))
                    if block == TORCH:
                        pygame.draw.circle(screen, (255, 190, 70), (sx + 16, sy + 14), 6)
                    pygame.draw.rect(screen, (0, 0, 0), (sx, sy, TILE, TILE), 1)

        if daylight < 0.15:
            darkness = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(min(170, 170 * (-daylight)))
            darkness.fill((0, 0, 20))
            darkness.set_alpha(alpha)
            screen.blit(darkness, (0, 0))

        for drop in drops:
            sx, sy = world_to_screen(camera_x, camera_y, drop.x, drop.y)
            pygame.draw.rect(screen, BLOCK_COLORS.get(drop.item, (255, 255, 255)), (sx, sy, drop.w, drop.h), border_radius=4)

        for enemy in enemies:
            if enemy.health <= 0:
                continue
            sx, sy = world_to_screen(camera_x, camera_y, enemy.x, enemy.y)
            if enemy.kind == "slime":
                pygame.draw.ellipse(screen, (120, 220, 110), (sx, sy, enemy.w, enemy.h))
                pygame.draw.circle(screen, (40, 70, 40), (sx + 9, sy + 8), 2)
                pygame.draw.circle(screen, (40, 70, 40), (sx + 19, sy + 8), 2)
            else:
                pygame.draw.ellipse(screen, (80, 80, 100), (sx, sy, enemy.w, enemy.h))
                pygame.draw.circle(screen, (220, 220, 240), (sx + 7, sy + 6), 2)
                pygame.draw.circle(screen, (220, 220, 240), (sx + 16, sy + 6), 2)

        px, py = world_to_screen(camera_x, camera_y, player.x, player.y)
        pygame.draw.rect(screen, (255, 210, 160), (px, py, player.w, player.h), border_radius=6)
        pygame.draw.rect(screen, (55, 90, 200), (px, py + 18, player.w, 26), border_radius=5)
        pygame.draw.rect(screen, (220, 180, 120), (px + 4, py - 6, 16, 12), border_radius=5)
        hand_x = px + (player.w - 4 if player.facing == 1 else -6)
        pygame.draw.rect(screen, (130, 90, 50), (hand_x, py + 20, 10, 4))
        if attack_flash > 0:
            attack_rect = pygame.Rect(px + (player.w if player.facing == 1 else -42), py + 6, 42, player.h - 12)
            pygame.draw.rect(screen, (255, 225, 120), attack_rect, 2)

        pygame.draw.rect(screen, (20, 20, 20), (18, 18, 240, 20), border_radius=6)
        pygame.draw.rect(screen, (200, 60, 60), (18, 18, 240 * max(0, player.health) / 100, 20), border_radius=6)

        hotbar_y = HEIGHT - 64
        pygame.draw.rect(screen, (18, 18, 18), (WIDTH // 2 - 260, hotbar_y - 10, 520, 58), border_radius=12)
        for i, block in enumerate(selected_order):
            x = WIDTH // 2 - 235 + i * 72
            box = pygame.Rect(x, hotbar_y, 60, 36)
            pygame.draw.rect(screen, (70, 70, 70), box, border_radius=6)
            pygame.draw.rect(screen, BLOCK_COLORS[block], box.inflate(-16, -16))
            if player.selected == block:
                pygame.draw.rect(screen, (255, 240, 100), box, 3, border_radius=6)
            qty = player.inventory.get(block, 0)
            draw_text(screen, font, str(qty), x + 4, hotbar_y + 15, (255, 255, 255))
            draw_text(screen, font, str(i + 1), x + 42, hotbar_y + 2, (220, 220, 220))

        if inventory_open:
            inv_panel = pygame.Rect(WIDTH // 2 - 230, HEIGHT - 290, 460, 220)
            pygame.draw.rect(screen, (28, 24, 22), inv_panel, border_radius=14)
            pygame.draw.rect(screen, (220, 190, 120), inv_panel, 2, border_radius=14)
            inv_items = inventory_items(player.inventory)
            for idx in range(INVENTORY_CAPACITY):
                slot = inventory_slot_rect(idx, inv_panel.x + 12, inv_panel.y + 44, columns=INVENTORY_COLUMNS)
                pygame.draw.rect(screen, (68, 68, 68), slot, border_radius=6)
                if idx < len(inv_items):
                    item = inv_items[idx]
                    pygame.draw.rect(screen, BLOCK_COLORS.get(item, (255, 255, 255)), slot.inflate(-14, -14))
                    draw_text(screen, font, str(player.inventory[item]), slot.x + 3, slot.y + 23, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), slot, 1, border_radius=6)
            draw_text(screen, font, "Inventory", inv_panel.x + 14, inv_panel.y + 12, (245, 230, 200))

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
            panel = pygame.Rect(WIDTH - 360, 120, 320, 420)
            pygame.draw.rect(screen, (30, 28, 26), panel, border_radius=12)
            pygame.draw.rect(screen, (220, 190, 120), panel, 2, border_radius=12)
            draw_text(screen, big, "Crafting", panel.x + 16, panel.y + 10, (245, 230, 200))
            draw_text(screen, font, "Click an item to craft", panel.x + 16, panel.y + 42, (220, 220, 220))
            draw_text(screen, font, "Scroll: mouse wheel", panel.x + 166, panel.y + 42, (180, 180, 180))
            visible = RECIPES[craft_scroll:craft_scroll + 7]
            for i, recipe in enumerate(visible):
                yy = panel.y + 72 + i * 48
                can_make = all(count_inventory(player, item) >= amt for item, amt in recipe["requires"].items()) and has_station(world, player, recipe["station"])
                row = pygame.Rect(panel.x + 12, yy, 296, 40)
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
            pygame.draw.rect(screen, (32, 26, 22), panel, border_radius=12)
            pygame.draw.rect(screen, (170, 120, 70), panel, 2, border_radius=12)
            draw_text(screen, big, "Chest", panel.x + 16, panel.y + 10, (245, 230, 200))
            draw_text(screen, font, "Left click to move stacks | Right click to quick transfer", panel.x + 16, panel.y + 42, (220, 220, 220))
            chest_items = inventory_items(chest)
            inv_items = inventory_items(player.inventory)
            left_grid = pygame.Rect(panel.x + 24, panel.y + 78, 360, 290)
            right_grid = pygame.Rect(panel.x + 560, panel.y + 78, 360, 290)
            pygame.draw.rect(screen, (22, 18, 16), left_grid, border_radius=10)
            pygame.draw.rect(screen, (22, 18, 16), right_grid, border_radius=10)
            pygame.draw.rect(screen, (105, 75, 45), left_grid, 2, border_radius=10)
            pygame.draw.rect(screen, (105, 75, 45), right_grid, 2, border_radius=10)
            draw_text(screen, font, "Chest Storage", left_grid.x + 10, left_grid.y - 24, (245, 230, 200))
            draw_text(screen, font, "Inventory", right_grid.x + 10, right_grid.y - 24, (245, 230, 200))
            for idx in range(INVENTORY_CAPACITY):
                slot = inventory_slot_rect(idx, left_grid.x + 12, left_grid.y + 12, slot_size=42, gap=6, columns=INVENTORY_COLUMNS)
                pygame.draw.rect(screen, (65, 65, 65), slot, border_radius=6)
                if idx < len(chest_items):
                    item = chest_items[idx]
                    pygame.draw.rect(screen, BLOCK_COLORS.get(item, (255, 255, 255)), slot.inflate(-12, -12))
                    draw_text(screen, font, str(chest[item]), slot.x + 3, slot.y + 20, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), slot, 1, border_radius=6)
            for idx in range(INVENTORY_CAPACITY):
                slot = inventory_slot_rect(idx, right_grid.x + 12, right_grid.y + 12, slot_size=42, gap=6, columns=INVENTORY_COLUMNS)
                pygame.draw.rect(screen, (65, 65, 65), slot, border_radius=6)
                if idx < len(inv_items):
                    item = inv_items[idx]
                    pygame.draw.rect(screen, BLOCK_COLORS.get(item, (255, 255, 255)), slot.inflate(-12, -12))
                    draw_text(screen, font, str(player.inventory[item]), slot.x + 3, slot.y + 20, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), slot, 1, border_radius=6)
            draw_text(screen, font, "Drag and drop between sides", panel.x + 16, panel.y + 446, (220, 220, 220))

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
