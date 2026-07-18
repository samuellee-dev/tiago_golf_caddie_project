import mujoco
import numpy as np


class DirectBaseController:
    """
    교육용 TIAGo 베이스 직접 이동 컨트롤러.

    로봇의 root free joint qpos를 직접 변경해
    x, y 평면에서 로봇을 이동시킨다.

    주의:
    이 방식은 실제 바퀴 actuator를 제어하는 방식이 아니다.
    골퍼 추종, 장애물 회피, 목표 이동 알고리즘을
    단순하게 검증하기 위한 교육용 이동 방식이다.
    """

    def __init__(
        self,
        model: mujoco.MjModel,
        joint_name: str,
    ) -> None:
        self.model = model
        self.joint_name = joint_name

        joint_id = mujoco.mj_name2id(
            model,
            mujoco.mjtObj.mjOBJ_JOINT,
            joint_name,
        )

        if joint_id == -1:
            raise ValueError(
                f"joint를 찾을 수 없습니다: {joint_name}"
            )

        if (
            model.jnt_type[joint_id]
            != mujoco.mjtJoint.mjJNT_FREE
        ):
            raise ValueError(
                f"{joint_name}은 free joint가 아닙니다."
            )

        self.qpos_addr = model.jnt_qposadr[
            joint_id
        ]

    def get_position(
        self,
        data: mujoco.MjData,
    ) -> np.ndarray:
        """
        로봇 root free joint의 현재 x, y, z 위치를 반환한다.
        """
        return data.qpos[
            self.qpos_addr:self.qpos_addr + 3
        ].copy()

    def move_xy(
        self,
        data: mujoco.MjData,
        dx: float,
        dy: float,
    ) -> None:
        """
        로봇을 현재 위치에서 x, y 방향으로 직접 이동한다.
        """
        data.qpos[self.qpos_addr + 0] += dx
        data.qpos[self.qpos_addr + 1] += dy

        mujoco.mj_forward(
            self.model,
            data,
        )

    def move_toward(
        self,
        data: mujoco.MjData,
        target_xy: np.ndarray,
        step_size: float,
    ) -> None:
        """
        현재 위치에서 target_xy 방향으로 step_size만큼 이동한다.
        """
        current_pos = self.get_position(
            data
        )

        current_xy = current_pos[:2]

        direction = (
            target_xy - current_xy
        )

        distance = np.linalg.norm(
            direction
        )

        if distance < 1e-6:
            return

        unit_direction = (
            direction / distance
        )

        dx = (
            unit_direction[0]
            * step_size
        )

        dy = (
            unit_direction[1]
            * step_size
        )

        self.move_xy(
            data,
            dx,
            dy,
        )