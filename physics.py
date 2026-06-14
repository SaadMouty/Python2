import math
from vpython import mag, vector

# =========================
# CONSTANTS
# =========================
GRAVITY = 9.81
DAMPING = 0.999  # air resistance

# collision properties (Newton's cradle → near elastic)
RESTITUTION = 0.999  # 1.0 = perfectly elastic


# =========================
# INITIALIZATION
# =========================
def initialize_ball_physics(ball):
    ball["pivot"] = (
        ball["anchor_left"]
        + ball["anchor_right"]
    ) / 2

    ball["length"] = (
        ball["pivot"].y
        - ball["sphere"].pos.y
    )

    ball["mass"] = 1.0

    ball["angle"] = 0.0
    ball["angular_velocity"] = 0.0
    ball["angular_acceleration"] = 0.0

    return ball


# =========================
# PENDULUM UPDATE (per ball)
# =========================
def update_physics(ball, dt):

    # θ'' = -(g/L) sin(θ)
    ball["angular_acceleration"] = (
        -(GRAVITY / ball["length"])
        * math.sin(ball["angle"])
    )

    ball["angular_velocity"] += ball["angular_acceleration"] * dt
    ball["angular_velocity"] *= DAMPING

    ball["angle"] += ball["angular_velocity"] * dt

    # position update
    pivot = ball["pivot"]
    x = pivot.x + ball["length"] * math.sin(ball["angle"])
    y = pivot.y - ball["length"] * math.cos(ball["angle"])

    ball["sphere"].pos = vector(x, y, pivot.z)

    update_strings(ball)


# =========================
# STRING UPDATE
# =========================
def update_strings(ball):
    s = ball["sphere"]
    r = ball["radius"]

    top_offset = vector(0, r * 0.78, 0)
    lateral = vector(r * 0.45, 0, 0)

    attach_left = s.pos + top_offset - lateral
    attach_right = s.pos + top_offset + lateral

    ball["string_left"].pos = ball["anchor_left"]
    ball["string_left"].axis = attach_left - ball["anchor_left"]

    ball["string_right"].pos = ball["anchor_right"]
    ball["string_right"].axis = attach_right - ball["anchor_right"]


# =========================
# RESET
# =========================
def reset_ball(ball, angle=0.0):
    ball["angle"] = angle
    ball["angular_velocity"] = 0.0
    ball["angular_acceleration"] = 0.0

    pivot = ball["pivot"]
    x = pivot.x + ball["length"] * math.sin(ball["angle"])
    y = pivot.y - ball["length"] * math.cos(ball["angle"])

    ball["sphere"].pos = vector(x, y, pivot.z)
    update_strings(ball)


# =========================================================
# CONVERT ANGULAR → LINEAR VELOCITY
# =========================================================
def tangential_velocity(ball):
    return ball["length"] * ball["angular_velocity"]


# =========================
# ENERGY FUNCTIONS
# =========================
def kinetic_energy(ball):
    v = tangential_velocity(ball)
    return 0.5 * ball["mass"] * v * v


def potential_energy(ball):
    lowest_y = ball["anchor_left"].y - ball["length"]
    h = ball["sphere"].pos.y - lowest_y
    return ball["mass"] * GRAVITY * h


def total_energy(ball):
    return kinetic_energy(ball) + potential_energy(ball)


# =========================================================
# COLLISION SYSTEM (NEWTON'S CRADLE CORE)
# =========================================================

def check_collision(ball_a, ball_b):
    pos_a = ball_a["sphere"].pos
    pos_b = ball_b["sphere"].pos

    distance = mag(pos_a - pos_b)
    min_dist = ball_a["radius"] + ball_b["radius"]

    return distance <= min_dist


# =========================================================
# 1D ELASTIC COLLISION (simplified for cradle line)
# =========================================================
def resolve_collision(ball_a, ball_b):

    # convert angular velocity → linear velocity
    v1 = tangential_velocity(ball_a)
    v2 = tangential_velocity(ball_b)

    m1 = ball_a["mass"]
    m2 = ball_b["mass"]

    # 1D elastic collision equations
    new_v1 = (
        (m1 - m2) / (m1 + m2) * v1 +
        (2 * m2) / (m1 + m2) * v2
    )

    new_v2 = (
        (2 * m1) / (m1 + m2) * v1 +
        (m2 - m1) / (m1 + m2) * v2
    )

    # apply restitution (energy loss control)
    new_v1 *= RESTITUTION
    new_v2 *= RESTITUTION

    # convert back to angular velocity
    ball_a["angular_velocity"] = new_v1 / ball_a["length"]
    ball_b["angular_velocity"] = new_v2 / ball_b["length"]


# =========================================================
# SYSTEM UPDATE (ALL BALLS TOGETHER)
# =========================================================
def update_system(balls, dt):

    # 1. update individual pendulums
    for ball in balls:
        update_physics(ball, dt)

    # 2. collision pass (important: after movement)
    for i in range(len(balls) - 1):
        a = balls[i]                       # left ball
        b = balls[i + 1]                   # right ball

        if not check_collision(a, b):
            continue

        # Only resolve when the balls are actually approaching each other.
        # 'a' is left of 'b', so they close in when a moves right faster
        # than b (tangential velocity is +x). Without this guard the same
        # overlap is resolved every frame and the balls stick together.
        if tangential_velocity(a) > tangential_velocity(b):
            resolve_collision(a, b)