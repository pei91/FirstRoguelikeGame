import tcod as libtcod

from entity import Entity
from random import randint
from map_objects.tile import Tile
from map_objects.rectangle import Rect



class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]
        return tiles
    
    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height
                , player, entities, max_monsters_per_room):
        # Creat two rooms for demonstration purpose
        rooms = []
        num_rooms = 0

        for _ in range(max_rooms):
            # random w and h
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width -w -1)
            y = randint(0, map_height -h -1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and check if intersect
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else: 
                # this means no intersections, so room valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coord of new room
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # The first room, where the player starts
                    player.x = new_x
                    player.y = new_y
                else:
                    # all other room:
                    # connect it to the previous room with a tunnel

                    # center coord of previous room
                    (prev_x, prev_y) = rooms[num_rooms -1].center()

                    # flip a coin (0 or 1)
                    if randint(0, 1) ==1:
                        # first move horizon, then vertical
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first vertical, then horizon
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)
                self.place_entities(new_room, entities, max_monsters_per_room)

                # finally append the new room to the list
                rooms.append(new_room)
                num_rooms +=1

    def create_room(self, room):
        #  go through the tiles in the rectangle and meke them passable
        for x in range(room.x1 +1, room.x2):
            for y in range(room.y1 +1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
   
    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) +1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False


    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) +1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities, max_monsters_per_room):
        # Get a random num of monsters
        number_of_monsters = randint(0, max_monsters_per_room)

        for _ in range(number_of_monsters):
            # choose a random location in the room
            x = randint(room.x1 +1, room.x2 - 1)
            y = randint(room.y1 +1, room.y2 - 1)

            # if location no monster
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                # 80% Orc
                if randint(0, 100) < 80:
                    monster = Entity(x, y, 'o', libtcod.desaturated_green, 'Orc', blocks=True)
                # 20% Troll
                else:
                    monster = Entity(x, y, 'T', libtcod.dark_green, 'Troll', blocks=True)

                entities.append(monster)


    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        
        return False

    