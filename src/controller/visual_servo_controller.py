from dataclasses import dataclass


@dataclass
class VisualServoCommand:
    """
    카메라 기반 제어 명령.

    action:
        SEARCH, TURN_LEFT, TURN_RIGHT, MOVE_FORWARD, STOP

    forward_step:
        전진 이동량

    yaw_error:
        화면 중심 기준 정규화 오차

    reason:
        현재 명령을 선택한 이유
    """

    action: str
    forward_step: float
    yaw_error: float
    reason: str


class VisualServoController:
    """
    단순 Visual Servoing 정책.

    입력:
    - target 검출 여부
    - target 방향: LEFT / CENTER / RIGHT / NOT_FOUND
    - 화면 중심 오차
    - target bounding box 면적

    출력:
    - 로봇 행동 명령
    """

    def __init__(
        self,
        forward_step: float = 0.015,
        stop_area_threshold: float = 5000.0,
    ):
        self.forward_step = forward_step
        self.stop_area_threshold = stop_area_threshold

    def decide(
        self,
        detected: bool,
        direction: str,
        center_error_normalized: float,
        target_area: float | None,
    ) -> VisualServoCommand:
        # --------------------------------------------------------
        # 1. target을 찾지 못한 경우
        # --------------------------------------------------------
        if not detected:
            return VisualServoCommand(
                action="SEARCH",
                forward_step=0.0,
                yaw_error=0.0,
                reason="target not found",
            )

        # --------------------------------------------------------
        # 2. target이 너무 크게 보이면 가까운 것으로 판단하고 정지
        # --------------------------------------------------------
        if (
            target_area is not None
            and target_area >= self.stop_area_threshold
        ):
            return VisualServoCommand(
                action="STOP",
                forward_step=0.0,
                yaw_error=center_error_normalized,
                reason=f"target area too large: {target_area:.1f}",
            )

        # --------------------------------------------------------
        # 3. target이 왼쪽에 있으면 좌회전
        # --------------------------------------------------------
        if direction == "LEFT":
            return VisualServoCommand(
                action="TURN_LEFT",
                forward_step=0.0,
                yaw_error=center_error_normalized,
                reason="target is left",
            )

        # --------------------------------------------------------
        # 4. target이 오른쪽에 있으면 우회전
        # --------------------------------------------------------
        if direction == "RIGHT":
            return VisualServoCommand(
                action="TURN_RIGHT",
                forward_step=0.0,
                yaw_error=center_error_normalized,
                reason="target is right",
            )

        # --------------------------------------------------------
        # 5. target이 중앙이면 전진
        # --------------------------------------------------------
        if direction == "CENTER":
            return VisualServoCommand(
                action="MOVE_FORWARD",
                forward_step=self.forward_step,
                yaw_error=center_error_normalized,
                reason="target centered",
            )

        # --------------------------------------------------------
        # 6. 알 수 없는 상태는 안전하게 정지
        # --------------------------------------------------------
        return VisualServoCommand(
            action="STOP",
            forward_step=0.0,
            yaw_error=center_error_normalized,
            reason=f"unknown direction: {direction}",
        )