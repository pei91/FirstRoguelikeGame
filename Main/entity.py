"""
A generic object to represent players, enemies, items, etc.
"""
import tcod as libtcod
import math
from render_functions import RenderOrder

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x, y, char, color, name, blocks=False,
                 render_order=RenderOrder.CORPSE, fighter=None, ai=None,
                 item=None, inventory=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory

        if self.fighter:
            self.fighter.owner = self
        
        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self
        
        if self.inventory:
            self.inventory.owner = self

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def move_towarts(self, target_x, target_y, game_map, entities):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or 
                get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)
    
    def move_astar(self, target, entities, game_map):
        # Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(game_map.width, game_map.height)

        # Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                libtcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight,
                                            not game_map.tiles[x1][y1].blocked)
        # Scan all the objects to see if there are objects that must be navigated around
        # Check the object isn't self or the target (so the start and the end points are free)
        # The AI class handles the situation if self is next to the target so it will not use this A* functions anyway
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, entity.x, entity.y, True, False)
        
        # Allocate a A* path
        # The 1.41 is the nomal diagonal cost of moving, could be 0.0 if diagonal prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)

        # Compute the path between self's coord and target's
        libtcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # Check if the path exists, and in this case, also the path is shorter than 25 tiles
        # The path size matters if you want the monster to use alternative longer paths 
        # (for example through other rooms) if for example the player is in a corridor
        # It makes sense to keep path size relatively low to keep the monsters from running around 
        # the map if there's an alternative path really far away
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            # Find the next coord int the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                # Set self's coord to the next path tile
                self.x, self.y = x, y
            else:
                # Keep the old move function as a backup so if no paths 
                # (for example another monster blocks a corridor)
                # it will still try to move towards the player (closer to the corridor opening)
                self.move_towarts(target.x, target.y, game_map, entities)

            # delete to free memory
            libtcod.path_delete(my_path)
        
    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy **2)


# Loops through the entities, if one is blocking and at (x,y), return it
def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity
    
    return None