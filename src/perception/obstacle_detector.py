import mujoco
import numpy as np


class SimpleObstacleDetector:
    """
    MuJoCo 내부 body 좌표를 직접 읽는 교육용 장애물 감지기.

    실제 로봇에서는 LiDAR, Depth Camera, Ultrasonic Sensor 등을
    사용하지만, 초기 시뮬레이션에서는 장애물 body 위치를 직접
    읽어서 회피 알고리즘을 먼저 검증한다.
    """

    def __init__(
        self,
        model: mujoco.MjModel,
        obstacle_body_names: list[str],
        safety_radius: float = 1.0,
    ):
        self.model = model
        self.obstacle_body_names = obstacle_body_names
        self.safety_radius = safety_radius

        self.obstacle_body_ids: list[int] = []

        for name in obstacle_body_names:
            body_id = mujoco.mj_name2id(
                model,
                mujoco.mjtObj.mjOBJ_BODY,
                name,
            )

            if body_id == -1:
                raise ValueError(
                    f"장애물 body를 찾을 수 없습니다: {name}"
                )

            self.obstacle_body_ids.append(body_id)

    def get_obstacle_positions(
        self,
        data: mujoco.MjData,
    ) -> dict[str, np.ndarray]:
        """
        장애물 이름과 현재 위치를 dict 형태로 반환한다.

        반환 예:
        {
            "obstacle_tree_01": array([-1.3, -1.5, 0.35]),
            "obstacle_tree_02": array([1.4, 1.2, 0.35]),
        }
        """
        result = {}

        for name, body_id in zip(
            self.obstacle_body_names,
            self.obstacle_body_ids,
        ):
            result[name] = data.xpos[body_id].copy()

        return result

    def find_nearest_obstacle(
        self,
        data: mujoco.MjData,
        robot_xy: np.ndarray,
    ) -> tuple[str | None, float, np.ndarray | None]:
        """
        로봇과 가장 가까운 장애물을 찾는다.

        반환:
        - obstacle_name 또는 None
        - distance
        - obstacle_xy 또는 None
        """
        nearest_name = None
        nearest_distance = float("inf")
        nearest_xy = None

        positions = self.get_obstacle_positions(
            data
        )

        for name, pos in positions.items():
            obstacle_xy = pos[:2]

            distance = float(
                np.linalg.norm(
                    obstacle_xy - robot_xy
                )
            )

            if distance < nearest_distance:
                nearest_name = name
                nearest_distance = distance
                nearest_xy = obstacle_xy

        return (
            nearest_name,
            nearest_distance,
            nearest_xy,
        )

    def is_obstacle_too_close(
        self,
        data: mujoco.MjData,
        robot_xy: np.ndarray,
    ) -> bool:
        """
        가장 가까운 장애물이 safety_radius 안에 있는지 확인한다.
        """
        _, distance, _ = (
            self.find_nearest_obstacle(
                data,
                robot_xy,
            )
        )

        return distance < self.safety_radius