import numpy as np


class FollowGolferBehavior:
    """
    골퍼 target을 따라가는 기본 행동 로직.

    핵심 개념:
    - 로봇과 골퍼 사이의 거리를 계산한다.
    - 너무 멀면 골퍼 쪽으로 이동한다.
    - 적정 거리면 정지한다.
    - 너무 가까우면 정지하거나 후퇴한다.
    - 이번 단계에서는 장애물 회피를 하지 않는다.
    """

    def __init__(
        self,
        desired_distance: float = 1.5,
        tolerance: float = 0.2,
        step_size: float = 0.01,
    ):
        self.desired_distance = desired_distance
        self.tolerance = tolerance
        self.step_size = step_size

    def compute_distance(
        self,
        robot_xy: np.ndarray,
        golfer_xy: np.ndarray,
    ) -> float:
        """
        로봇과 골퍼 사이의 2D 거리 계산.
        """
        return float(np.linalg.norm(golfer_xy - robot_xy))

    def decide_action(
        self,
        robot_xy: np.ndarray,
        golfer_xy: np.ndarray,
    ) -> str:
        """
        현재 거리에 따라 행동을 결정한다.

        반환값:
        - "FOLLOW": 골퍼 쪽으로 이동
        - "STOP": 적정 거리 유지
        - "TOO_CLOSE": 너무 가까움
        """
        distance = self.compute_distance(robot_xy, golfer_xy)

        min_distance = self.desired_distance - self.tolerance
        max_distance = self.desired_distance + self.tolerance

        if distance > max_distance:
            return "FOLLOW"

        if distance < min_distance:
            return "TOO_CLOSE"

        return "STOP"

    def compute_follow_target(
        self,
        robot_xy: np.ndarray,
        golfer_xy: np.ndarray,
    ) -> np.ndarray:
        """
        로봇이 이동해야 할 목표 지점을 계산한다.

        중요한 점:
        로봇이 골퍼 위치까지 완전히 가면 안 된다.
        골퍼와 desired_distance만큼 떨어진 지점을 목표로 해야 한다.

        예:
        골퍼가 앞에 있고 로봇이 뒤에 있으면,
        골퍼 바로 뒤 desired_distance 위치까지만 이동한다.
        """
        direction = golfer_xy - robot_xy
        distance = np.linalg.norm(direction)

        if distance < 1e-6:
            return robot_xy.copy()

        unit_direction = direction / distance

        # 골퍼 위치에서 로봇 방향으로 desired_distance만큼 떨어진 지점
        target_xy = golfer_xy - unit_direction * self.desired_distance

        return target_xy
