# Pixiblobs

A lil pygame game I made for the 4th Algoritmika's Hackathon.

The theme of the event was Fantasy.

> There may be some unfinished or unused features in the code,
> like object tags, individual object walkables, particles,
> object tiles and some more.


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