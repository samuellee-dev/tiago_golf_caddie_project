import csv
from pathlib import Path

import cv2
import mujoco

from behavior.caddie_state_machine import (
    CaddieContext,
    CaddieState,
    CaddieStateMachine,
)
from behavior.obstacle_avoidance import (
    ObstacleAvoidanceBehavior,
)
from controller.base_controller import (
    DirectBaseController,
)
from controller.heading_controller import (
    DirectHeadingController,
)
from controller.visual_servo_controller import (
    VisualServoController,
)
from perception.obstacle_detector import (
    SimpleObstacleDetector,
)
from vision.camera_targeting import (
    CameraTargeting,
)
from vision.detect_golf_objects import (
    detect_flag,
)


# ============================================================
# 1. 프로젝트 설정
# ============================================================

XML_PATH = Path(
    "models/custom/golf_caddie_tiago/"
    "pal_tiago_dual_golf/"
    "golf_caddie_tiago_scene.xml"
)

OUTPUT_DIR = Path(
    "outputs/state_machine_vision"
)

CSV_LOG_PATH = (
    OUTPUT_DIR
    / "state_machine_vision_log.csv"
)

CAMERA_NAME = "robot_front_camera"

ROBOT_ROOT_FREE_JOINT = "reference"

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

# 15단계 Visual Servoing에서 정상 검증된 반복 수와 이동량을 유지한다.
TOTAL_STEPS = 220

FORWARD_STEP = 0.05

STOP_AREA_THRESHOLD = 5000.0

SEARCH_DELTA_YAW = 0.02

HEADING_GAIN = 0.03

HEADING_MAX_DELTA = 0.05

AVOID_STEP_SIZE = 0.03

# 현재 Scene에서는 yaw=0일 때 +y 방향이 전방이다.
FORWARD_AXIS = "y"


def draw_detections(
    image_bgr,
    detections,
):
    """
    detect_flag()가 반환한 검출 결과를 이미지에 표시한다.

    PDF 예시의 draw_detections() 역할을 현재 프로젝트의
    DetectionResult 구조에 맞춰 수행한다.
    """

    result_image = image_bgr.copy()

    for detection in detections:
        x, y, width, height = detection.bbox
        center_x, center_y = detection.center

        cv2.rectangle(
            result_image,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            2,
        )

        cv2.circle(
            result_image,
            (center_x, center_y),
            6,
            (255, 0, 0),
            -1,
        )

        label_text = (
            f"{detection.label} "
            f"area={detection.area:.1f}"
        )

        cv2.putText(
            result_image,
            label_text,
            (x, max(y - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

    return result_image


def draw_state_status(
    image_bgr,
    state: CaddieState,
    visual_command_action: str,
    target_direction: str,
    target_area: float | None,
    nearest_obstacle_distance: float,
    yaw: float,
    robot_x: float,
    robot_y: float,
) -> None:
    """
    상태머신 상태와 Visual Servoing 명령을 이미지에 표시한다.

    state:
        로봇이 현재 수행 중인 상위 행동 모드

    visual_command_action:
        현재 한 step에서 실행할 세부 제어 명령
    """

    if target_area is None:
        target_area_text = "None"
    else:
        target_area_text = f"{target_area:.1f}"

    status_text_1 = (
        f"state={state.name} "
        f"command={visual_command_action}"
    )

    status_text_2 = (
        f"direction={target_direction} "
        f"area={target_area_text} "
        f"obs_dist={nearest_obstacle_distance:.3f}"
    )

    status_text_3 = (
        f"yaw={yaw:.3f} "
        f"robot_xy=({robot_x:.3f}, {robot_y:.3f})"
    )

    cv2.putText(
        image_bgr,
        status_text_1,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        image_bgr,
        status_text_2,
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        image_bgr,
        status_text_3,
        (20, 110),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    image_center_x = IMAGE_WIDTH // 2

    cv2.line(
        image_bgr,
        (image_center_x, 0),
        (image_center_x, IMAGE_HEIGHT),
        (0, 255, 255),
        2,
    )

def main() -> None:
    """
    카메라 렌더링, 빨간 깃발 검출, Visual Servoing,
    장애물 감지와 CaddieStateMachine을 통합 테스트한다.
    """

    # --------------------------------------------------------
    # 1. 경로 확인 및 출력 폴더 생성
    # --------------------------------------------------------

    if not XML_PATH.exists():
        raise FileNotFoundError(
            f"통합 Scene XML을 찾을 수 없습니다: {XML_PATH}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # 2. MuJoCo 통합 Scene 로딩
    # --------------------------------------------------------

    print(f"[INFO] XML 로딩 시작: {XML_PATH}")

    model = mujoco.MjModel.from_xml_path(
        str(XML_PATH)
    )

    data = mujoco.MjData(model)

    mujoco.mj_forward(
        model,
        data,
    )

    print("[SUCCESS] 통합 Scene 로딩 성공")

    # --------------------------------------------------------
    # 3. robot_front_camera 확인
    # --------------------------------------------------------

    camera_id = mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_CAMERA,
        CAMERA_NAME,
    )

    if camera_id == -1:
        raise ValueError(
            f"카메라를 찾을 수 없습니다: {CAMERA_NAME}"
        )

    print(
        f"[INFO] 카메라 확인: "
        f"name={CAMERA_NAME}, id={camera_id}"
    )

    # --------------------------------------------------------
    # 4. Renderer 및 Controller 생성
    # --------------------------------------------------------

    renderer = mujoco.Renderer(
        model,
        height=IMAGE_HEIGHT,
        width=IMAGE_WIDTH,
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

    targeting = CameraTargeting(
        image_width=IMAGE_WIDTH,
        dead_zone=50,
    )

    visual_servo = VisualServoController(
        forward_step=FORWARD_STEP,
        stop_area_threshold=STOP_AREA_THRESHOLD,
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

    home_xy = (
        base_controller.get_position(
            data
        )[:2].copy()
    )

    print(
        "[INFO] Vision 통합 상태머신 테스트 시작"
    )

    print(
        f"[INFO] home_xy = {home_xy}"
    )

    print(
        f"[INFO] camera={CAMERA_NAME}, "
        f"forward_axis={FORWARD_AXIS}, "
        f"forward_step={FORWARD_STEP:.3f}, "
        f"stop_area_threshold="
        f"{STOP_AREA_THRESHOLD:.1f}"
    )

    # --------------------------------------------------------
    # 5. CSV 로그 생성
    # --------------------------------------------------------

    log_file = CSV_LOG_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    )

    writer = csv.writer(
        log_file
    )

    writer.writerow(
        [
            "step",
            "state",
            "visual_command",
            "target_detected",
            "target_direction",
            "target_area",
            "nearest_obstacle_distance",
            "yaw",
            "robot_x",
            "robot_y",
            "camera_name",
        ]
    )

    try:
        # ----------------------------------------------------
        # 6. Vision 통합 상태머신 반복
        # ----------------------------------------------------

        for step in range(TOTAL_STEPS):
            # ------------------------------------------------
            # 6-1. robot_front_camera 이미지 렌더링
            # ------------------------------------------------

            renderer.update_scene(
                data,
                camera=CAMERA_NAME,
            )

            image_rgb = renderer.render()

            image_bgr = cv2.cvtColor(
                image_rgb,
                cv2.COLOR_RGB2BGR,
            )

            # ------------------------------------------------
            # 6-2. 빨간 깃발 target 검출
            # SEARCH 상태 검증을 위해 
            # 초기 몇 step은 target을 찾지 못한 상황을 만든다.
            # ------------------------------------------------

            if step < 5:
                detections = []
            else:
                detections = detect_flag(
                    image_bgr
                )

            if detections:
                # detect_flag() 결과는 면적 내림차순으로 정렬된다.
                target_detection = detections[0]

                targeting_result = (
                    targeting.decide_from_detection(
                        target_detection.center
                    )
                )

                target_area = (
                    target_detection.area
                )

            else:
                target_detection = None

                targeting_result = (
                    targeting.decide_from_detection(
                        None
                    )
                )

                target_area = None

            # ------------------------------------------------
            # 6-3. Visual Servoing 명령 계산
            # ------------------------------------------------

            visual_command = visual_servo.decide(
                detected=targeting_result.detected,
                direction=targeting_result.direction,
                center_error_normalized=(
                    targeting_result.center_error_normalized
                ),
                target_area=target_area,
            )

            # ------------------------------------------------
            # 6-4. 로봇 위치 및 장애물 정보 수집
            # ------------------------------------------------

            robot_xy = (
                base_controller.get_position(
                    data
                )[:2]
            )

            (
                nearest_name,
                nearest_distance,
                nearest_xy,
            ) = obstacle_detector.find_nearest_obstacle(
                data=data,
                robot_xy=robot_xy,
            )

            # ------------------------------------------------
            # AVOID 상태 검증을 위해
            # 잠시 obstacle이 매우 가까운 상황을 만든다.
            # ------------------------------------------------

            if 40 <= step < 45:
                nearest_distance = 0.1

            # ------------------------------------------------
            # 6-5. 상태머신 Context 생성
            # ------------------------------------------------

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
                safety_radius=(
                    obstacle_detector.safety_radius
                ),
                target_detected=(
                    targeting_result.detected
                ),
                target_direction=(
                    targeting_result.direction
                ),
                target_center_error_normalized=(
                    targeting_result
                    .center_error_normalized
                ),
                target_area=target_area,
                visual_command_action=(
                    visual_command.action
                ),
            )

            state = state_machine.update(
                context
            )

            # ------------------------------------------------
            # 6-6. 상태별 행동 실행
            # ------------------------------------------------

            if state == CaddieState.SEARCH_TARGET:
                heading_controller.rotate_left(
                    data=data,
                    delta_yaw=SEARCH_DELTA_YAW,
                )

            elif state == CaddieState.VISION_TRACK:
                if visual_command.action == "SEARCH":
                    heading_controller.rotate_left(
                        data=data,
                        delta_yaw=SEARCH_DELTA_YAW,
                    )

                elif visual_command.action in (
                    "TURN_LEFT",
                    "TURN_RIGHT",
                ):
                    heading_controller.rotate_by_error(
                        data=data,
                        normalized_error=(
                            visual_command.yaw_error
                        ),
                        gain=HEADING_GAIN,
                        max_delta=HEADING_MAX_DELTA,
                    )

                elif visual_command.action == "MOVE_FORWARD":
                    base_controller.move_forward_by_yaw(
                        data=data,
                        yaw=(
                            heading_controller.get_yaw()
                        ),
                        step_size=(
                            visual_command.forward_step
                        ),
                        forward_axis=FORWARD_AXIS,
                    )

                elif visual_command.action == "STOP":
                    mujoco.mj_forward(
                        model,
                        data,
                    )

            elif state == CaddieState.AVOID:
                if nearest_xy is not None:
                    avoid_target_xy = (
                        obstacle_avoidance
                        .compute_avoid_target(
                            robot_xy=robot_xy,
                            obstacle_xy=nearest_xy,
                        )
                    )

                    base_controller.move_toward(
                        data=data,
                        target_xy=avoid_target_xy,
                        step_size=AVOID_STEP_SIZE,
                    )

                else:
                    mujoco.mj_forward(
                        model,
                        data,
                    )

            elif state == CaddieState.RETURN_HOME:
                base_controller.move_toward(
                    data=data,
                    target_xy=home_xy,
                    step_size=0.015,
                )

            elif state in (
                CaddieState.STOP,
                CaddieState.IDLE,
                CaddieState.TOO_CLOSE,
            ):
                mujoco.mj_forward(
                    model,
                    data,
                )

            elif state == CaddieState.EMERGENCY_STOP:
                mujoco.mj_forward(
                    model,
                    data,
                )

                print(
                    "[WARN] 긴급 정지 상태입니다."
                )

                break

            # ------------------------------------------------
            # 6-7. 물리 시뮬레이션 진행
            # ------------------------------------------------

            mujoco.mj_step(
                model,
                data,
            )

            # ------------------------------------------------
            # 6-8. 현재 상태 읽기
            # ------------------------------------------------

            robot_position = (
                base_controller.get_position(
                    data
                )
            )

            current_yaw = (
                heading_controller.get_yaw()
            )

            # ------------------------------------------------
            # 6-9. 결과 이미지 생성 및 저장
            # ------------------------------------------------

            result_image = draw_detections(
                image_bgr=image_bgr,
                detections=detections,
            )

            draw_state_status(
                image_bgr=result_image,
                state=state,
                visual_command_action=(
                    visual_command.action
                ),
                target_direction=(
                    targeting_result.direction
                ),
                target_area=target_area,
                nearest_obstacle_distance=(
                    nearest_distance
                ),
                yaw=current_yaw,
                robot_x=float(
                    robot_position[0]
                ),
                robot_y=float(
                    robot_position[1]
                ),
            )

            if step % 5 == 0:
                output_path = (
                    OUTPUT_DIR
                    / f"vision_sm_{step:04d}.png"
                )

                saved = cv2.imwrite(
                    str(output_path),
                    result_image,
                )

                if not saved:
                    raise RuntimeError(
                        "이미지 저장에 실패했습니다: "
                        f"{output_path}"
                    )

            # ------------------------------------------------
            # 6-10. CSV 로그 저장
            # ------------------------------------------------

            writer.writerow(
                [
                    step,
                    state.name,
                    visual_command.action,
                    targeting_result.detected,
                    targeting_result.direction,
                    target_area,
                    nearest_distance,
                    current_yaw,
                    float(robot_position[0]),
                    float(robot_position[1]),
                    CAMERA_NAME,
                ]
            )

            # ------------------------------------------------
            # 6-11. 터미널 로그 출력
            # ------------------------------------------------

            if target_area is None:
                target_area_text = "None"
            else:
                target_area_text = (
                    f"{target_area:.1f}"
                )

            print(
                f"step={step:03d}, "
                f"state={state.name:13s}, "
                f"camera={CAMERA_NAME}, "
                f"detected={targeting_result.detected}, "
                f"dir="
                f"{targeting_result.direction:9s}, "
                f"v_cmd="
                f"{visual_command.action:12s}, "
                f"area={target_area_text}, "
                f"nearest={nearest_name}, "
                f"obs_dist={nearest_distance:.3f}, "
                f"yaw={current_yaw:.3f}, "
                f"robot_xy="
                f"({robot_position[0]:.3f}, "
                f"{robot_position[1]:.3f})"
            )

            # ------------------------------------------------
            # 6-12. STOP 확인 후 통합 테스트 종료
            # ------------------------------------------------

            if state == CaddieState.STOP:
                print(
                    "[INFO] STOP 상태 확인: "
                    "Visual Servoing 정지 조건을 만족했습니다."
                )

                break

    finally:
        log_file.close()
        renderer.close()

    # --------------------------------------------------------
    # 7. 최종 결과 출력
    # --------------------------------------------------------

    final_robot_xy = (
        base_controller.get_position(
            data
        )[:2]
    )

    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        f"final_state = "
        f"{state_machine.state}"
    )

    print(
        f"previous_state = "
        f"{state_machine.previous_state}"
    )

    print(
        f"transition_count = "
        f"{state_machine.transition_count}"
    )

    print(
        f"final_robot_xy = "
        f"{final_robot_xy}"
    )

    print(
        f"[SUCCESS] CSV 로그 저장 완료: "
        f"{CSV_LOG_PATH}"
    )

    print(
        f"[SUCCESS] 결과 이미지 저장 위치: "
        f"{OUTPUT_DIR}"
    )

    print(
        "[SUCCESS] Vision 통합 상태머신 테스트 완료"
    )


if __name__ == "__main__":
    main()