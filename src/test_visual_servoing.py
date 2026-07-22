from pathlib import Path

import cv2
import mujoco

from controller.base_controller import (
    DirectBaseController,
)
from controller.heading_controller import (
    DirectHeadingController,
)
from controller.visual_servo_controller import (
    VisualServoController,
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
    "outputs/visual_servoing"
)

CAMERA_NAME = "robot_front_camera"

ROBOT_ROOT_FREE_JOINT = "reference"

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

TOTAL_STEPS = 220

FORWARD_STEP = 0.05

STOP_AREA_THRESHOLD = 5000.0

SEARCH_DELTA_YAW = 0.02

HEADING_GAIN = 0.03

HEADING_MAX_DELTA = 0.05

# 현재 프로젝트에서 yaw=0일 때
# robot_front_camera가 +y 방향의 깃발을 바라보고 있으므로
# TIAGo 전진축은 "y"를 사용한다.
FORWARD_AXIS = "y"


def draw_detection(
    image_bgr,
    detection,
) -> None:
    """
    검출된 빨간 깃발 후보 하나를 이미지에 표시한다.

    표시 내용:
    - Bounding Box
    - 객체 중심점
    - label
    - contour 면적
    """

    x, y, width, height = detection.bbox
    center_x, center_y = detection.center

    cv2.rectangle(
        image_bgr,
        (x, y),
        (x + width, y + height),
        (0, 255, 0),
        2,
    )

    cv2.circle(
        image_bgr,
        (center_x, center_y),
        6,
        (255, 0, 0),
        -1,
    )

    label_text = (
        f"{detection.label} "
        f"area={detection.area:.1f}"
    )

    text_y = max(y - 10, 20)

    cv2.putText(
        image_bgr,
        label_text,
        (x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )


def draw_visual_servo_status(
    image_bgr,
    direction: str,
    normalized_error: float,
    action: str,
    yaw: float,
    robot_x: float,
    robot_y: float,
) -> None:
    """
    Visual Servoing 판단 결과를 이미지에 표시한다.
    """

    status_text_1 = (
        f"direction={direction} "
        f"error={normalized_error:.3f} "
        f"action={action}"
    )

    status_text_2 = (
        f"yaw={yaw:.3f} "
        f"robot_xy=({robot_x:.3f}, {robot_y:.3f})"
    )

    cv2.putText(
        image_bgr,
        status_text_1,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        image_bgr,
        status_text_2,
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
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
    전방 카메라 이미지에서 빨간 깃발을 검출하고,
    Visual Servoing 정책으로 TIAGo를 회전 또는 전진시킨다.
    """

    # --------------------------------------------------------
    # 1. XML 및 출력 폴더 확인
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
    # 3. robot_front_camera 존재 여부 확인
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

    visual_servo_controller = VisualServoController(
        forward_step=FORWARD_STEP,
        stop_area_threshold=STOP_AREA_THRESHOLD,
    )

    initial_position = base_controller.get_position(
        data
    )

    print(
        "[INFO] Visual Servoing 테스트 시작"
    )

    print(
        f"[INFO] initial_position="
        f"{initial_position}"
    )

    print(
        f"[INFO] forward_axis={FORWARD_AXIS}, "
        f"forward_step={FORWARD_STEP:.3f}, "
        f"stop_area_threshold="
        f"{STOP_AREA_THRESHOLD:.1f}"
    )

    stop_detected = False

    try:
        # ----------------------------------------------------
        # 5. Visual Servoing 반복 테스트
        # ----------------------------------------------------

        for step in range(TOTAL_STEPS):
            # ------------------------------------------------
            # 5-1. robot_front_camera 이미지 렌더링
            # ------------------------------------------------

            renderer.update_scene(
                data,
                camera=CAMERA_NAME,
            )

            image_rgb = renderer.render()

            # MuJoCo Renderer는 RGB 이미지를 반환하고,
            # OpenCV 검출 코드는 BGR 이미지를 사용한다.
            image_bgr = cv2.cvtColor(
                image_rgb,
                cv2.COLOR_RGB2BGR,
            )

            # ------------------------------------------------
            # 5-2. 빨간 깃발 후보 검출
            # ------------------------------------------------

            detections = detect_flag(
                image_bgr,
            )

            if detections:
                # detect_flag()는 면적이 큰 순서로 정렬한다.
                largest_flag = detections[0]

                targeting_result = (
                    targeting.decide_from_detection(
                        largest_flag.center
                    )
                )

                target_area = largest_flag.area

                draw_detection(
                    image_bgr,
                    largest_flag,
                )

            else:
                largest_flag = None

                targeting_result = (
                    targeting.decide_from_detection(
                        None
                    )
                )

                target_area = None

            # ------------------------------------------------
            # 5-3. Visual Servoing 행동 결정
            # ------------------------------------------------

            command = visual_servo_controller.decide(
                detected=targeting_result.detected,
                direction=targeting_result.direction,
                center_error_normalized=(
                    targeting_result.center_error_normalized
                ),
                target_area=target_area,
            )

            # ------------------------------------------------
            # 5-4. 결정된 행동 실행
            # ------------------------------------------------

            if command.action == "SEARCH":
                # target을 찾지 못한 경우
                # 제자리에서 천천히 왼쪽으로 탐색 회전한다.
                heading_controller.rotate_left(
                    data=data,
                    delta_yaw=SEARCH_DELTA_YAW,
                )

            elif command.action in (
                "TURN_LEFT",
                "TURN_RIGHT",
            ):
                # 화면 중심 오차의 부호를 이용해
                # 왼쪽 또는 오른쪽으로 yaw를 보정한다.
                heading_controller.rotate_by_error(
                    data=data,
                    normalized_error=command.yaw_error,
                    gain=HEADING_GAIN,
                    max_delta=HEADING_MAX_DELTA,
                )

            elif command.action == "MOVE_FORWARD":
                # target이 화면 중앙에 들어오면
                # 현재 yaw 방향으로 전진한다.
                current_yaw = (
                    heading_controller.get_yaw()
                )

                base_controller.move_forward_by_yaw(
                    data=data,
                    yaw=current_yaw,
                    step_size=command.forward_step,
                    forward_axis=FORWARD_AXIS,
                )

            elif command.action == "STOP":
                # target이 충분히 크게 보이면
                # 가까워진 것으로 판단하고 정지한다.
                stop_detected = True

            else:
                raise ValueError(
                    f"지원하지 않는 action입니다: "
                    f"{command.action}"
                )

            # ------------------------------------------------
            # 5-5. 현재 상태 읽기
            # ------------------------------------------------

            current_yaw = (
                heading_controller.get_yaw()
            )

            robot_position = (
                base_controller.get_position(
                    data
                )
            )

            # ------------------------------------------------
            # 5-6. 결과 이미지에 상태 표시
            # ------------------------------------------------

            draw_visual_servo_status(
                image_bgr=image_bgr,
                direction=targeting_result.direction,
                normalized_error=(
                    targeting_result.center_error_normalized
                ),
                action=command.action,
                yaw=current_yaw,
                robot_x=float(robot_position[0]),
                robot_y=float(robot_position[1]),
            )

            # ------------------------------------------------
            # 5-7. 결과 이미지 저장
            # ------------------------------------------------

            output_path = (
                OUTPUT_DIR
                / f"visual_servo_step_{step:03d}.png"
            )

            saved = cv2.imwrite(
                str(output_path),
                image_bgr,
            )

            if not saved:
                raise RuntimeError(
                    f"이미지 저장에 실패했습니다: "
                    f"{output_path}"
                )

            # ------------------------------------------------
            # 5-8. 실행 로그 출력
            # ------------------------------------------------

            if largest_flag is None:
                flag_center_text = "None"
                flag_area_text = "None"
            else:
                flag_center_text = str(
                    largest_flag.center
                )

                flag_area_text = (
                    f"{largest_flag.area:.1f}"
                )

            print(
                f"step={step:03d}, "
                f"detected={targeting_result.detected}, "
                f"center={flag_center_text}, "
                f"area={flag_area_text}, "
                f"direction={targeting_result.direction}, "
                f"error="
                f"{targeting_result.center_error_normalized:.3f}, "
                f"action={command.action}, "
                f"yaw={current_yaw:.3f}, "
                f"robot_xy="
                f"({robot_position[0]:.3f}, "
                f"{robot_position[1]:.3f}), "
                f"reason={command.reason}, "
                f"saved={output_path}"
            )

            # ------------------------------------------------
            # 5-9. STOP 확인 후 반복 종료
            # ------------------------------------------------

            if stop_detected:
                print(
                    "[INFO] STOP 조건 확인: "
                    "target area가 기준 이상입니다."
                )
                break

    finally:
        renderer.close()

    # --------------------------------------------------------
    # 6. 최종 결과 출력
    # --------------------------------------------------------

    final_position = base_controller.get_position(
        data
    )

    print("\n========== VISUAL SERVO RESULT ==========")

    print(
        "initial_position :",
        initial_position,
    )

    print(
        "final_position   :",
        final_position,
    )

    print(
        "final_yaw        :",
        heading_controller.get_yaw(),
    )

    print(
        "stop_detected    :",
        stop_detected,
    )

    if stop_detected:
        print(
            "[SUCCESS] Visual Servoing STOP 조건 확인"
        )
    else:
        print(
            "[WARN] TOTAL_STEPS 안에서 "
            "STOP 조건에 도달하지 못했습니다."
        )

    print(
        "[SUCCESS] Visual Servoing 테스트 완료"
    )


if __name__ == "__main__":
    main()