# from vpython import rate

# from Python2 import Model
# from physics import update_system

# scene, balls = Model.build_scene()


# # Lift first ball
# balls[0]["angle"] = 0.6


# dt = 1 / 60


# while True:

#     rate(60)

#     update_system(balls, dt)


from vpython import sphere, cylinder, vector, rate, color

from physics import (
    initialize_ball_physics,
    update_system,
)

# =========================
# CREATE BALL SYSTEM
# =========================
balls = []

N = 5          # number of balls
spacing = 1.2  # distance between balls
radius = 0.5
length = 3.0

anchor_y = 0

for i in range(N):

    x = i * spacing

    ball = {
        "radius": radius,

        "anchor_left": vector(x, anchor_y, 0),
        "anchor_right": vector(x, anchor_y, 0),

        "sphere": sphere(
            pos=vector(x, anchor_y - length, 0),
            radius=radius,
            color=color.red if i == 0 else color.white
        ),

        "string_left": cylinder(
            pos=vector(x, anchor_y, 0),
            axis=vector(0, -length, 0),
            radius=0.02,
            color=color.white
        ),

        "string_right": cylinder(
            pos=vector(x, anchor_y, 0),
            axis=vector(0, -length, 0),
            radius=0.02,
            color=color.white
        ),
    }

    initialize_ball_physics(ball)
    balls.append(ball)

# =========================
# INITIAL IMPULSE (IMPORTANT)
# =========================
balls[0]["angular_velocity"] = 2.5

# =========================
# SIMULATION LOOP
# =========================
dt = 0.01

while True:
    rate(100)

    update_system(balls, dt)