from pathlib import Path

import imageio.v2 as imageio
import mujoco
import numpy as np

from controller.base_controller import DirectBaseController
from controller.target_controller import TargetBodyController
from perception.fake_golfer_tracker import FakeGolferTracker
from behavior.follow_behavior import FollowGolferBehavior


ROBOT_ROOT_FREE_JOINT = "reference"
GOLFER_TARGET_FREE_JOINT = "golfer_target_free_joint"


def main():
    # ------------------------------------------------------------
    # 1. 통합 Scene 경로와 출력 폴더 설정
    # ------------------------------------------------------------
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    output_dir = Path(
        "outputs/camera/follow_sequence"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {xml_path}"
        )

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
    # 7. 오프스크린 Renderer 생성
    # ------------------------------------------------------------
    renderer = mujoco.Renderer(
        model,
        height=720,
        width=1280,
    )

    print(
        "[INFO] 추종 시퀀스 렌더링 시작"
    )

    # ------------------------------------------------------------
    # 8. 움직이는 골퍼 추종 및 프레임 저장
    # ------------------------------------------------------------
    for step in range(1000):
        # --------------------------------------------------------
        # 8-1. 골퍼 Target을 천천히 +Y 방향으로 이동
        # --------------------------------------------------------
        if step % 5 == 0:
            target_controller.move_xy(
                data=data,
                dx=0.0,
                dy=0.003,
            )

        # --------------------------------------------------------
        # 8-2. 현재 로봇과 골퍼 위치 읽기
        # --------------------------------------------------------
        robot_xy = (
            base_controller
            .get_position(data)[:2]
        )

        golfer_xy = golfer_tracker.get_xy(
            data
        )

        # --------------------------------------------------------
        # 8-3. 추종 행동 판단 및 거리 계산
        # --------------------------------------------------------
        action = follow_behavior.decide_action(
            robot_xy=robot_xy,
            golfer_xy=golfer_xy,
        )

        distance = follow_behavior.compute_distance(
            robot_xy=robot_xy,
            golfer_xy=golfer_xy,
        )

        # --------------------------------------------------------
        # 8-4. FOLLOW이면 골퍼 뒤쪽 목표로 이동
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

        else:
            mujoco.mj_forward(
                model,
                data,
            )

        # --------------------------------------------------------
        # 8-5. 100 step 간격으로 프레임 저장
        # --------------------------------------------------------
        if step % 100 == 0:
            renderer.update_scene(
                data,
                camera="golf_overview_camera",
            )

            image = renderer.render()

            output_path = (
                output_dir
                / f"frame_{step:04d}.png"
            )

            imageio.imwrite(
                output_path,
                image,
            )

            print(
                f"step={step:04d}, "
                f"distance={distance:.3f}, "
                f"action={action}, "
                f"saved={output_path}"
            )

    renderer.close()

    print(
        "[SUCCESS] 추종 시퀀스 렌더링 완료"
    )


if __name__ == "__main__":
    main()