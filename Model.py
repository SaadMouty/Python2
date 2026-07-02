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
        "rail_y": rail_y,
        "rail_front_z": rail_front.pos.z,
        "rail_back_z": rail_back.pos.z,
        "base_h": base_h,
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
    import math
    from vpython import rate, slider, button, wtext

    from physics import (
        initialize_ball_physics,
        kinetic_energy,
        potential_energy,
        reset_ball,
        tangential_velocity,
        total_energy,
        update_system,
    )

    scene, balls = build_scene()

    # Wire each static ball from the model up to the physics engine.
    for ball in balls:
        initialize_ball_physics(ball)

    # -------------------------
    # Controls
    # -------------------------
    # "speed" is the linear release speed (m/s) given to the starting balls.
    # It is converted to angular velocity via v = L * omega.
    state = {"speed": 1.0, "release_count": 1}

    def launch(_=None):
        # Reset everything to rest, then kick the chosen number of left-side
        # balls to the right (+x, toward the group).
        for b in balls:
            reset_ball(b, angle=0.0)
        for b in balls[:state["release_count"]]:
            b["angular_velocity"] = state["speed"] / b["length"]

    def reset_all(_=None):
        for b in balls:
            reset_ball(b, angle=0.0)

    def set_speed(sl):
        state["speed"] = sl.value
        speed_readout.text = f"  Release speed: {sl.value:.2f} m/s"

    def set_release_count(sl):
        state["release_count"] = int(sl.value)
        release_count_readout.text = (
            f"  Balls released: {state['release_count']}"
        )

    scene.append_to_caption("\n\n")
    slider(min=0.0, max=3.0, value=state["speed"], step=0.05,
           length=320, bind=set_speed)
    speed_readout = wtext(text=f"  Release speed: {state['speed']:.2f} m/s")
    scene.append_to_caption("\n\n")
    slider(min=1, max=4, value=state["release_count"], step=1,
           length=320, bind=set_release_count)
    release_count_readout = wtext(
        text=f"  Balls released: {state['release_count']}"
    )
    scene.append_to_caption("\n\n")
    button(text="Release", bind=launch)
    scene.append_to_caption("    ")
    button(text="Reset", bind=reset_all)
    scene.append_to_caption("\n\n")

    stats_panel = wtext(text="")

    def update_stats():
        total_ke = sum(kinetic_energy(ball) for ball in balls)
        total_pe = sum(potential_energy(ball) for ball in balls)
        total_e = sum(total_energy(ball) for ball in balls)

        rows = [
            "Physical statistics",
            "",
            f"Total kinetic energy:   {total_ke:.5f} J",
            f"Total potential energy: {total_pe:.5f} J",
            f"Total energy:           {total_e:.5f} J",
            "",
            "Ball   angle(deg)   speed(m/s)",
        ]

        for ball in balls:
            rows.append(
                f"{ball['id']:>2}     "
                f"{math.degrees(ball['angle']):>8.2f}     "
                f"{tangential_velocity(ball):>8.3f}"
            )

        stats_panel.text = (
            "<pre style='"
            "position: fixed;"
            "right: 24px;"
            "top: 90px;"
            "z-index: 9999;"
            "margin: 0;"
            "padding: 14px 16px;"
            "width: 330px;"
            "background: #ffffff;"
            "color: #000000;"
            "border: 2px solid #000000;"
            "border-radius: 8px;"
            "font: 13px monospace;"
            "line-height: 1.35;"
            "white-space: pre;"
            "text-align: left;"
            "'>"
            + "\n".join(rows)
            + "</pre>"
        )

    # Simulation loop. A high fps keeps the near-instant collisions crisp.
    fps = 240
    dt = 1.0 / fps
    frame_count = 0
    update_stats()

    while True:
        rate(fps)
        update_system(balls, dt)
        frame_count += 1
        if frame_count % 6 == 0:
            update_stats()