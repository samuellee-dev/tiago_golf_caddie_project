from pathlib import Path

import mujoco
import numpy as np

from behavior.follow_behavior import FollowGolferBehavior
from behavior.obstacle_avoidance import ObstacleAvoidanceBehavior
from controller.base_controller import DirectBaseController
from perception.fake_golfer_tracker import FakeGolferTracker
from perception.obstacle_detector import SimpleObstacleDetector


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

    # ------------------------------------------------------------
    # 2. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    model = mujoco.MjModel.from_xml_path(
        str(xml_path)
    )

    data = mujoco.MjData(model)

    mujoco.mj_forward(
        model,
        data,
    )

    print("[SUCCESS] 통합 Scene 로딩 성공")

    # ------------------------------------------------------------
    # 3. 베이스 Controller 생성
    # ------------------------------------------------------------
    base_controller = DirectBaseController(
        model=model,
        joint_name=ROBOT_ROOT_FREE_JOINT,
    )

    # ------------------------------------------------------------
    # 4. 골퍼 Tracker 생성
    # ------------------------------------------------------------
    golfer_tracker = FakeGolferTracker(
        model=model,
        target_body_name="golfer_target",
    )

    # ------------------------------------------------------------
    # 5. 골퍼 추종 Behavior 생성
    # ------------------------------------------------------------
    follow_behavior = FollowGolferBehavior(
        desired_distance=1.5,
        tolerance=0.2,
        step_size=0.01,
    )

    # ------------------------------------------------------------
    # 6. 장애물 Detector 생성
    # ------------------------------------------------------------
    obstacle_detector = SimpleObstacleDetector(
        model=model,
        obstacle_body_names=[
            "obstacle_tree_01",
            "obstacle_tree_02",
            "obstacle_marker_box",
        ],
        safety_radius=1.5,
    )

    # ------------------------------------------------------------
    # 7. 장애물 회피 Behavior 생성
    # ------------------------------------------------------------
    obstacle_avoidance = ObstacleAvoidanceBehavior(
        avoid_distance=1.0,
    )

    avoid_step_size = 0.02

    print("[INFO] 골퍼 추종 + 장애물 회피 테스트 시작")

    # ------------------------------------------------------------
    # 8. 테스트 상태 기록
    # ------------------------------------------------------------
    follow_count = 0
    avoid_count = 0
    stop_count = 0

    # ------------------------------------------------------------
    # 9. 추종 및 회피 반복
    # ------------------------------------------------------------
    for step in range(1200):
        robot_position = base_controller.get_position(
            data
        )

        robot_xy = robot_position[:2]

        golfer_xy = golfer_tracker.get_xy(
            data
        )

        (
            nearest_obstacle_name,
            nearest_obstacle_distance,
            nearest_obstacle_xy,
        ) = obstacle_detector.find_nearest_obstacle(
            data=data,
            robot_xy=robot_xy,
        )

        # --------------------------------------------------------
        # 9-1. 장애물 회피가 가장 높은 우선순위
        # --------------------------------------------------------
        should_avoid = (
            obstacle_avoidance.should_avoid(
                obstacle_distance=nearest_obstacle_distance,
                safety_radius=obstacle_detector.safety_radius,
            )
        )

        if (
            should_avoid
            and nearest_obstacle_xy is not None
        ):
            action = "AVOID"

            avoid_target_xy = (
                obstacle_avoidance.compute_avoid_target(
                    robot_xy=robot_xy,
                    obstacle_xy=nearest_obstacle_xy,
                )
            )

            base_controller.move_toward(
                data=data,
                target_xy=avoid_target_xy,
                step_size=avoid_step_size,
            )

            avoid_count += 1

        # --------------------------------------------------------
        # 9-2. 장애물이 안전하면 골퍼 추종
        # --------------------------------------------------------
        else:
            follow_action = (
                follow_behavior.decide_action(
                    robot_xy=robot_xy,
                    golfer_xy=golfer_xy,
                )
            )

            if follow_action == "FOLLOW":
                action = "FOLLOW"

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

            elif follow_action == "TOO_CLOSE":
                action = "STOP"
                stop_count += 1

            else:
                action = "STOP"
                stop_count += 1

        # --------------------------------------------------------
        # 9-3. 물리 시뮬레이션 진행
        # --------------------------------------------------------
        mujoco.mj_step(
            model,
            data,
        )

        # --------------------------------------------------------
        # 9-4. 로그 출력
        # --------------------------------------------------------
        if step % 50 == 0:
            distance_to_golfer = (
                follow_behavior.compute_distance(
                    robot_xy=robot_xy,
                    golfer_xy=golfer_xy,
                )
            )

            print(
                f"step={step:04d} "
                f"action={action:6s} "
                f"robot_xy={robot_xy} "
                f"golfer_distance={distance_to_golfer:.3f} "
                f"nearest={nearest_obstacle_name} "
                f"obstacle_distance="
                f"{nearest_obstacle_distance:.3f}"
            )

    # ------------------------------------------------------------
    # 10. 최종 결과 확인
    # ------------------------------------------------------------
    final_robot_xy = (
        base_controller.get_position(data)[:2]
    )

    final_golfer_xy = golfer_tracker.get_xy(
        data
    )

    final_golfer_distance = (
        follow_behavior.compute_distance(
            robot_xy=final_robot_xy,
            golfer_xy=final_golfer_xy,
        )
    )

    (
        final_obstacle_name,
        final_obstacle_distance,
        final_obstacle_xy,
    ) = obstacle_detector.find_nearest_obstacle(
        data=data,
        robot_xy=final_robot_xy,
    )

    print("\n========== FINAL RESULT ==========")

    print(
        f"final_robot_xy        = "
        f"{final_robot_xy}"
    )

    print(
        f"final_golfer_xy       = "
        f"{final_golfer_xy}"
    )

    print(
        f"final_golfer_distance = "
        f"{final_golfer_distance:.3f}"
    )

    print(
        f"nearest_obstacle      = "
        f"{final_obstacle_name}"
    )

    print(
        f"nearest_obstacle_xy   = "
        f"{final_obstacle_xy}"
    )

    print(
        f"nearest_obstacle_distance = "
        f"{final_obstacle_distance:.3f}"
    )

    print("\n========== ACTION COUNTS ==========")

    print(f"FOLLOW = {follow_count}")
    print(f"AVOID  = {avoid_count}")
    print(f"STOP   = {stop_count}")

    # ------------------------------------------------------------
    # 11. 성공 여부 확인
    # ------------------------------------------------------------
    if avoid_count > 0:
        print(
            "[SUCCESS] AVOID 상태가 실행되었습니다."
        )
    else:
        print(
            "[WARN] AVOID 상태가 실행되지 않았습니다."
        )

    if (
        follow_behavior.desired_distance
        - follow_behavior.tolerance
        <= final_golfer_distance
        <= follow_behavior.desired_distance
        + follow_behavior.tolerance
    ):
        print(
            "[SUCCESS] 골퍼와 적정 거리를 유지했습니다."
        )
    else:
        print(
            "[WARN] 골퍼와의 최종 거리가 "
            "허용 범위를 벗어났습니다."
        )


if __name__ == "__main__":
    main()