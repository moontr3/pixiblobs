# Pixiblobs

A lil pygame game I made for the 4th Algoritmika's Hackathon.

The theme of the event was Fantasy.

> There may be some unfinished or unused features in the code,
> like object tags, individual object walkables, particles,
> object tiles and some more.

**Hold Mouse Wheel to drag the camera around.**


## Requirements

```bash
pip uninstall pygame
pip install pygame-ce
pip install easing-functions
```


# Enemies

- **Zombie Maxwell** - Walks towards the castle. Damages objects
  on collision.

- **Skeleton Bob** - Walks towards the castle. Damages
  objects on collision. Has more HP than Bob and is faster.

- **Witch Anastasiya** - Walks towards the castle. Shoots
  projectiles from time to time.

- **French poop Zifuaro** - Walks towards the castle. Damages
  any objects nearby periodically.
  
- **Cloud Clyde** - Floats towards the castle. Spawns projectiles
  around himself periodically. Can pass through any wood-related
  object on the map.
  
- **Krivulka** - Can appear suddenly in large groups in the
  the late game. Phases through any object except the castle.
  Has a lot of HP and a big hitbox, also moves really fast.


# Objects

- **Tree** - Gives wood when broken.

- **Grass** - Does nothing.

- **Stick wall** (5w) - Works great as a reinforcement.

- **Wood block** (15w) - Even better than a stick wall.

- **Log stack** (40w) - 2 tiles in length. Amazing for
  protection.

- **Small/pink crystal** (100c) - Shoots nearby enemies with shards.

- **Medium/violet crystal** (250c) - Shoots nearby enemies with shards.
  Has greater range than small crystal and shards deal more
  damage.

- **Large/blue crystal** (750с) - Shoots nearby enemies with shards.
  Same as medium crystal, but shoots faster, deals a little bit
  more damage and is 2 blocks tall. Great as a wall defense.

- **Landmine** (250c) - If an enemy collides with it, it will
  receive from 25 to 50 damage. Destroys on collision. Can
  be destroyed with projectiles.


# Cheat codes

Press any of the numbers whilst holding Right Shift to enter
a cheat code. The input state will be shown in the console,
if avaliable.

> You need to enter a cheat code in the game window, not the
> console window. The console just shows the input progress.

> You can't erase numbers in the cheat code input field.
> To rewrite the cheat code, enter it fully and then start
> from the beginning.

|  Code  | Action |
| ----- | ----- |
| `0333` | Spawns a Zombie. |
| `0334` | Spawns a Skeleton. |
| `0335` | Spawns a Witch. |
| `0336` | Spawns a Poop. |
| `0337` | Spawns a Cloud. |
| `0338` | Spawns a Krivulka. |
| `8007` | Builds a Stick Wall (costs 1 crystal). |
| `8008` | Builds a Wood Block (costs 1 crystal). |
| `8009` | Builds a Log Stack (costs 1 crystal). |
| `8010` | Builds a Small Crystal (costs 1 crystal). |
| `8011` | Builds a Medium Crystal (costs 1 crystal). |
| `8012` | Builds a Large Crystal (costs 1 crystal). |
| `8013` | Builds a Landmine (costs 1 crystal). |
| `1488` | Kills all enemies on the map (player receives the crystals for the kills). |
| `6912` | Skips the current ongoing wave and eliminates all enemies on the map (player does NOT receive the crystals for eliminations). |
| `7300` | Removes the timeout on the cursor for the rest of the game. |


# Make custom maps

You can use [`map builder`](map_builder.py) included in the
project to make your own maps:

1. Open the utility.
2. Enter 2 integers for the X and Y size of the map.
3. Enter map name - also a filename of the map.
4. A pygame window will open. The instructions on how
   to build a map will be shown in the console.
5. Upon saving or closing the app the map will save
   in the `maps/` folder under a filename `<entered name>.pbmap`.

> The saving will overwrite any existing map with the same
> name in the maps/ folder.

> To close the app without saving press Ctrl+C in the console
> or just close using Task Manager, should work.


# How custom maps work

If you want to make your own map for the game, you need a file
in .pbmap format.

It should contain data in the following format:

A list of integers separated by semicolons `;`.
The first 2 integers represent X and Y size of the map,
then all blocks of 2 integers represent a coordinate
of a water tile on the map.

The file should have an even amount of integers, and a
minimum of 2 integers. There _can_ be zero amount of
water tiles, but the size of the map is required to have.

```
25;25;5;5;6;6;7;7
```

In the above example the map has a size of `(25, 25)` and
has water tiles at `(5, 5)`, `(6, 6)`, `(7, 7)`.
