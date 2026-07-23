from pathlib import Path

import mujoco
import numpy as np

from behavior.follow_behavior import FollowGolferBehavior
from controller.base_controller import DirectBaseController
from controller.target_controller import TargetBodyController
from perception.fake_golfer_tracker import FakeGolferTracker


ROBOT_ROOT_FREE_JOINT = "reference"
GOLFER_TARGET_FREE_JOINT = "golfer_target_free_joint"


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

    # ------------------------------------------------------------
    # 2. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    print(
        f"[INFO] XML 로딩 시작: {xml_path}"
    )

    model = mujoco.MjModel.from_xml_path(
        str(xml_path)
    )

    data = mujoco.MjData(model)

    mujoco.mj_forward(
        model,
        data,
    )

    print(
        "[SUCCESS] 통합 Scene 로딩 성공"
    )

    # ------------------------------------------------------------
    # 3. TIAGo 베이스 Controller 생성
    # ------------------------------------------------------------
    base_controller = DirectBaseController(
        model=model,
        joint_name=ROBOT_ROOT_FREE_JOINT,
    )

    # ------------------------------------------------------------
    # 4. 골퍼 Target Controller 생성
    # ------------------------------------------------------------
    target_controller = TargetBodyController(
        model=model,
        joint_name=GOLFER_TARGET_FREE_JOINT,
    )

    # ------------------------------------------------------------
    # 5. 골퍼 위치 Tracker 생성
    # ------------------------------------------------------------
    golfer_tracker = FakeGolferTracker(
        model=model,
        target_body_name="golfer_target",
    )

    # ------------------------------------------------------------
    # 6. 골퍼 추종 Behavior 생성
    # ------------------------------------------------------------
    follow_behavior = FollowGolferBehavior(
        desired_distance=1.5,
        tolerance=0.2,
        step_size=0.012,
    )

    # ------------------------------------------------------------
    # 7. 초기 상태 확인
    # ------------------------------------------------------------
    initial_robot_xy = (
        base_controller
        .get_position(data)[:2]
    )

    initial_golfer_xy = (
        golfer_tracker
        .get_xy(data)
    )

    initial_distance = (
        follow_behavior.compute_distance(
            robot_xy=initial_robot_xy,
            golfer_xy=initial_golfer_xy,
        )
    )

    print(
        "\n========== INITIAL STATE =========="
    )

    print(
        f"robot_xy        = "
        f"{initial_robot_xy}"
    )

    print(
        f"golfer_xy       = "
        f"{initial_golfer_xy}"
    )

    print(
        f"initial_distance= "
        f"{initial_distance:.3f}"
    )

    print(
        "\n[INFO] 움직이는 골퍼 target "
        "추종 테스트 시작"
    )

    # ------------------------------------------------------------
    # 8. 테스트 상태 기록
    # ------------------------------------------------------------
    follow_count = 0
    stop_count = 0
    too_close_count = 0

    # ------------------------------------------------------------
    # 9. 움직이는 골퍼 추종 반복
    # ------------------------------------------------------------
    for step in range(1000):
        # --------------------------------------------------------
        # 9-1. 골퍼 target을 천천히 +Y 방향으로 이동
        # --------------------------------------------------------
        if step % 5 == 0:
            target_controller.move_xy(
                data=data,
                dx=0.0,
                dy=0.003,
            )

        # --------------------------------------------------------
        # 9-2. 현재 로봇과 골퍼 위치 읽기
        # --------------------------------------------------------
        robot_position = (
            base_controller.get_position(
                data
            )
        )

        robot_xy = robot_position[:2]

        golfer_xy = golfer_tracker.get_xy(
            data
        )

        # --------------------------------------------------------
        # 9-3. 로봇과 골퍼 사이 거리 계산
        # --------------------------------------------------------
        distance = (
            follow_behavior.compute_distance(
                robot_xy=robot_xy,
                golfer_xy=golfer_xy,
            )
        )

        # --------------------------------------------------------
        # 9-4. 추종 행동 판단
        # --------------------------------------------------------
        action = (
            follow_behavior.decide_action(
                robot_xy=robot_xy,
                golfer_xy=golfer_xy,
            )
        )

        # --------------------------------------------------------
        # 9-5. FOLLOW 상태
        # --------------------------------------------------------
        if action == "FOLLOW":
            follow_target_xy = (
                follow_behavior.compute_follow_target(
                    robot_xy=robot_xy,
                    golfer_xy=golfer_xy,
                )
            )

            base_controller.move_toward(
                data=data,
                target_xy=follow_target_xy,
                step_size=follow_behavior.step_size,
            )

            follow_count += 1
                # --------------------------------------------------------
        # 9-6. STOP 상태
        # --------------------------------------------------------
        elif action == "STOP":
            mujoco.mj_forward(
                model,
                data,
            )

            stop_count += 1

        # --------------------------------------------------------
        # 9-7. TOO_CLOSE 상태
        # --------------------------------------------------------
        else:
            mujoco.mj_forward(
                model,
                data,
            )

            too_close_count += 1

        # --------------------------------------------------------
        # 9-8. 물리 시뮬레이션 진행
        # --------------------------------------------------------
        mujoco.mj_step(
            model,
            data,
        )

        # --------------------------------------------------------
        # 9-9. 로그 출력
        # --------------------------------------------------------
        if step % 50 == 0:
            print(
                f"step={step:04d} "
                f"robot_xy={robot_xy} "
                f"golfer_xy={golfer_xy} "
                f"distance={distance:.3f} "
                f"action={action}"
            )

    # ------------------------------------------------------------
    # 10. 최종 위치 확인
    # ------------------------------------------------------------
    final_robot_xy = (
        base_controller
        .get_position(data)[:2]
    )

    final_golfer_xy = (
        golfer_tracker
        .get_xy(data)
    )

    final_distance = (
        follow_behavior.compute_distance(
            robot_xy=final_robot_xy,
            golfer_xy=final_golfer_xy,
        )
    )

    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        f"final_robot_xy   = "
        f"{final_robot_xy}"
    )

    print(
        f"final_golfer_xy  = "
        f"{final_golfer_xy}"
    )

    print(
        f"final_distance   = "
        f"{final_distance:.3f}"
    )

    print(
        "\n========== ACTION COUNTS =========="
    )

    print(
        f"FOLLOW    = {follow_count}"
    )

    print(
        f"STOP      = {stop_count}"
    )

    print(
        f"TOO_CLOSE = {too_close_count}"
    )

    # ------------------------------------------------------------
    # 11. 성공 여부 확인
    # ------------------------------------------------------------
    min_distance = (
        follow_behavior.desired_distance
        - follow_behavior.tolerance
    )

    max_distance = (
        follow_behavior.desired_distance
        + follow_behavior.tolerance
    )

    if (
        min_distance
        <= final_distance
        <= max_distance
    ):
        print(
            "[SUCCESS] 움직이는 골퍼 target과 "
            "적정 거리를 유지했습니다."
        )
    else:
        print(
            "[WARN] 움직이는 골퍼 target과의 "
            "최종 거리가 허용 범위를 벗어났습니다."
        )


if __name__ == "__main__":
    main()