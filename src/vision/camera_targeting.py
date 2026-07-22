from dataclasses import dataclass

from vision.image_geometry import (
    estimate_horizontal_direction,
    normalize_center_error,
)


@dataclass
class CameraTargetingResult:
    """
    카메라 기반 target 방향 판단 결과.
    """

    detected: bool
    direction: str
    center_error_normalized: float
    target_center: tuple[int, int] | None


class CameraTargeting:
    """
    이미지에서 검출된 객체 중심을 이용해
    로봇이 어느 방향으로 회전해야 하는지 판단한다.
    """

    def __init__(
        self,
        image_width: int,
        dead_zone: int = 50,
    ):
        """
        Args:
            image_width:
                입력 이미지의 전체 너비

            dead_zone:
                화면 중앙에서 CENTER로 판단할 허용 범위
        """

        self.image_width = image_width
        self.dead_zone = dead_zone

    def decide_from_detection(
        self,
        target_center: tuple[int, int] | None,
    ) -> CameraTargetingResult:
        """
        검출된 target 중심 좌표를 이용해
        LEFT, CENTER, RIGHT 또는 NOT_FOUND를 판단한다.

        Args:
            target_center:
                검출된 객체 중심 좌표 (x, y)

                객체를 찾지 못한 경우 None

        Returns:
            CameraTargetingResult
        """

        if target_center is None:
            return CameraTargetingResult(
                detected=False,
                direction="NOT_FOUND",
                center_error_normalized=0.0,
                target_center=None,
            )

        center_x, _ = target_center

        direction = estimate_horizontal_direction(
            object_center_x=center_x,
            image_width=self.image_width,
            dead_zone=self.dead_zone,
        )

        normalized_error = normalize_center_error(
            object_center_x=center_x,
            image_width=self.image_width,
        )

        return CameraTargetingResult(
            detected=True,
            direction=direction,
            center_error_normalized=normalized_error,
            target_center=target_center,
        )