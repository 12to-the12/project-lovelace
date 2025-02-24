from time import time as epoch
from time import time_ns as epoch_ns
from random import uniform

from config import config

dist = lambda x: uniform(-x, x)
from math import pi as π
from world import world


class vector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class Sprite:
    def __init__(
        self,
        worldspace_position=None,
        velocity=None,
        acceleration=None,
        orientation=None,
        rotational_velocity=None,
        rotational_inertia=None,
        mass=None,
        world=None,
        bounds=(480, 320),
    ):
        self.width, self.height = bounds
        factor = 1e2
        if not worldspace_position:
            # pos = SpatialVector()
            worldspace_position = vector(
                uniform(0, self.width), uniform(0, self.height), 0
            )
        if not velocity:
            velocity = vector()
            # vel = SpatialVector(dist(factor), dist(factor))
        if not acceleration:
            acceleration = vector()
            # acc = SpatialVector(dist(factor), dist(factor))
        if not orientation:
            orientation = 0
        if not rotational_velocity:
            rotational_velocity = 0
        if not rotational_inertia:
            rotational_inertia = 0
        if not mass:
            mass = 1

        self.pos = worldspace_position
        self.vel = velocity
        self.acc = acceleration
        self.orientation = orientation
        self.rotational_velocity = rotational_velocity
        self.rotational_inertia = rotational_inertia
        self.mass = mass

        self.acc_factor = config.acc_factor
        self.sap = config.sap

        # assert (type(self.acc.x) == int) or (type(self.acc.x) == float), type(
        #     self.acc.x
        # )

        # orientation is encoded in radians counter clockwise

        self.last_updated_ns = epoch_ns()

    # the period since the values were last updated
    @property
    def age(self):
        timestamp_ns = epoch_ns()
        elapsed_ns = timestamp_ns - self.last_updated_ns
        self.last_updated_ns = timestamp_ns
        return elapsed_ns / 1e9

    def advance(self, time):
        self.vel.x += self.acc.x * time
        self.vel.y += self.acc.y * time
        self.vel.z += self.acc.z * time

        self.pos.x += self.vel.x * time
        self.pos.y += self.vel.y * time
        self.pos.z += self.vel.z * time

        self.orientation += self.rotational_velocity * time
        self.orientation %= 2 * π
        self.orientation *= self.sap**time

        self.pos.x %= self.width
        self.pos.y %= self.height

        self.vel.x *= self.sap**time
        self.vel.y *= self.sap**time
        self.vel.z *= self.sap**time

    def apply(self):
        self.advance(self.age)

    def push(self, vector):
        player.acc.x = vector[0] * self.acc_factor
        player.acc.y = vector[1] * self.acc_factor
        self.apply()

    def push_binary(self, right, left, up, down):
        if right:
            player.acc.x = self.acc_factor
        if left:
            player.acc.x = -self.acc_factor
        if right and left:
            player.acc.x = 0
        if (not right) and (not left):
            player.acc.x = 0
        if down:
            player.acc.y = self.acc_factor
        if up:
            player.acc.y = -self.acc_factor
        if down and up:
            player.acc.y = 0
        if (not up) and (not down):
            player.acc.y = 0
        self.apply()

    def serialize(self):
        pass

    def draw(self):
        pass

    def screen_coords(self):
        return (int(self.pos.x), int(self.pos.y))


def mix(a, a_weight, b, b_weight):
    a = build_sprite(a)
    b = build_sprite(b)
    pos = vector(
        a.pos.x * a_weight + b.pos.x * b_weight,
        a.pos.y * a_weight + b.pos.y * b_weight,
        a.pos.z * a_weight + b.pos.z * b_weight,
    )
    vel = vector(
        a.vel.x * a_weight + b.vel.x * b_weight,
        a.vel.y * a_weight + b.vel.y * b_weight,
        a.vel.z * a_weight + b.vel.z * b_weight,
    )
    acc = vector(
        a.acc.x * a_weight + b.acc.x * b_weight,
        a.acc.y * a_weight + b.acc.y * b_weight,
        a.acc.z * a_weight + b.acc.z * b_weight,
    )
    return Sprite(worldspace_position=pos, velocity=vel, acceleration=acc)


def pos_sprite(pos):
    return Sprite(vector(*pos))


def build_sprite(state):
    pos = state["position"]
    vec = state["velocity"]
    acc = state["acceleration"]
    return Sprite(vector(*pos), vector(*vec), vector(*acc))


player = Sprite()
world.sprites["player"] = player
