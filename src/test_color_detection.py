from pathlib import Path

import cv2

from vision.detect_golf_objects import (
    create_flag_mask,
    create_golf_ball_mask,
    detect_flag,
    detect_golf_ball,
)


# ============================================================
# 1. 입력 및 출력 경로
# ============================================================
INPUT_IMAGE_PATH = Path(
    "outputs/camera/single_frame.png"
)

OUTPUT_DIR = Path(
    "outputs/vision"
)

GOLF_BALL_MASK_PATH = OUTPUT_DIR / "golf_ball_mask.png"
FLAG_MASK_PATH = OUTPUT_DIR / "flag_mask.png"
DETECTION_RESULT_PATH = OUTPUT_DIR / "detection_result.png"


def draw_detection(
    image,
    detection,
    box_color: tuple[int, int, int],
) -> None:
    """
    검출 결과를 이미지 위에 표시한다.

    box_color는 OpenCV BGR 순서이다.
    """

    x, y, w, h = detection.bbox
    center_x, center_y = detection.center

    cv2.rectangle(
        image,
        (x, y),
        (x + w, y + h),
        box_color,
        2,
    )

    cv2.circle(
        image,
        (center_x, center_y),
        4,
        box_color,
        -1,
    )

    label_text = (
        f"{detection.label} "
        f"area={detection.area:.1f}"
    )

    cv2.putText(
        image,
        label_text,
        (x, max(y - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        box_color,
        1,
        cv2.LINE_AA,
    )


def print_detection_results(
    title: str,
    detections,
) -> None:
    """
    검출 결과의 center, area, bbox를 출력한다.
    """

    print(f"\n========== {title} ==========")

    if not detections:
        print("[INFO] 검출된 객체가 없습니다.")
        return

    for index, detection in enumerate(detections):
        print(
            f"[{index}] "
            f"label={detection.label}, "
            f"center={detection.center}, "
            f"area={detection.area:.1f}, "
            f"bbox={detection.bbox}"
        )


def main():
    # ========================================================
    # 1. 입력 이미지 존재 확인
    # ========================================================
    if not INPUT_IMAGE_PATH.exists():
        raise FileNotFoundError(
            "입력 이미지를 찾을 수 없습니다:\n"
            f"{INPUT_IMAGE_PATH}\n"
            "먼저 src/render_single_frame.py를 실행하세요."
        )

    # ========================================================
    # 2. 출력 폴더 확인
    # ========================================================
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 3. OpenCV로 이미지 읽기
    # ========================================================
    image_bgr = cv2.imread(
        str(INPUT_IMAGE_PATH)
    )

    if image_bgr is None:
        raise RuntimeError(
            "OpenCV가 입력 이미지를 읽지 못했습니다:\n"
            f"{INPUT_IMAGE_PATH}"
        )

    height, width, channels = image_bgr.shape

    print("[SUCCESS] 입력 이미지 읽기 성공")
    print(f"image_path = {INPUT_IMAGE_PATH}")
    print(
        f"image_shape = "
        f"({height}, {width}, {channels})"
    )

    # 원본을 보존하기 위해 복사본에 검출 결과를 표시한다.
    result_image = image_bgr.copy()

    # ========================================================
    # 4. 골프공 및 깃발 마스크 생성
    # ========================================================
    golf_ball_mask = create_golf_ball_mask(
        image_bgr
    )

    flag_mask = create_flag_mask(
        image_bgr
    )

    # ========================================================
    # 5. 골프공 및 깃발 검출
    # ========================================================
    golf_ball_detections = detect_golf_ball(
        image_bgr
    )

    flag_detections = detect_flag(
        image_bgr
    )

    # ========================================================
    # 6. 검출 결과 로그 출력
    # ========================================================
    print_detection_results(
        "GOLF BALL DETECTIONS",
        golf_ball_detections,
    )

    print_detection_results(
        "FLAG DETECTIONS",
        flag_detections,
    )

    # ========================================================
    # 7. 검출 결과 이미지에 표시
    # ========================================================
    # 골프공: 파란색 BGR
    for detection in golf_ball_detections:
        draw_detection(
            result_image,
            detection,
            box_color=(255, 0, 0),
        )

    # 깃발: 빨간색 BGR
    for detection in flag_detections:
        draw_detection(
            result_image,
            detection,
            box_color=(0, 0, 255),
        )

    # ========================================================
    # 8. 결과 이미지 저장
    # ========================================================
    golf_ball_mask_saved = cv2.imwrite(
        str(GOLF_BALL_MASK_PATH),
        golf_ball_mask,
    )

    flag_mask_saved = cv2.imwrite(
        str(FLAG_MASK_PATH),
        flag_mask,
    )

    detection_result_saved = cv2.imwrite(
        str(DETECTION_RESULT_PATH),
        result_image,
    )

    if not golf_ball_mask_saved:
        raise RuntimeError(
            "골프공 마스크 저장에 실패했습니다:\n"
            f"{GOLF_BALL_MASK_PATH}"
        )

    if not flag_mask_saved:
        raise RuntimeError(
            "깃발 마스크 저장에 실패했습니다:\n"
            f"{FLAG_MASK_PATH}"
        )

    if not detection_result_saved:
        raise RuntimeError(
            "검출 결과 이미지 저장에 실패했습니다:\n"
            f"{DETECTION_RESULT_PATH}"
        )

    print("\n========== OUTPUT FILES ==========")
    print(
        f"[SUCCESS] 골프공 마스크 저장: "
        f"{GOLF_BALL_MASK_PATH}"
    )
    print(
        f"[SUCCESS] 깃발 마스크 저장: "
        f"{FLAG_MASK_PATH}"
    )
    print(
        f"[SUCCESS] 검출 결과 저장: "
        f"{DETECTION_RESULT_PATH}"
    )


if __name__ == "__main__":
    main()