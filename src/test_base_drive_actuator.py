from pathlib import Path

import mujoco
import numpy as np


# ------------------------------------------------------------
# 1. 현재 모델에서 확인된 바퀴 actuator 이름
# ------------------------------------------------------------
WHEEL_ACTUATOR_NAMES = [
    "wheel_front_right_joint_velocity",
    "wheel_front_left_joint_velocity",
    "wheel_rear_right_joint_velocity",
    "wheel_rear_left_joint_velocity",
]

BASE_BODY_NAME = "base_link"

# 처음부터 큰 제어값을 넣지 않고 낮은 값으로 검사한다.
DRIVE_CONTROL_VALUE = 1.0

# timestep이 0.002초라면 1000 step은 약 2초이다.
DRIVE_STEPS = 1000

# 구동 후 정지 상태를 확인할 step 수
STOP_STEPS = 200


def get_actuator_id(
    model: mujoco.MjModel,
    actuator_name: str,
) -> int:
    """
    actuator 이름을 이용해 actuator ID를 찾는다.
    """
    actuator_id = mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_ACTUATOR,
        actuator_name,
    )

    if actuator_id == -1:
        raise ValueError(
            f"actuator를 찾을 수 없습니다: {actuator_name}"
        )

    return actuator_id


def get_body_id(
    model: mujoco.MjModel,
    body_name: str,
) -> int:
    """
    body 이름을 이용해 body ID를 찾는다.
    """
    body_id = mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_BODY,
        body_name,
    )

    if body_id == -1:
        raise ValueError(
            f"body를 찾을 수 없습니다: {body_name}"
        )

    return body_id


def get_base_position(
    data: mujoco.MjData,
    base_body_id: int,
) -> np.ndarray:
    """
    base_link의 현재 월드 위치를 반환한다.
    """
    return data.xpos[base_body_id].copy()


def print_base_position(
    label: str,
    data: mujoco.MjData,
    base_body_id: int,
) -> np.ndarray:
    """
    base_link의 현재 월드 위치를 출력하고 반환한다.
    """
    position = get_base_position(
        data,
        base_body_id,
    )

    print(
        f"{label:20s} "
        f"x={position[0]: .6f}, "
        f"y={position[1]: .6f}, "
        f"z={position[2]: .6f}"
    )

    return position


def main() -> None:
    # ------------------------------------------------------------
    # 2. TIAGo + 골프장 + 골프백 통합 Scene 경로
    # ------------------------------------------------------------
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    if not xml_path.exists():
        raise FileNotFoundError(
            f"통합 XML 파일을 찾을 수 없습니다: {xml_path}"
        )

    # ------------------------------------------------------------
    # 3. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    print(f"[INFO] XML 로딩 시작: {xml_path}")

    model = mujoco.MjModel.from_xml_path(
        str(xml_path)
    )

    data = mujoco.MjData(model)

    print("[SUCCESS] 통합 Scene 로딩 성공")

    # ------------------------------------------------------------
    # 4. base body와 wheel actuator ID 확인
    # ------------------------------------------------------------
    base_body_id = get_body_id(
        model,
        BASE_BODY_NAME,
    )

    wheel_actuator_ids = []

    print("\n========== WHEEL ACTUATOR IDS ==========")

    for actuator_name in WHEEL_ACTUATOR_NAMES:
        actuator_id = get_actuator_id(
            model,
            actuator_name,
        )

        wheel_actuator_ids.append(
            actuator_id
        )

        control_range = model.actuator_ctrlrange[
            actuator_id
        ]

        print(
            f"id={actuator_id:2d} | "
            f"name={actuator_name:35s} | "
            f"ctrlrange={control_range}"
        )

    # ------------------------------------------------------------
    # 5. 초기 상태 계산 및 위치 확인
    # ------------------------------------------------------------
    mujoco.mj_forward(
        model,
        data,
    )

    print("\n========== INITIAL STATE ==========")

    initial_position = print_base_position(
        "initial position",
        data,
        base_body_id,
    )

    print(
        "initial qpos xyz    "
        f"x={data.qpos[0]: .6f}, "
        f"y={data.qpos[1]: .6f}, "
        f"z={data.qpos[2]: .6f}"
    )

    # ------------------------------------------------------------
    # 6. 네 바퀴에 동일한 낮은 velocity 명령 적용
    # ------------------------------------------------------------
    print("\n========== DRIVE TEST ==========")
    print(
        "[INFO] 네 바퀴 actuator에 "
        f"{DRIVE_CONTROL_VALUE} 값을 적용합니다."
    )

    for actuator_id in wheel_actuator_ids:
        data.ctrl[actuator_id] = (
            DRIVE_CONTROL_VALUE
        )

    # ------------------------------------------------------------
    # 7. 시뮬레이션 구동
    # ------------------------------------------------------------
    for step in range(DRIVE_STEPS):
        mujoco.mj_step(
            model,
            data,
        )

        if step in [0, 249, 499, 749, 999]:
            print_base_position(
                f"step={step + 1:4d}",
                data,
                base_body_id,
            )

    driven_position = get_base_position(
        data,
        base_body_id,
    )

    # ------------------------------------------------------------
    # 8. 바퀴 actuator 정지
    # ------------------------------------------------------------
    print("\n========== STOP TEST ==========")

    for actuator_id in wheel_actuator_ids:
        data.ctrl[actuator_id] = 0.0

    for _ in range(STOP_STEPS):
        mujoco.mj_step(
            model,
            data,
        )

    stopped_position = print_base_position(
        "stopped position",
        data,
        base_body_id,
    )

    # ------------------------------------------------------------
    # 9. 이동량 계산
    # ------------------------------------------------------------
    drive_displacement = (
        driven_position - initial_position
    )

    total_displacement = (
        stopped_position - initial_position
    )

    drive_distance_xy = float(
        np.linalg.norm(
            drive_displacement[:2]
        )
    )

    total_distance_xy = float(
        np.linalg.norm(
            total_displacement[:2]
        )
    )

    print("\n========== TEST RESULT ==========")

    print(
        "drive displacement = "
        f"{drive_displacement}"
    )

    print(
        "total displacement = "
        f"{total_displacement}"
    )

    print(
        "drive distance xy  = "
        f"{drive_distance_xy:.6f}"
    )

    print(
        "total distance xy  = "
        f"{total_distance_xy:.6f}"
    )

    # ------------------------------------------------------------
    # 10. 검사 결과 판정
    # ------------------------------------------------------------
    if drive_distance_xy > 0.01:
        print(
            "[SUCCESS] 바퀴 actuator 명령으로 "
            "TIAGo 베이스가 이동했습니다."
        )
    else:
        print(
            "[WARN] 바퀴는 제어됐지만 베이스 이동량이 "
            "충분하지 않습니다."
        )

        print(
            "[INFO] 다음 단계에서 바퀴 방향, 마찰, "
            "actuator 설정을 분석해야 합니다."
        )

    print(
        "[INFO] 이번 테스트는 네 바퀴에 동일한 부호를 "
        "적용한 첫 번째 구동 검사입니다."
    )


if __name__ == "__main__":
    main()