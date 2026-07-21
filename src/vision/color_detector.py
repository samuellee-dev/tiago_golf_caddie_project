from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class DetectionResult:
    """
    색상 기반 검출 결과.

    center:
        이미지 좌표계 기준 중심점 (x, y)

    area:
        contour 면적

    bbox:
        bounding box (x, y, w, h)

    label:
        객체 이름
    """

    center: tuple[int, int]
    area: float
    bbox: tuple[int, int, int, int]
    label: str


class ColorObjectDetector:
    """
    OpenCV HSV 색상 범위 기반 객체 검출기.

    처리 순서:
    1. BGR 이미지를 HSV로 변환
    2. HSV 범위에 맞는 마스크 생성
    3. morphology 연산으로 노이즈 제거
    4. contour 찾기
    5. 일정 면적 이상 contour만 검출 결과로 반환
    """

    def __init__(
        self,
        label: str,
        lower_hsv: tuple[int, int, int],
        upper_hsv: tuple[int, int, int],
        min_area: float = 20.0,
    ):
        self.label = label
        self.lower_hsv = np.array(lower_hsv, dtype=np.uint8)
        self.upper_hsv = np.array(upper_hsv, dtype=np.uint8)
        self.min_area = min_area

    def create_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        """
        BGR 이미지를 입력받아 HSV 색상 범위 마스크를 만든다.
        """

        image_hsv = cv2.cvtColor(
            image_bgr,
            cv2.COLOR_BGR2HSV,
        )

        mask = cv2.inRange(
            image_hsv,
            self.lower_hsv,
            self.upper_hsv,
        )

        # 작은 노이즈 제거
        kernel = np.ones((3, 3), dtype=np.uint8)

        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1,
        )

        # 끊어진 영역을 약간 연결
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1,
        )

        return mask

    def detect(
        self,
        image_bgr: np.ndarray,
    ) -> list[DetectionResult]:
        """
        색상 범위에 해당하는 객체 후보를 검출한다.
        """

        mask = self.create_mask(image_bgr)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        results: list[DetectionResult] = []

        for contour in contours:
            area = cv2.contourArea(contour)

            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            center_x = x + w // 2
            center_y = y + h // 2

            results.append(
                DetectionResult(
                    center=(center_x, center_y),
                    area=float(area),
                    bbox=(x, y, w, h),
                    label=self.label,
                )
            )

        # 면적이 큰 객체가 먼저 오도록 정렬
        results.sort(
            key=lambda result: result.area,
            reverse=True,
        )

        return results