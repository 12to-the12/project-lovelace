from time import time as epoch


class SpatialVector:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z


class SpatialObject:
    def __init__(
        self,
        pos=SpatialVector(),
        vel=SpatialVector(),
        acc=SpatialVector(),
        bounds=(1500, 1000),
    ):
        self.pos = pos
        self.vel = vel
        self.acc = acc
        self.acc_factor = 1e3

        # assert (type(self.acc.x) == int) or (type(self.acc.x) == float), type(
        #     self.acc.x
        # )
        self.width, self.height = bounds

        self.last_updated = epoch()

    # the period since the values were last updated
    @property
    def age(self):
        timestamp = epoch()
        elapsed = timestamp - self.last_updated
        self.last_updated = timestamp
        return elapsed

    def advance(self, time):
        self.vel.x += self.acc.x * time
        self.vel.y += self.acc.y * time
        self.vel.z += self.acc.z * time

        self.pos.x += self.vel.x * time
        self.pos.y += self.vel.y * time
        self.pos.z += self.vel.z * time

        self.pos.x %= self.width
        self.pos.y %= self.height

        self.vel.x *= 0.5**time
        self.vel.y *= 0.5**time
        self.vel.z *= 0.5**time

    def apply(self):
        self.advance(self.age)

    def push(self, right, left, up, down):
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


def build_ball(state):
    pos = state["position"]
    vec = state["velocity"]
    acc = state["acceleration"]
    return SpatialObject(SpatialVector(*pos), SpatialVector(*vec), SpatialVector(*acc))


ball = SpatialObject()
ball.pos.x = 5
ball.pos.y = 5
