from time import time as epoch
from time import time_ns as epoch_ns
from random import uniform

from config import config

dist = lambda x: uniform(-x, x)


class SpatialVector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class SpatialObject:
    def __init__(
        self,
        pos=None,
        vel=None,
        acc=None,
        orientation=None,
        rotational_velocity=None,
        mass=None,
        bounds=(480, 320),
    ):
        self.width, self.height = bounds
        factor = 1e2
        if not pos:
            # pos = SpatialVector()
            pos = SpatialVector(uniform(0, self.width), uniform(0, self.height), 0)
        if not vel:
            vel = SpatialVector()
            # vel = SpatialVector(dist(factor), dist(factor))
        if not acc:
            acc = SpatialVector()
            # acc = SpatialVector(dist(factor), dist(factor))
        if not orientation:
            orientation = 0
        if not rotational_velocity: rotational_velocity=0    
        if not mass: mass=0

        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.orientation = orientation
        self.rotational_velocity = rotational_velocity
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

        self.pos.x %= self.width
        self.pos.y %= self.height

        self.vel.x *= self.sap**time
        self.vel.y *= self.sap**time
        self.vel.z *= self.sap**time

    def apply(self):
        self.advance(self.age)

    def push(self, vector):
        ball.acc.x = vector[0] * self.acc_factor
        ball.acc.y = vector[1] * self.acc_factor
        self.apply()

    def push_binary(self, right, left, up, down):
        if right:
            ball.acc.x = self.acc_factor
        if left:
            ball.acc.x = -self.acc_factor
        if right and left:
            ball.acc.x = 0
        if (not right) and (not left):
            ball.acc.x = 0
        if down:
            ball.acc.y = self.acc_factor
        if up:
            ball.acc.y = -self.acc_factor
        if down and up:
            ball.acc.y = 0
        if (not up) and (not down):
            ball.acc.y = 0
        self.apply()
    def serialize(self):
        pass
    def draw(self):
        pass


def mix(a, a_weight, b, b_weight):
    a = build_ball(a)
    b = build_ball(b)
    pos = SpatialVector(
        a.pos.x * a_weight + b.pos.x * b_weight,
        a.pos.y * a_weight + b.pos.y * b_weight,
        a.pos.z * a_weight + b.pos.z * b_weight,
    )
    vel = SpatialVector(
        a.vel.x * a_weight + b.vel.x * b_weight,
        a.vel.y * a_weight + b.vel.y * b_weight,
        a.vel.z * a_weight + b.vel.z * b_weight,
    )
    acc = SpatialVector(
        a.acc.x * a_weight + b.acc.x * b_weight,
        a.acc.y * a_weight + b.acc.y * b_weight,
        a.acc.z * a_weight + b.acc.z * b_weight,
    )
    return SpatialObject(pos=pos, vel=vel, acc=acc)


def build_ball(state):
    pos = state["position"]
    vec = state["velocity"]
    acc = state["acceleration"]
    return SpatialObject(SpatialVector(*pos), SpatialVector(*vec), SpatialVector(*acc))


ball = SpatialObject()
