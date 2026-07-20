import mujoco
import numpy as np


class TargetBodyController:
    """
    교육용 target body 이동 컨트롤러.

    golfer_target_free_joint를 이용해
    골퍼 target marker를 x, y 평면에서 직접 이동시킨다.
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
        target body free joint의 현재 x, y, z 위치를 반환한다.
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
        target body를 현재 위치에서 x, y 방향으로 직접 이동한다.
        """
        data.qpos[self.qpos_addr + 0] += dx
        data.qpos[self.qpos_addr + 1] += dy

        mujoco.mj_forward(
            self.model,
            data,
        )