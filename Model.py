"""
Newton's Cradle static 3D model (stand + frame + 5 balls in separate files).

Install:  py -m pip install vpython
Run:      py Model.py
"""

from vpython import (
    canvas, vector, box, cylinder, textures, distant_light, local_light
)

from ball_1 import create_ball as create_ball_1
from ball_2 import create_ball as create_ball_2
from ball_3 import create_ball as create_ball_3
from ball_4 import create_ball as create_ball_4
from ball_5 import create_ball as create_ball_5


def v(x, y, z):
    return vector(x, y, z)


def metallic_silver():
    # Use this in ball files (included here for consistency/reference)
    return vector(0.82, 0.83, 0.86)


def metallic_black():
    # Dark gunmetal; reads as metallic black in VPython with high shininess
    return vector(0.12, 0.12, 0.14)


def matte_black():
    return vector(0.08, 0.08, 0.09)


def build_scene():
    scene = canvas(
        title="Newton's Cradle (Model)",
        width=1200,
        height=720,
        background=vector(0.92, 0.91, 0.90),
        center=v(0, 0.10, 0),
        forward=v(-0.55, -0.25, -0.78),
        fov=0.75,
    )

    # Lighting (slightly tuned to read black metal + silver highlights)
    distant_light(direction=v(-0.4, -1.0, -0.6), color=vector(1.0, 1.0, 1.0))      # key
    distant_light(direction=v(0.6, -0.8, 0.2), color=vector(0.75, 0.85, 1.0))       # cool fill
    local_light(pos=v(0, 0.55, 0.35), color=vector(1.0, 0.95, 0.9))                 # warm accent

    # -------------------------
    # Dimensions
    # -------------------------
    base_w = 0.54
    base_d = 0.24
    base_h = 0.03

    leg_h = 0.34
    leg_thick = 0.02
    leg_span = base_w * 0.86

    top_w = base_w * 0.92
    top_d = 0.06
    top_h = 0.02

    rail_r = 0.0055
    rail_y = base_h + leg_h - 0.01

    # -------------------------
    # Base (wood)
    # -------------------------
    box(
        pos=v(0, base_h / 2, 0),
        size=v(base_w, base_h, base_d),
        texture=textures.wood,
        shininess=1.0,
    )

    # Feet pads (matte black rubber)
    pad_w, pad_d, pad_h = 0.06, 0.05, 0.006
    for sx in (-1, 1):
        for sz in (-1, 1):
            box(
                pos=v(
                    sx * (base_w / 2 - pad_w / 2 - 0.02),
                    pad_h / 2,
                    sz * (base_d / 2 - pad_d / 2 - 0.02),
                ),
                size=v(pad_w, pad_h, pad_d),
                color=matte_black(),
                shininess=0.05,
            )

    # -------------------------
    # Frame legs (metallic black)
    # -------------------------
    leg_color = metallic_black()
    leg_z_off = base_d * 0.30
    leg_x_off = leg_span / 2
    top_inset = 0.035

    def make_leg(x_base, z_base, x_top, z_top):
        axis = v(x_top - x_base, leg_h, z_top - z_base)
        cylinder(
            pos=v(x_base, base_h, z_base),
            axis=axis,
            radius=leg_thick / 2,
            color=leg_color,
            shininess=0.95,
        )

    # Front pair
    make_leg(-leg_x_off,  leg_z_off, -leg_x_off + top_inset,  leg_z_off * 0.25)
    make_leg( leg_x_off,  leg_z_off,  leg_x_off - top_inset,  leg_z_off * 0.25)
    # Back pair
    make_leg(-leg_x_off, -leg_z_off, -leg_x_off + top_inset, -leg_z_off * 0.25)
    make_leg( leg_x_off, -leg_z_off,  leg_x_off - top_inset, -leg_z_off * 0.25)

    # -------------------------
    # Top crossbar + rails (metallic black)
    # -------------------------
    box(
        pos=v(0, base_h + leg_h, 0),
        size=v(top_w, top_h, top_d),
        color=leg_color,
        shininess=0.95,
    )

    rail_x0 = -top_w / 2 + 0.03
    rail_x1 = top_w / 2 - 0.03
    rail_len = rail_x1 - rail_x0

    rail_front = cylinder(
        pos=v(rail_x0, rail_y, 0.018),
        axis=v(rail_len, 0, 0),
        radius=rail_r,
        color=leg_color,
        shininess=1.0,
    )
    rail_back = cylinder(
        pos=v(rail_x0, rail_y, -0.018),
        axis=v(rail_len, 0, 0),
        radius=rail_r,
        color=leg_color,
        shininess=0.98,
    )

    # -------------------------
    # Provide shared geometry to ball modules
    # -------------------------
    scene_objects = {
        "vector": vector,
        "rail_y": rail_y,
        "rail_front_z": rail_front.pos.z,
        "rail_back_z": rail_back.pos.z,
        "base_h": base_h,
        # Optional: let ball modules use a consistent silver if you choose to
        "ball_color": metallic_silver(),
    }

    # Build 5 standalone balls (each in its own file)
    balls = [
        create_ball_1(scene_objects),
        create_ball_2(scene_objects),
        create_ball_3(scene_objects),
        create_ball_4(scene_objects),
        create_ball_5(scene_objects),
    ]

    return scene, balls


if __name__ == "__main__":
    scene, balls = build_scene()

    # Keep the program alive so the VPython browser window doesn't immediately close.
    from vpython import rate
    while True:
        rate(60)