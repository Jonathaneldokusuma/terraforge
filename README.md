# TerraForge

TerraForge is a Terraria-inspired 2D Python game prototype with mining, crafting, combat, caves, ore veins, chests, bosses, and save/load support.

## Features

- Procedurally generated terrain with caves and ore veins
- Mining and block placement
- Crafting UI
- Inventory and chest storage
- Enemies, drops, and boss encounters
- Minimap and day/night cycle
- Tile-based save/load system

## Controls

- `A/D` or left/right arrows: move
- `Space`: jump
- Left mouse: mine blocks
- Right mouse: place selected block
- Middle mouse: attack
- `Tab` or `C`: open crafting
- `T`: open chest UI when near a chest
- `I`: toggle inventory
- `H`: toggle help overlay
- `F5`: save
- `F9`: load
- `R`: new world

## Run

```bash
pip install -r requirements.txt
python main.py
```

## Notes

- Save files are written locally to `savegame.json`.
- The project is still a prototype, but it is fully playable and easy to extend.
