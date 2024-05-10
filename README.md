# Pixiblobs

A lil pygame game I made for the 4th Algoritmika's Hackathon.

The theme of the event was Fantasy.

> There may be some unfinished or unused features in the code,
> like object tags, individual object walkables, particles,
> object tiles and some more.


## Requirements

```bash
pip uninstall pygame
pip install pygame-ce
pip instll easing-functions
```


# Enemies

- **Zombie Bob** - Walks towards the castle. Damages objects
  on collision.

- **Skeleton Maxwell** - Walks towards the casthe. Damages
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
| `0333` | Spawns a Zombie. |
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
