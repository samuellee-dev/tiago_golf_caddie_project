from pathlib import Path

import mujoco
import numpy as np

from controller.base_controller import DirectBaseController
from perception.fake_golfer_tracker import FakeGolferTracker
from behavior.follow_behavior import FollowGolferBehavior


ROBOT_ROOT_FREE_JOINT = "reference"


def main() -> None:
    # ------------------------------------------------------------
    # 1. 통합 Scene XML 경로
    # ------------------------------------------------------------
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {xml_path}"
        )

    print(f"[INFO] XML 로딩 시작: {xml_path}")

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    mujoco.mj_forward(model, data)

    print("[SUCCESS] 통합 Scene 로딩 성공")

    # ------------------------------------------------------------
    # 2. Controller
    # ------------------------------------------------------------
    base_controller = DirectBaseController(
        model=model,
        joint_name=ROBOT_ROOT_FREE_JOINT,
    )

    # ------------------------------------------------------------
    # 3. Tracker
    # ------------------------------------------------------------
    golfer_tracker = FakeGolferTracker(
        model=model,
        target_body_name="golfer_target",
    )

    # ------------------------------------------------------------
    # 4. Follow Behavior
    # ------------------------------------------------------------
    follow_behavior = FollowGolferBehavior(
        desired_distance=1.5,
        tolerance=0.2,
        step_size=0.01,
    )

    print("[INFO] 골퍼 추종 테스트 시작")

    # ------------------------------------------------------------
    # 5. Follow Loop
    # ------------------------------------------------------------
    for step in range(600):

        robot_xy = (
            base_controller
            .get_position(data)[:2]
        )

        golfer_xy = golfer_tracker.get_xy(data)

        distance = (
            follow_behavior.compute_distance(
                robot_xy,
                golfer_xy,
            )
        )

        action = (
            follow_behavior.decide_action(
                robot_xy,
                golfer_xy,
            )
        )

        if action == "FOLLOW":

            target_xy = (
                follow_behavior.compute_follow_target(
                    robot_xy,
                    golfer_xy,
                )
            )

            base_controller.move_toward(
                data=data,
                target_xy=target_xy,
                step_size=follow_behavior.step_size,
            )

        mujoco.mj_step(model, data)

        if step % 50 == 0:
            print(
                f"step={step:03d} "
                f"robot={robot_xy} "
                f"golfer={golfer_xy} "
                f"distance={distance:.3f} "
                f"action={action}"
            )

    final_robot = (
        base_controller
        .get_position(data)[:2]
    )

    final_golfer = golfer_tracker.get_xy(data)

    final_distance = np.linalg.norm(
        final_golfer - final_robot
    )

    print("\n========== RESULT ==========")

    print("robot  :", final_robot)
    print("golfer :", final_golfer)
    print("distance :", final_distance)


if __name__ == "__main__":
    main()