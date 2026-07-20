from pathlib import Path

import mujoco
import numpy as np

from behavior.caddie_state_machine import (
    CaddieContext,
    CaddieState,
    CaddieStateMachine,
)
from behavior.follow_behavior import FollowGolferBehavior
from behavior.obstacle_avoidance import (
    ObstacleAvoidanceBehavior,
)
from controller.base_controller import DirectBaseController
from controller.target_controller import TargetBodyController
from perception.fake_golfer_tracker import FakeGolferTracker
from perception.obstacle_detector import SimpleObstacleDetector


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
        step_size=0.01,
    )

    # ------------------------------------------------------------
    # 7. 장애물 Detector 생성
    # ------------------------------------------------------------
    obstacle_detector = SimpleObstacleDetector(
        model=model,
        obstacle_body_names=[
            "obstacle_tree_01",
            "obstacle_tree_02",
            "obstacle_marker_box",
        ],
        safety_radius=1.0,
    )

    # ------------------------------------------------------------
    # 8. 장애물 회피 Behavior 생성
    # ------------------------------------------------------------
    obstacle_avoidance = ObstacleAvoidanceBehavior(
        avoid_distance=1.0,
    )

    avoid_step_size = 0.03

    # ------------------------------------------------------------
    # 9. 상태머신 생성
    # ------------------------------------------------------------
    state_machine = CaddieStateMachine()

    # ------------------------------------------------------------
    # 10. Home 위치 저장
    # ------------------------------------------------------------
    home_xy = (
        base_controller.get_position(
            data
        )[:2].copy()
    )

    print(
        "[INFO] 캐디 로봇 상태머신 "
        "통합 테스트 시작"
    )

    print(
        f"[INFO] home_xy = {home_xy}"
    )

    # ------------------------------------------------------------
    # 11. 상태별 실행 횟수
    # ------------------------------------------------------------
    state_counts = {
        state: 0
        for state in CaddieState
    }

    # ------------------------------------------------------------
    # 12. 상태머신 통합 반복
    # ------------------------------------------------------------
    for step in range(1500):

        # --------------------------------------------------------
        # 12-1. 골퍼 target 이동
        # --------------------------------------------------------
        if step % 5 == 0:
            target_controller.move_xy(
                data=data,
                dx=0.0,
                dy=0.003,
            )

        # --------------------------------------------------------
        # 12-2. 현재 위치
        # --------------------------------------------------------
        robot_xy = (
            base_controller.get_position(
                data
            )[:2]
        )

        golfer_xy = golfer_tracker.get_xy(
            data
        )

        distance_to_golfer = float(
            np.linalg.norm(
                golfer_xy - robot_xy
            )
        )

        (
            nearest_name,
            nearest_distance,
            nearest_xy,
        ) = obstacle_detector.find_nearest_obstacle(
            data=data,
            robot_xy=robot_xy,
        )

        # --------------------------------------------------------
        # 12-3. 상태머신 Context 생성
        # --------------------------------------------------------
        context = CaddieContext(
            start_follow=True,
            return_home=(step >= 1300),
            emergency_stop=False,
            robot_xy=robot_xy,
            golfer_xy=golfer_xy,
            home_xy=home_xy,
            distance_to_golfer=distance_to_golfer,
            nearest_obstacle_name=nearest_name,
            nearest_obstacle_distance=nearest_distance,
            nearest_obstacle_xy=nearest_xy,
            desired_distance=(
                follow_behavior.desired_distance
            ),
            tolerance=(
                follow_behavior.tolerance
            ),
            safety_radius=(
                obstacle_detector.safety_radius
            ),
        )

        state = state_machine.update(
            context
        )

        state_counts[state] += 1

        # --------------------------------------------------------
        # 12-4. FOLLOW
        # --------------------------------------------------------
        if state == CaddieState.FOLLOW:

            follow_target_xy = (
                follow_behavior.compute_follow_target(
                    robot_xy=robot_xy,
                    golfer_xy=golfer_xy,
                )
            )

            base_controller.move_toward(
                data=data,
                target_xy=follow_target_xy,
                step_size=(
                    follow_behavior.step_size
                ),
            )

        # --------------------------------------------------------
        # 12-5. AVOID
        # --------------------------------------------------------
        elif state == CaddieState.AVOID:

            if nearest_xy is not None:

                avoid_target_xy = (
                    obstacle_avoidance.compute_avoid_target(
                        robot_xy=robot_xy,
                        obstacle_xy=nearest_xy,
                    )
                )

                base_controller.move_toward(
                    data=data,
                    target_xy=avoid_target_xy,
                    step_size=avoid_step_size,
                )

            else:

                mujoco.mj_forward(
                    model,
                    data,
                )

        # --------------------------------------------------------
        # 12-6. RETURN_HOME
        # --------------------------------------------------------
        elif state == CaddieState.RETURN_HOME:

            base_controller.move_toward(
                data=data,
                target_xy=home_xy,
                step_size=0.015,
            )

        # --------------------------------------------------------
        # 12-7. STOP
        # --------------------------------------------------------
        elif state == CaddieState.STOP:

            mujoco.mj_forward(
                model,
                data,
            )

        # --------------------------------------------------------
        # 12-8. TOO_CLOSE
        # --------------------------------------------------------
        elif state == CaddieState.TOO_CLOSE:

            mujoco.mj_forward(
                model,
                data,
            )

        # --------------------------------------------------------
        # 12-9. IDLE
        # --------------------------------------------------------
        elif state == CaddieState.IDLE:

            mujoco.mj_forward(
                model,
                data,
            )

        # --------------------------------------------------------
        # 12-10. EMERGENCY_STOP
        # --------------------------------------------------------
        elif state == CaddieState.EMERGENCY_STOP:

            mujoco.mj_forward(
                model,
                data,
            )

            print(
                "[WARN] 긴급 정지 상태입니다."
            )

            break

        # --------------------------------------------------------
        # 12-11. 물리 시뮬레이션 진행
        # --------------------------------------------------------
        mujoco.mj_step(
            model,
            data,
        )

        # --------------------------------------------------------
        # 12-12. 로그 출력
        # --------------------------------------------------------
        if step % 100 == 0:

            return_home = (
                step >= 1300
            )

            print(
                f"step={step:04d}, "
                f"state={state.name:12s}, "
                f"robot_xy={robot_xy}, "
                f"golfer_xy={golfer_xy}, "
                f"dist={distance_to_golfer:.3f}, "
                f"nearest={nearest_name}, "
                f"obs_dist={nearest_distance:.3f}, "
                f"return_home={return_home}"
            )

    # ------------------------------------------------------------
    # 13. 최종 위치 확인
    # ------------------------------------------------------------
    final_robot_xy = (
        base_controller.get_position(
            data
        )[:2]
    )

    final_golfer_xy = (
        golfer_tracker.get_xy(
            data
        )
    )

    final_distance_to_golfer = float(
        np.linalg.norm(
            final_golfer_xy
            - final_robot_xy
        )
    )

    distance_to_home = float(
        np.linalg.norm(
            home_xy
            - final_robot_xy
        )
    )

    # ------------------------------------------------------------
    # 14. 최종 결과 출력
    # ------------------------------------------------------------
    print(
        "\n========== FINAL RESULT =========="
    )

    print(
        f"final_state = "
        f"{state_machine.state}"
    )

    print(
        f"previous_state = "
        f"{state_machine.previous_state}"
    )

    print(
        f"transition_count = "
        f"{state_machine.transition_count}"
    )

    print(
        f"final_robot_xy = "
        f"{final_robot_xy}"
    )

    print(
        f"final_golfer_xy = "
        f"{final_golfer_xy}"
    )

    print(
        f"final_distance_to_golfer = "
        f"{final_distance_to_golfer:.3f}"
    )

    print(
        f"home_xy = "
        f"{home_xy}"
    )

    print(
        f"distance_to_home = "
        f"{distance_to_home:.3f}"
    )

    # ------------------------------------------------------------
    # 15. 상태별 실행 횟수 출력
    # ------------------------------------------------------------
    print(
        "\n========== STATE COUNTS =========="
    )

    for caddie_state in CaddieState:

        print(
            f"{caddie_state.name:15s} = "
            f"{state_counts[caddie_state]}"
        )

    # ------------------------------------------------------------
    # 16. 통합 테스트 결과 확인
    # ------------------------------------------------------------
    if (
        state_machine.transition_count
        > 0
    ):
        print(
            "[SUCCESS] 상태 전환이 "
            "정상적으로 발생했습니다."
        )
    else:
        print(
            "[WARN] 상태 전환이 "
            "발생하지 않았습니다."
        )

    if (
        state_counts[
            CaddieState.RETURN_HOME
        ]
        > 0
    ):
        print(
            "[SUCCESS] RETURN_HOME 상태가 "
            "실행되었습니다."
        )
    else:
        print(
            "[WARN] RETURN_HOME 상태가 "
            "실행되지 않았습니다."
        )

    print(
        "[SUCCESS] 캐디 로봇 상태머신 "
        "통합 테스트 완료"
    )


if __name__ == "__main__":
    main()