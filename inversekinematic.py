from omni.isaac.core.articulations import Articulation
from omni.isaac.core.utils.stage import get_current_stage
from omni.isaac.motion_generation import ArticulationKinematicsSolver
from omni.isaac.motion_generation.lula import LulaKinematicsSolver
import omni.kit.app
import omni.appwindow
import carb
import numpy as np

ROBOT_PATH = "/World/Franka"
EE_FRAME = "right_gripper"   # nếu lỗi, đổi thành "panda_hand"
STEP_POS = 0.005

robot = Articulation(ROBOT_PATH)
robot.initialize()

# Lula IK config của Franka thường có sẵn trong Isaac Sim assets/example.
# Nếu dòng này lỗi vì thiếu file config, mình sẽ đổi sang cách khác cho bản 4.5 của bạn.
kin_solver = LulaKinematicsSolver(
    robot_description_path="",
    urdf_path=""
)

articulation_solver = ArticulationKinematicsSolver(
    robot,
    kin_solver,
    EE_FRAME
)

target_pos = np.array([0.45, 0.0, 0.45])
target_ori = np.array([1.0, 0.0, 0.0, 0.0])  # quaternion w,x,y,z

pressed_keys = set()

appwindow = omni.appwindow.get_default_app_window()
keyboard = appwindow.get_keyboard()
input_interface = carb.input.acquire_input_interface()

def on_keyboard_event(event):
    key = event.input.name

    if event.type == carb.input.KeyboardEventType.KEY_PRESS:
        pressed_keys.add(key)
    elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
        pressed_keys.discard(key)

    return True

keyboard_sub = input_interface.subscribe_to_keyboard_events(
    keyboard,
    on_keyboard_event
)

def update_step(e):
    global target_pos

    moved = False

    if "W" in pressed_keys:
        target_pos[0] += STEP_POS
        moved = True
    if "S" in pressed_keys:
        target_pos[0] -= STEP_POS
        moved = True
    if "A" in pressed_keys:
        target_pos[1] += STEP_POS
        moved = True
    if "D" in pressed_keys:
        target_pos[1] -= STEP_POS
        moved = True
    if "Q" in pressed_keys:
        target_pos[2] += STEP_POS
        moved = True
    if "E" in pressed_keys:
        target_pos[2] -= STEP_POS
        moved = True

    if not moved:
        return

    action, success = articulation_solver.compute_inverse_kinematics(
        target_position=target_pos,
        target_orientation=target_ori
    )

    if success:
        robot.apply_action(action)
        print("IK target:", target_pos)
    else:
        print("IK failed:", target_pos)

update_sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
    update_step,
    name="franka_ik_keyboard_teleop"
)

print("IK teleop started")
print("W/S=X, A/D=Y, Q/E=Z")