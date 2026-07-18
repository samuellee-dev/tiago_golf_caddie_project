from pathlib import Path

import mujoco
import numpy as np

from controller.base_controller import DirectBaseController


def main() -> None:
    # ------------------------------------------------------------
    # 1. 통합 Scene
    # ------------------------------------------------------------
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    print(f"[INFO] XML 로딩 시작: {xml_path}")

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    print("[SUCCESS] 통합 Scene 로딩 성공")

    # ------------------------------------------------------------
    # 2. Controller 생성
    # ------------------------------------------------------------
    controller = DirectBaseController(
        model=model,
        joint_name="reference",
    )

    mujoco.mj_forward(model, data)

    print("\n========== INITIAL POSITION ==========")

    initial_position = controller.get_position(data)

    print(initial_position)

    # ------------------------------------------------------------
    # 3. 목표 좌표
    # ------------------------------------------------------------
    target_xy = np.array(
        [
            2.0,
            0.0,
        ]
    )

    print("\n========== TARGET ==========")
    print(target_xy)

    # ------------------------------------------------------------
    # 4. 목표까지 이동
    # ------------------------------------------------------------
    step_size = 0.02

    print("\n========== MOVE ==========")

    for step in range(100):

        controller.move_toward(
            data=data,
            target_xy=target_xy,
            step_size=step_size,
        )

        if step in [0, 24, 49, 74, 99]:

            position = controller.get_position(data)

            print(
                f"step={step+1:3d} "
                f"x={position[0]:.3f} "
                f"y={position[1]:.3f} "
                f"z={position[2]:.3f}"
            )

    # ------------------------------------------------------------
    # 5. 최종 위치
    # ------------------------------------------------------------
    final_position = controller.get_position(data)

    print("\n========== RESULT ==========")

    print("initial :", initial_position)

    print("final   :", final_position)

    print(
        "distance :",
        np.linalg.norm(
            target_xy - final_position[:2]
        )
    )


if __name__ == "__main__":
    main()