from pathlib import Path

import cv2
import mujoco

from controller.base_controller import DirectBaseController
from controller.heading_controller import DirectHeadingController
from controller.visual_servo_controller import VisualServoController
from behavior.caddie_state_machine import (
    CaddieContext,
    CaddieState,
    CaddieStateMachine,
)
from behavior.obstacle_avoidance import ObstacleAvoidanceBehavior
from perception.obstacle_detector import SimpleObstacleDetector
from vision.camera_targeting import CameraTargeting
from vision.detect_golf_objects import detect_flag


ROBOT_ROOT_FREE_JOINT = "reference"


def main():
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    output_dir = Path("outputs/final_demo")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {xml_path}"
        )

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)

    renderer = mujoco.Renderer(
        model,
        height=720,
        width=1280,
    )

    base_controller = DirectBaseController(
        model=model,
        joint_name=ROBOT_ROOT_FREE_JOINT,
    )

    heading_controller = DirectHeadingController(
        model=model,
        joint_name=ROBOT_ROOT_FREE_JOINT,
        initial_yaw=0.0,
    )

    visual_servo = VisualServoController(
        forward_step=0.015,
        stop_area_threshold=5000.0,
    )

    targeting = CameraTargeting(
        image_width=1280,
        dead_zone=60,
    )

    obstacle_detector = SimpleObstacleDetector(
        model=model,
        obstacle_body_names=[
            "obstacle_tree_01",
            "obstacle_tree_02",
            "obstacle_marker_box",
        ],
        safety_radius=1.0,
    )

    obstacle_avoidance = ObstacleAvoidanceBehavior(
    avoid_distance=1.0,
    )

    state_machine = CaddieStateMachine()

    home_xy = base_controller.get_position(data)[:2].copy()

    print("[INFO] Golf Caddie Robot Final Demo Start")
    print(f"[INFO] home_xy = {home_xy}")

    for step in range(150):
        camera_name = "robot_front_camera"

        try:
            renderer.update_scene(
                data,
                camera=camera_name,
            )
        except Exception:
            camera_name = "golf_overview_camera"
            renderer.update_scene(
                data,
                camera=camera_name,
            )

        image_rgb = renderer.render()
        image_bgr = cv2.cvtColor(
            image_rgb,
            cv2.COLOR_RGB2BGR,
        )

        detections = detect_flag(image_bgr)

        if not detections:
            target_detection = None
            targeting_result = targeting.decide_from_detection(None)
            target_area = None
        else:
            target_detection = detections[0]
            targeting_result = targeting.decide_from_detection(
                target_detection.center
            )
            target_area = target_detection.area

        visual_command = visual_servo.decide(
            detected=targeting_result.detected,
            direction=targeting_result.direction,
            center_error_normalized=(
                targeting_result.center_error_normalized
            ),
            target_area=target_area,
        )

        robot_xy = base_controller.get_position(data)[:2]

        (
            nearest_name,
            nearest_distance,
            nearest_xy,
        ) = obstacle_detector.find_nearest_obstacle(
            data=data,
            robot_xy=robot_xy,
        )

        context = CaddieContext(
            start_follow=False,
            start_vision_tracking=True,
            return_home=False,
            emergency_stop=False,
            robot_xy=robot_xy,
            golfer_xy=None,
            home_xy=home_xy,
            distance_to_golfer=None,
            nearest_obstacle_name=nearest_name,
            nearest_obstacle_distance=nearest_distance,
            nearest_obstacle_xy=nearest_xy,
            desired_distance=1.5,
            tolerance=0.2,
            safety_radius=obstacle_detector.safety_radius,
            target_detected=targeting_result.detected,
            target_direction=targeting_result.direction,
            target_center_error_normalized=(
                targeting_result.center_error_normalized
            ),
            target_area=target_area,
            visual_command_action=visual_command.action,
        )

        state = state_machine.update(context)

        if state == CaddieState.SEARCH_TARGET:
            heading_controller.rotate_left(
                data=data,
                delta_yaw=0.02,
            )

        elif state == CaddieState.VISION_TRACK:
            if visual_command.action == "SEARCH":
                heading_controller.rotate_left(
                    data=data,
                    delta_yaw=0.02,
                )

            elif visual_command.action in [
                "TURN_LEFT",
                "TURN_RIGHT",
            ]:
                heading_controller.rotate_by_error(
                    data=data,
                    normalized_error=visual_command.yaw_error,
                    gain=0.025,
                    max_delta=0.04,
                )

            elif visual_command.action == "MOVE_FORWARD":
                base_controller.move_forward_by_yaw(
                    data=data,
                    yaw=heading_controller.get_yaw(),
                    step_size=visual_command.forward_step,
                    forward_axis="y",
                )

            elif visual_command.action == "STOP":
                mujoco.mj_forward(model, data)

        elif state == CaddieState.AVOID:
            if nearest_xy is not None:
                avoid_target_xy = (
                    obstacle_avoidance.compute_avoid_target(
                        robot_xy=robot_xy,
                        obstacle_xy=nearest_xy,
                    )
                )

                base_controller.move_toward(
                    data=data,
                    target_xy=avoid_target_xy,
                    step_size=0.03,
                )
            else:
                mujoco.mj_forward(model, data)

        elif state == CaddieState.RETURN_HOME:
            base_controller.move_toward(
                data=data,
                target_xy=home_xy,
                step_size=0.015,
            )

        else:
            mujoco.mj_forward(model, data)

        if step % 5 == 0:
            cv2.imwrite(
                str(
                    output_dir
                    / f"final_demo_{step:04d}.png"
                ),
        image_bgr,
    )

        robot_pos = base_controller.get_position(data)

        print(
            f"step={step:03d}, "
            f"state={state.name:13s}, "
            f"cmd={visual_command.action:12s}, "
            f"detected={targeting_result.detected}, "
            f"dir={targeting_result.direction:9s}, "
            f"area={target_area}, "
            f"obs={nearest_distance:.3f}, "
            f"yaw={heading_controller.get_yaw():.3f}, "
            f"robot_xy=("
            f"{robot_pos[0]:.3f}, "
            f"{robot_pos[1]:.3f})"
        )

    print(
        "[SUCCESS] "
        "Golf Caddie Robot Final Demo Complete"
    )
    print(f"[INFO] output images: {output_dir}")


if __name__ == "__main__":
    main()