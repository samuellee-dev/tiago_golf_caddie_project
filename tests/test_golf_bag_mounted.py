from pathlib import Path

import mujoco
import numpy as np


def get_body_id(
    model: mujoco.MjModel,
    body_name: str,
) -> int:
    """
    body 이름으로 MuJoCo body ID를 찾는다.
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


def get_body_position(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    body_name: str,
) -> np.ndarray:
    """
    body의 월드 위치를 반환한다.
    """
    body_id = get_body_id(
        model,
        body_name,
    )

    return data.xpos[body_id].copy()


def get_body_rotation(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    body_name: str,
) -> np.ndarray:
    """
    body의 월드 회전행렬을 3x3 배열로 반환한다.
    """
    body_id = get_body_id(
        model,
        body_name,
    )

    return data.xmat[body_id].reshape(3, 3).copy()


def get_child_local_position(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    parent_name: str,
    child_name: str,
) -> np.ndarray:
    """
    child의 월드 위치를 parent 기준 로컬 위치로 변환한다.

    local_position =
        parent_rotation.T
        @ (child_world_position - parent_world_position)
    """
    parent_position = get_body_position(
        model,
        data,
        parent_name,
    )

    child_position = get_body_position(
        model,
        data,
        child_name,
    )

    parent_rotation = get_body_rotation(
        model,
        data,
        parent_name,
    )

    return parent_rotation.T @ (
        child_position - parent_position
    )


def print_body_position(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    body_name: str,
) -> np.ndarray:
    """
    body의 월드 위치를 출력하고 반환한다.
    """
    body_id = get_body_id(
        model,
        body_name,
    )

    position = get_body_position(
        model,
        data,
        body_name,
    )

    print(
        f"{body_name:25s} "
        f"id={body_id:3d}, "
        f"pos={position}"
    )

    return position


def main() -> None:
    # ------------------------------------------------------------
    # 1. 골프백이 TIAGo 베이스에 장착된 통합 Scene 경로
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
    # 2. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    print(f"[INFO] XML 로딩 시작: {xml_path}")

    model = mujoco.MjModel.from_xml_path(
        str(xml_path)
    )

    data = mujoco.MjData(model)

    print(
        "[SUCCESS] TIAGo 골프백 장착 Scene 로딩 성공"
    )

    # ------------------------------------------------------------
    # 3. 모델 기본 정보
    # ------------------------------------------------------------
    print("\n========== MODEL INFO ==========")
    print(f"nbody   = {model.nbody}")
    print(f"ngeom   = {model.ngeom}")
    print(f"njnt    = {model.njnt}")
    print(f"nq      = {model.nq}")
    print(f"nv      = {model.nv}")
    print(f"nu      = {model.nu}")
    print(f"nsensor = {model.nsensor}")

    mujoco.mj_forward(
        model,
        data,
    )

    # ------------------------------------------------------------
    # 4. 초기 월드 위치 확인
    # ------------------------------------------------------------
    print(
        "\n========== INITIAL BODY POSITIONS =========="
    )

    print_body_position(
        model,
        data,
        "base_link",
    )

    print_body_position(
        model,
        data,
        "golf_bag_rack_mount",
    )

    print_body_position(
        model,
        data,
        "golf_bag_body",
    )

    # ------------------------------------------------------------
    # 5. 초기 로컬 위치 확인
    # ------------------------------------------------------------
    rack_local_before = get_child_local_position(
        model,
        data,
        parent_name="base_link",
        child_name="golf_bag_rack_mount",
    )

    bag_local_before = get_child_local_position(
        model,
        data,
        parent_name="golf_bag_rack_mount",
        child_name="golf_bag_body",
    )

    print(
        "\n========== INITIAL LOCAL POSITIONS =========="
    )

    print(
        "rack local position = "
        f"{rack_local_before}"
    )

    print(
        "bag local position  = "
        f"{bag_local_before}"
    )

    # ------------------------------------------------------------
    # 6. 300 step 실행
    # ------------------------------------------------------------
    for _ in range(300):
        mujoco.mj_step(
            model,
            data,
        )

    # ------------------------------------------------------------
    # 7. 300 step 후 월드 위치 확인
    # ------------------------------------------------------------
    print(
        "\n========== AFTER 300 STEPS =========="
    )

    print_body_position(
        model,
        data,
        "base_link",
    )

    print_body_position(
        model,
        data,
        "golf_bag_rack_mount",
    )

    print_body_position(
        model,
        data,
        "golf_bag_body",
    )

    # ------------------------------------------------------------
    # 8. 300 step 후 로컬 위치 계산
    # ------------------------------------------------------------
    rack_local_after = get_child_local_position(
        model,
        data,
        parent_name="base_link",
        child_name="golf_bag_rack_mount",
    )

    bag_local_after = get_child_local_position(
        model,
        data,
        parent_name="golf_bag_rack_mount",
        child_name="golf_bag_body",
    )

    rack_local_error = np.linalg.norm(
        rack_local_after - rack_local_before
    )

    bag_local_error = np.linalg.norm(
        bag_local_after - bag_local_before
    )

    print(
        "\n========== MOUNT STABILITY CHECK =========="
    )

    print(
        "300 step 후 rack local position = "
        f"{rack_local_after}"
    )

    print(
        "300 step 후 bag local position  = "
        f"{bag_local_after}"
    )

    print(
        "rack-base 로컬 위치 오차 = "
        f"{rack_local_error:.12f} m"
    )

    print(
        "bag-rack 로컬 위치 오차  = "
        f"{bag_local_error:.12f} m"
    )

    # ------------------------------------------------------------
    # 9. 최종 판정
    # ------------------------------------------------------------
    tolerance = 1e-8

    if rack_local_error > tolerance:
        raise RuntimeError(
            "골프백 랙이 base_link 기준 로컬 위치를 "
            "유지하지 못했습니다."
        )

    if bag_local_error > tolerance:
        raise RuntimeError(
            "골프백 본체가 랙 기준 로컬 위치를 "
            "유지하지 못했습니다."
        )

    print(
        "\n[SUCCESS] 골프백 랙이 "
        "TIAGo 베이스에 고정됨"
    )

    print(
        "[SUCCESS] 골프백 장착 상태 "
        "300 step 실행 성공"
    )


if __name__ == "__main__":
    main()