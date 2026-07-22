import math

import mujoco
import numpy as np


class DirectHeadingController:
    """
    교육용 단순 heading 제어기.

    주의:
    - 실제 바퀴 회전 제어가 아니다.
    - free joint의 quaternion을 직접 수정한다.
    - 카메라 기반 방향 판단 알고리즘을 이해하기 위한 실습용이다.
    """

    def __init__(
        self,
        model: mujoco.MjModel,
        joint_name: str,
        initial_yaw: float = 0.0,
    ):
        """
        Args:
            model:
                로딩된 MuJoCo 모델

            joint_name:
                TIAGo root free joint 이름

            initial_yaw:
                제어기가 관리할 초기 yaw 각도
        """

        self.model = model
        self.joint_name = joint_name
        self.yaw = initial_yaw

        joint_id = mujoco.mj_name2id(
            model,
            mujoco.mjtObj.mjOBJ_JOINT,
            joint_name,
        )

        if joint_id == -1:
            raise ValueError(
                f"joint를 찾을 수 없습니다: {joint_name}"
            )

        if model.jnt_type[joint_id] != mujoco.mjtJoint.mjJNT_FREE:
            raise ValueError(
                f"{joint_name}은 free joint가 아닙니다."
            )

        self.qpos_addr = model.jnt_qposadr[joint_id]

    def _set_yaw(
        self,
        data: mujoco.MjData,
        yaw: float,
    ) -> None:
        """
        yaw 값을 quaternion으로 변환하여
        free joint qpos에 반영한다.
        """

        self.yaw = yaw

        qw = math.cos(yaw / 2.0)
        qx = 0.0
        qy = 0.0
        qz = math.sin(yaw / 2.0)

        data.qpos[self.qpos_addr + 3] = qw
        data.qpos[self.qpos_addr + 4] = qx
        data.qpos[self.qpos_addr + 5] = qy
        data.qpos[self.qpos_addr + 6] = qz

        mujoco.mj_forward(self.model, data)

    def rotate_left(
        self,
        data: mujoco.MjData,
        delta_yaw: float = 0.02,
    ) -> None:
        """
        왼쪽으로 회전한다.
        """

        self._set_yaw(
            data,
            self.yaw + delta_yaw,
        )

    def rotate_right(
        self,
        data: mujoco.MjData,
        delta_yaw: float = 0.02,
    ) -> None:
        """
        오른쪽으로 회전한다.
        """

        self._set_yaw(
            data,
            self.yaw - delta_yaw,
        )

    def rotate_by_error(
        self,
        data: mujoco.MjData,
        normalized_error: float,
        gain: float = 0.03,
        max_delta: float = 0.05,
    ) -> None:
        """
        화면 중앙 오차를 이용해 yaw를 조정한다.

        normalized_error:
        - 음수: target이 화면 왼쪽
        - 양수: target이 화면 오른쪽

        카메라 화면 기준:
        - target이 왼쪽이면 로봇은 왼쪽으로 돌아야 한다.
        - target이 오른쪽이면 로봇은 오른쪽으로 돌아야 한다.
        """

        delta = normalized_error * gain

        delta = float(
            np.clip(
                delta,
                -max_delta,
                max_delta,
            )
        )

        self._set_yaw(
            data,
            self.yaw - delta,
        )

    def get_yaw(self) -> float:
        """
        현재 제어기가 관리하는 yaw 값을 반환한다.
        """

        return float(self.yaw)