import cv2
import numpy as np

from vision.color_detector import (
    ColorObjectDetector,
    DetectionResult,
)


# ============================================================
# 1. 흰색 골프공 검출기
# ============================================================
# 흰색은 HSV에서 다음 특징을 가진다.
# - 채도 S가 낮다.
# - 밝기 V가 높다.
GOLF_BALL_DETECTOR = ColorObjectDetector(
    label="golf_ball",
    lower_hsv=(0, 0, 180),
    upper_hsv=(179, 80, 255),
    min_area=5.0,
)


# ============================================================
# 2. 빨간 깃발 검출기
# ============================================================
# OpenCV HSV의 Hue 범위는 0~179이다.
#
# 빨간색은 Hue 경계의 양쪽에 걸쳐 있으므로
# 다음 두 범위를 각각 검사해야 한다.
#
# 첫 번째 범위: 0~10
# 두 번째 범위: 170~179
FLAG_RED_LOW_DETECTOR = ColorObjectDetector(
    label="flag",
    lower_hsv=(0, 100, 100),
    upper_hsv=(10, 255, 255),
    min_area=20.0,
)

FLAG_RED_HIGH_DETECTOR = ColorObjectDetector(
    label="flag",
    lower_hsv=(170, 100, 100),
    upper_hsv=(179, 255, 255),
    min_area=20.0,
)


def create_golf_ball_mask(
    image_bgr: np.ndarray,
) -> np.ndarray:
    """
    흰색 골프공 후보 마스크를 생성한다.
    """

    return GOLF_BALL_DETECTOR.create_mask(image_bgr)


def detect_golf_ball(
    image_bgr: np.ndarray,
) -> list[DetectionResult]:
    """
    이미지에서 흰색 골프공 후보를 검출한다.
    """

    return GOLF_BALL_DETECTOR.detect(image_bgr)


def create_flag_mask(
    image_bgr: np.ndarray,
) -> np.ndarray:
    """
    빨간색 두 HSV 범위의 마스크를 결합해
    깃발 후보 마스크를 생성한다.
    """

    low_mask = FLAG_RED_LOW_DETECTOR.create_mask(image_bgr)
    high_mask = FLAG_RED_HIGH_DETECTOR.create_mask(image_bgr)

    combined_mask = cv2.bitwise_or(
        low_mask,
        high_mask,
    )

    return combined_mask


def detect_flag(
    image_bgr: np.ndarray,
) -> list[DetectionResult]:
    """
    이미지에서 빨간 깃발 후보를 검출한다.

    두 빨간색 범위에서 얻은 결과를 합친 뒤
    면적이 큰 순서로 정렬한다.
    """

    low_results = FLAG_RED_LOW_DETECTOR.detect(image_bgr)
    high_results = FLAG_RED_HIGH_DETECTOR.detect(image_bgr)

    results = low_results + high_results

    results.sort(
        key=lambda result: result.area,
        reverse=True,
    )

    return results