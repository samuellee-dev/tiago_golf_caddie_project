from pathlib import Path

import cv2
import mujoco

from controller.heading_controller import (
    DirectHeadingController,
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
    "outputs/camera_heading"
)

CAMERA_NAME = "robot_front_camera"

ROBOT_ROOT_FREE_JOINT = "reference"

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

TOTAL_STEPS = 20


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


def draw_targeting_result(
    image_bgr,
    direction: str,
    normalized_error: float,
    yaw: float,
) -> None:
    """
    카메라 방향 판단 결과와 현재 yaw를 이미지에 표시한다.
    """

    status_text = (
        f"direction={direction} "
        f"error={normalized_error:.3f} "
        f"yaw={yaw:.3f}"
    )

    cv2.putText(
        image_bgr,
        status_text,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
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


def main():
    """
    전방 카메라에서 빨간 깃발을 검출하고,
    깃발 중심의 화면 오차를 이용해 TIAGo의 yaw를 조정한다.
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
    # 2. MuJoCo 모델 로딩
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
    # 4. Renderer 및 제어 객체 생성
    # --------------------------------------------------------

    renderer = mujoco.Renderer(
        model,
        height=IMAGE_HEIGHT,
        width=IMAGE_WIDTH,
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

    print("[INFO] 카메라 기반 heading 테스트 시작")

    try:
        # ----------------------------------------------------
        # 5. 카메라 기반 heading 반복 테스트
        # ----------------------------------------------------

        for step in range(TOTAL_STEPS):
            # ------------------------------------------------
            # 5-1. 현재 전방 카메라 이미지 렌더링
            # ------------------------------------------------

            renderer.update_scene(
                data,
                camera=CAMERA_NAME,
            )

            image_rgb = renderer.render()

            # MuJoCo Renderer는 RGB,
            # 기존 OpenCV 검출 코드는 BGR을 사용한다.
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

                result = targeting.decide_from_detection(
                    largest_flag.center
                )

                draw_detection(
                    image_bgr,
                    largest_flag,
                )

            else:
                largest_flag = None

                result = targeting.decide_from_detection(
                    None
                )

            # ------------------------------------------------
            # 5-3. 검출 오차에 따른 yaw 회전
            # ------------------------------------------------

            if result.detected:
                heading_controller.rotate_by_error(
                    data=data,
                    normalized_error=(
                        result.center_error_normalized
                    ),
                    gain=0.03,
                    max_delta=0.05,
                )

            current_yaw = heading_controller.get_yaw()

            # ------------------------------------------------
            # 5-4. 판단 결과 표시
            # ------------------------------------------------

            draw_targeting_result(
                image_bgr=image_bgr,
                direction=result.direction,
                normalized_error=(
                    result.center_error_normalized
                ),
                yaw=current_yaw,
            )

            # ------------------------------------------------
            # 5-5. 결과 이미지 저장
            # ------------------------------------------------

            output_path = (
                OUTPUT_DIR
                / f"heading_step_{step:03d}.png"
            )

            saved = cv2.imwrite(
                str(output_path),
                image_bgr,
            )

            if not saved:
                raise RuntimeError(
                    f"이미지 저장에 실패했습니다: {output_path}"
                )

            # ------------------------------------------------
            # 5-6. 실행 로그 출력
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
                f"camera={CAMERA_NAME}, "
                f"detected={result.detected}, "
                f"center={flag_center_text}, "
                f"area={flag_area_text}, "
                f"direction={result.direction}, "
                f"error="
                f"{result.center_error_normalized:.3f}, "
                f"yaw={current_yaw:.3f}, "
                f"saved={output_path}"
            )

    finally:
        renderer.close()

    print("[SUCCESS] 카메라 기반 heading 테스트 완료")


if __name__ == "__main__":
    main()