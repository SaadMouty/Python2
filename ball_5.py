from vpython import sphere, cylinder, vector


def create_ball(scene_objects):
    rail_y = scene_objects["rail_y"]
    rail_front_z = scene_objects["rail_front_z"]
    rail_back_z = scene_objects["rail_back_z"]

    ball_r = 0.035
    gap = ball_r * 0.06
    spacing = 2 * ball_r + gap

    num_balls = 5
    total_w = (num_balls - 1) * spacing
    x0 = -total_w / 2

    idx = 5
    x = x0 + (idx - 1) * spacing
    ball_center_y = scene_objects["base_h"] + 0.12

    ball_color = vector(0.72, 0.72, 0.75)

    s = sphere(
        pos=vector(x, ball_center_y, 0),
        radius=ball_r,
        color=ball_color,
        shininess=0.95,
    )

    string_r = 0.0013
    anchor_dx = ball_r * 0.60
    anchor_left = vector(x - anchor_dx, rail_y, rail_front_z)
    anchor_right = vector(x + anchor_dx, rail_y, rail_back_z)

    top_offset = vector(0, ball_r * 0.78, 0)
    lateral = vector(ball_r * 0.45, 0, 0)
    attach_left = s.pos + top_offset - lateral
    attach_right = s.pos + top_offset + lateral

    string_color = vector(0.08, 0.08, 0.09)

    c1 = cylinder(
        pos=anchor_left,
        axis=attach_left - anchor_left,
        radius=string_r,
        color=string_color,
        shininess=0.1,
    )
    c2 = cylinder(
        pos=anchor_right,
        axis=attach_right - anchor_right,
        radius=string_r,
        color=string_color,
        shininess=0.1,
    )

    return {
        "id": idx,
        "sphere": s,
        "string_left": c1,
        "string_right": c2,
        "anchor_left": anchor_left,
        "anchor_right": anchor_right,
        "attach_left": attach_left,
        "attach_right": attach_right,
        "radius": ball_r,
        # physics properties (to be updated later)
        "mass": 1.0,
        "length": rail_y - ball_center_y,
        "angle": 0.0,
        "angular_velocity": 0.0,
        "angular_acceleration": 0.0,
    }
