from omni.isaac.core.articulations import Articulation
from omni.isaac.motion_generation import ArticulationKinematicsSolver
from omni.isaac.motion_generation.lula import LulaKinematicsSolver

import omni.kit.app
import numpy as np
import os
import time

# =========================
# CONFIG
# =========================
ROBOT_PATH = "/World/Franka"
EE_FRAME = "panda_hand"
ISAAC_SIM_PATH = "C:/isaacsim"

robot_description_path = ISAAC_SIM_PATH + "/exts/isaacsim.robot_motion.motion_generation/motion_policy_configs/franka/rmpflow/robot_descriptor.yaml"
urdf_path = ISAAC_SIM_PATH + "/exts/isaacsim.robot_motion.motion_generation/motion_policy_configs/franka/lula_franka_gen.urdf"

# =========================
# NHẬP TỌA ĐỘ Ở ĐÂY
# đơn vị: mét
# pick  = vị trí hộp
# place = vị trí muốn đặt
# =========================
TASKS = [
    {"name": "box1", "pick": [0.35,  0.15, 0.12], "place": [0.55,  0.15, 0.12]},
    {"name": "box2", "pick": [0.35,  0.05, 0.12], "place": [0.55,  0.05, 0.12]},
    {"name": "box3", "pick": [0.35, -0.05, 0.12], "place": [0.55, -0.05, 0.12]},
    {"name": "box4", "pick": [0.35, -0.15, 0.12], "place": [0.55, -0.15, 0.12]},
]

# cao hơn hộp để robot đi an toàn
Z_ABOVE = 0.45

# độ cao khi gắp/đặt, đừng để quá thấp
Z_GRASP = 0.12
Z_PLACE = 0.12

MOVE_TOL = 0.02

GRIPPER_OPEN = 0.04
GRIPPER_CLOSE = 0.005

# =========================
# STOP OLD SCRIPT
# =========================
try:
    update_sub.unsubscribe()
except:
    pass

print("Old script stopped")

# =========================
# CHECK FILES
# =========================
if not os.path.exists(robot_description_path):
    raise FileNotFoundError(robot_description_path)

if not os.path.exists(urdf_path):
    raise FileNotFoundError(urdf_path)

# =========================
# INIT ROBOT
# =========================
robot = Articulation(ROBOT_PATH)
robot.initialize()

# đưa robot về tư thế dễ IK hơn
home_q = np.array([
    0.0,     # joint1
    -0.7,    # joint2
    0.0,     # joint3
    -2.0,    # joint4
    0.0,     # joint5
    1.6,     # joint6
    0.8,     # joint7
    0.04,    # finger left
    0.04     # finger right
])

robot.set_joint_positions(home_q)

time.sleep(0.5)

kin_solver = LulaKinematicsSolver(
    robot_description_path=robot_description_path,
    urdf_path=urdf_path
)

ik_solver = ArticulationKinematicsSolver(
    robot,
    kin_solver,
    EE_FRAME
)

# =========================
# HELPER
# =========================
def get_tcp_pos():
    pos, _ = ik_solver.compute_end_effector_pose()
    return np.array(pos)

def move_to(pos):
    action, success = ik_solver.compute_inverse_kinematics(
        target_position=np.array(pos)
    )

    if success:
        robot.apply_action(action)

    return success

def set_gripper(width):
    q = robot.get_joint_positions()

    if q is None:
        return

    q = q.copy()

    if len(q) >= 9:
        q[7] = width
        q[8] = width

    robot.set_joint_positions(q)

def reached(target):
    tcp = get_tcp_pos()
    error = np.linalg.norm(tcp - np.array(target))
    return error < MOVE_TOL

def make_points(task):
    pick = np.array(task["pick"], dtype=float)
    place = np.array(task["place"], dtype=float)

    pick_above = pick.copy()
    pick_above[2] = Z_ABOVE

    pick_down = pick.copy()
    pick_down[2] = Z_GRASP

    place_above = place.copy()
    place_above[2] = Z_ABOVE

    place_down = place.copy()
    place_down[2] = Z_PLACE

    return pick_above, pick_down, place_above, place_down

# =========================
# STATE MACHINE
# =========================
task_id = 0
phase = -1
wait_until = 0

def update_step(e):
    global task_id, phase, wait_until

    if task_id >= len(TASKS):
        print("ALL TASKS DONE")
        update_sub.unsubscribe()
        return

    now = time.time()

    if now < wait_until:
        return

    task = TASKS[task_id]
    pick_above, pick_down, place_above, place_down = make_points(task)

    # phase -1: về home trước
    if phase == -1:
        print("Go home first")
        robot.set_joint_positions(home_q)
        set_gripper(GRIPPER_OPEN)
        wait_until = now + 1.0
        phase = 0
        return

    # phase 0: mở gripper
    if phase == 0:
        print("Task:", task["name"], "open gripper")
        set_gripper(GRIPPER_OPEN)
        wait_until = now + 0.5
        phase = 1
        return

    # phase 1: đi tới trên hộp
    if phase == 1:
        success = move_to(pick_above)

        if success and reached(pick_above):
            print("Reached pick above")
            phase = 2
        return

    # phase 2: hạ xuống hộp
    if phase == 2:
        success = move_to(pick_down)

        if success and reached(pick_down):
            print("Reached pick down")
            phase = 3
        return

    # phase 3: đóng gripper
    if phase == 3:
        print("Close gripper")
        set_gripper(GRIPPER_CLOSE)
        wait_until = now + 0.8
        phase = 4
        return

    # phase 4: nhấc lên
    if phase == 4:
        success = move_to(pick_above)

        if success and reached(pick_above):
            print("Lifted")
            phase = 5
        return

    # phase 5: đi tới trên vị trí đặt
    if phase == 5:
        success = move_to(place_above)

        if success and reached(place_above):
            print("Reached place above")
            phase = 6
        return

    # phase 6: hạ xuống vị trí đặt
    if phase == 6:
        success = move_to(place_down)

        if success and reached(place_down):
            print("Reached place down")
            phase = 7
        return

    # phase 7: mở gripper
    if phase == 7:
        print("Open gripper")
        set_gripper(GRIPPER_OPEN)
        wait_until = now + 0.8
        phase = 8
        return

    # phase 8: nhấc lên
    if phase == 8:
        success = move_to(place_above)

        if success and reached(place_above):
            print("Finished:", task["name"])
            task_id += 1
            phase = 0
        return

update_sub = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(
    update_step,
    name="franka_auto_pick_place_better_pose"
)

print("Auto pick and place started")
print("Robot sẽ về home trước rồi mới gắp")
print("Bạn sửa tọa độ trong TASKS")