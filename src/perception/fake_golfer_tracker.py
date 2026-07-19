import mujoco
import numpy as np


class FakeGolferTracker:
    """
    MuJoCo 내부 body 위치를 직접 읽는 교육용 골퍼 추적기.

    실제 로봇에서는 카메라, LiDAR, GPS, UWB, YOLO 등을
    이용해 사람 위치를 추정할 수 있다.

    이번 단계에서는 golfer_target body의 위치를 직접 읽어
    추종 알고리즘을 먼저 검증한다.
    """

    def __init__(
        self,
        model: mujoco.MjModel,
        target_body_name: str = "golfer_target",
    ) -> None:
        self.model = model
        self.target_body_name = target_body_name

        self.body_id = mujoco.mj_name2id(
            model,
            mujoco.mjtObj.mjOBJ_BODY,
            target_body_name,
        )

        if self.body_id == -1:
            raise ValueError(
                "골퍼 target body를 찾을 수 없습니다: "
                f"{target_body_name}"
            )

    def get_position(
        self,
        data: mujoco.MjData,
    ) -> np.ndarray:
        """
        골퍼 target의 월드 좌표를 반환한다.

        반환 예:
        [x, y, z]
        """
        return data.xpos[
            self.body_id
        ].copy()

    def get_xy(
        self,
        data: mujoco.MjData,
    ) -> np.ndarray:
        """
        추종 제어에서 사용할 골퍼 target의 x, y 좌표를 반환한다.
        """
        return self.get_position(
            data
        )[:2]