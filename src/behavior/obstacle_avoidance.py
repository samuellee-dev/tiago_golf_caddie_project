import numpy as np


class ObstacleAvoidanceBehavior:
    """
    가장 가까운 장애물을 기준으로
    회피 목표 좌표를 계산하는 행동 클래스.
    """

    def __init__(
        self,
        avoid_distance: float = 1.0,
    ):
        self.avoid_distance = avoid_distance

    def compute_avoid_target(
        self,
        robot_xy: np.ndarray,
        obstacle_xy: np.ndarray,
    ) -> np.ndarray:
        """
        장애물을 기준으로 회피 목표 좌표를 계산한다.
        """

        direction = obstacle_xy - robot_xy

        distance = np.linalg.norm(direction)

        if distance < 1e-6:
            return robot_xy.copy()

        unit_direction = direction / distance

        # 장애물 방향에 수직인 방향
        avoid_direction = np.array(
            [
                -unit_direction[1],
                unit_direction[0],
            ]
        )

        target_xy = (
            robot_xy
            + avoid_direction
            * self.avoid_distance
        )

        return target_xy

    def should_avoid(
        self,
        obstacle_distance: float,
        safety_radius: float,
    ) -> bool:
        """
        회피가 필요한지 판단한다.
        """
        return obstacle_distance < safety_radius