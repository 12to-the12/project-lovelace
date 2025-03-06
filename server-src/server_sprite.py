from time import time_ns  # purely relative value
from random import uniform
from config import config

dist = lambda x: uniform(-x, x)
from math import pi as π
import random


class Vector:
    def __init__(self, *args):
        # print(args)
        # print(args[0])
        if not args:
            args = (0, 0, 0)
        # self.vector= [x,y,z]
        self.x = args[0]
        self.y = args[1]
        self.z = args[2]

    @property
    def mag(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    # @property
    # def x(self):
    #     return self.vector[0]

    # @property
    # def y(self):
    #     return self.vector[1]

    # @property
    # def z(self):
    #     return self.vector[2]

    def elementwise(self, other, operation):
        if isinstance(other, Vector):
            x = operation(self.x, other.x)
            y = operation(self.y, other.y)
            z = operation(self.z, other.z)
            return Vector(x, y, z)
        elif isinstance(other, (int, float)):
            x = operation(self.x, other)
            y = operation(self.y, other)
            z = operation(self.z, other)
            return Vector(x, y, z)

    def serialize(self):
        return self.x, self.y, self.z

    def __repr__(self) -> str:
        return f"({self.x},{self.y},{self.z})"

    def __iadd__(self, other) -> None:
        return self.elementwise(other, lambda x, y: x + y)

    def __isub__(self, other) -> None:
        return self.elementwise(other, lambda x, y: x + y)

    def __itruediv__(self, other) -> None:
        return self.elementwise(other, lambda x, y: x + y)

    def __imul__(self, other) -> None:
        return self.elementwise(other, lambda x, y: x + y)

    def __add__(self, other):
        return self.elementwise(other, lambda x, y: x + y)

    def __sub__(self, other):
        return self.elementwise(other, lambda x, y: x - y)

    def __truediv__(self, other):
        return self.elementwise(other, lambda x, y: x / y)

    def __mul__(self, other):
        return self.elementwise(other, lambda x, y: x * y)


class Entity:
    name = None
    frame = 0
    frame_rate = 0.25
    fname = "dragonyellow.rgb"
    dim = (32, 32)
    frame_count = 8

    def __init__(
        self,
        worldspace_position=None,
        velocity=None,
        acceleration=None,
        force=None,
        orientation=None,
        rotational_velocity=None,
        rotational_inertia=None,
        mass=None,
        world=None,
        bounds=(480, 320),
        **kwargs
    ):
        for k,v in kwargs.items():
          setattr(self, k, v)
        self.width, self.height = bounds
        factor = 1e2
        if worldspace_position:
            if isinstance(worldspace_position, (tuple, list)):
                worldspace_position = Vector(*worldspace_position)
        else:
            # pos = SpatialVector()
            worldspace_position = Vector()
        if not velocity:
            velocity = Vector()
            # vel = SpatialVector(dist(factor), dist(factor))
        if not acceleration:
            acceleration = Vector()
            # acc = SpatialVector(dist(factor), dist(factor))
        if not force:
            force = Vector()
            # acc = SpatialVector(dist(factor), dist(factor))
        if not orientation:
            orientation = 0
        if not rotational_velocity:
            rotational_velocity = 0
        if not rotational_inertia:
            rotational_inertia = 0
        if not mass:
            mass = 1
        if not self.name:
            self.name = random.random()
        

        assert world

        self.pos = worldspace_position
        self.vel = velocity
        self.acc = acceleration
        self.force = force
        self.orientation = orientation
        self.rotational_velocity = rotational_velocity
        self.rotational_inertia = rotational_inertia
        self.mass = mass

        self.force_factor = config.force_factor
        self.sap = config.sap
        self.booster = config.booster

        self.world = world
        self.world.entities.append(self)

        # assert (type(self.acc.x) == int) or (type(self.acc.x) == float), type(
        #     self.acc.x
        # )

        # orientation is encoded in radians counter clockwise

        self.last_updated_ns = time_ns()

    # def set_pos(self, pos_list):
    #     assert len(pos_list)==3

    #     x, y, z = pos_list
    #     self.x = x
    #     self.y = y
    #     self.z = z

    # the period since the values were last updated
    @property
    def age(self):
        timestamp_ns = time_ns()
        elapsed_ns = timestamp_ns - self.last_updated_ns
        self.last_updated_ns = timestamp_ns
        return elapsed_ns / 1e9

    @property
    def speed(self):
        return self.vel.mag

    # worldspace
    def worldspace_distance(self, other_pos) -> float:
        offset = Vector(
            self.pos.x - other_pos.x, self.pos.y - other_pos.y, self.pos.z - other_pos.z
        )
        distance = offset.mag
        return distance

    def advance(self, time):
        time *= .01 # FIXME: slowing time down
        self.acc = self.force / self.mass

        self.vel += self.acc * time

        self.acc *= 0

        self.force *= 0

        self.pos += self.vel * time

        self.orientation += self.rotational_velocity * time
        self.orientation %= 2 * π
        self.orientation *= self.sap**time

        self.pos.x %= self.width
        self.pos.y %= self.height
        # if self.pos.x>=self.width:self

        # self.vel *= self.sap**time

        self.frame += 0.25
        if self.frame >= self.frame_count:
            self.frame = 0

    def apply(self):
        time = self.age
        self.advance(time)

    def push(self, vector):
        # push is in terms of force
        self.force.x += self.force_factor * vector[0]
        self.force.y += self.force_factor * vector[1]

    def push_binary(self, right, left, up, down):
        if right:
            self.acc.x = self.force_factor
        if left:
            self.acc.x = -self.force_factor
        if right and left:
            self.acc.x = 0
        if (not right) and (not left):
            self.acc.x = 0
        if down:
            self.acc.y = self.force_factor
        if up:
            self.acc.y = -self.force_factor
        if down and up:
            self.acc.y = 0
        if (not up) and (not down):
            self.acc.y = 0
        self.apply()

    def serialize(self):
        return {'pos': self.pos.serialize(), 'dim': self.dim, 'fname': self.fname}

    def screen_coords(self):
        screenspace_x = int(self.pos.x - self.world.viewport_entity.pos.x)
        screenspace_y = int(self.pos.y - self.world.viewport_entity.pos.y)
        # screenspace_x = int(self.pos.x)
        # screenspace_y = int(self.pos.y)
        return (screenspace_x, screenspace_y)

    def draw(self):
        x, y = self.screen_coords()
        lcd_blit_file(
            self.fname,
            int(x - self.w / 2),
            int(y - self.h / 2),
            self.w,
            self.h,
            int(self.frame),
        )
        self.frame += 0.25
        if self.frame >= self.frame_count:
            self.frame = 0


class Player(Entity):
    def apply_booster(self, time):
        if self.vel.mag:
            # print("boosting...")
            direction = self.vel / self.vel.mag
            # print(self.force)
            self.force += direction * time * self.booster
            # print(self.force)

    def apply(self, playerstate):
        time = self.age
        self.apply_gravity()
        if playerstate["right"]:
            self.apply_booster(time)
        self.advance(time)

    def apply_gravity(self):
        star_x = 240
        star_y = 160
        star_position = Vector(star_x, star_y, 0)
        offset = star_position - self.pos
        norm_offset = offset / offset.mag
        distance_to_star = star_position.mag
        G = 6.6743e-11
        star_mass = 1e18
        # gfactor = 1e1

        force = G * (self.mass * star_mass) / (distance_to_star**2)
        force_vector = norm_offset * force

        self.force += force_vector


def mix(a, a_weight, b, b_weight):
    a = build_sprite(a)
    b = build_sprite(b)
    pos = Vector(
        a.pos.x * a_weight + b.pos.x * b_weight,
        a.pos.y * a_weight + b.pos.y * b_weight,
        a.pos.z * a_weight + b.pos.z * b_weight,
    )
    vel = Vector(
        a.vel.x * a_weight + b.vel.x * b_weight,
        a.vel.y * a_weight + b.vel.y * b_weight,
        a.vel.z * a_weight + b.vel.z * b_weight,
    )
    acc = Vector(
        a.acc.x * a_weight + b.acc.x * b_weight,
        a.acc.y * a_weight + b.acc.y * b_weight,
        a.acc.z * a_weight + b.acc.z * b_weight,
    )
    return Entity(worldspace_position=pos, velocity=vel, acceleration=acc)


# class World:
#     def __init__(self):
#         self.display_width = 480
#         self.display_height = 320
#         # where the world is in relation to the viewport
#         # top left corner of the screen
#         self.sprites = {}
#         self.viewport_entity = Entity(world=self)

#     def legitimize(self, id):  # means we're network connected...
#         self.id = id

#     # def update_from_packet(self,name,worldstate:str):
#     #     self.sprites[packet]


def build_sprite(state):
    pos = state["position"]
    vec = state["velocity"]
    acc = state["acceleration"]
    return Entity(Vector(*pos), Vector(*vec), Vector(*acc))


# world = World()


def pos_sprite(name, pos):
    if name.startswith("player"):
        player_id = int(name[6:] or 0)
        color = ["red", "green", "blue", "yellow"][player_id % 4]
        e = Player(Vector(*pos), world=world)
        e.fname = f"dragon{color}.rgb"
        w = 32
        h = 32
    if name == "hole":
        w = 64
        h = 64
        e = Entity(Vector(*pos), name=name, world=world)
        e.fname = "blackhole.rgb"
        e.frame_count = 1
    e.w = w
    e.h = h
    return e


# player = Player(name="player", world=world)
