from pathlib import Path

import mujoco
import numpy as np


def get_body_id(model: mujoco.MjModel, body_name: str) -> int:
    """
    body 이름으로 MuJoCo body ID를 찾는다.

    찾지 못하면 -1을 반환한다.
    """
    return mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_BODY,
        body_name,
    )


def get_geom_id(model: mujoco.MjModel, geom_name: str) -> int:
    """
    geom 이름으로 MuJoCo geom ID를 찾는다.

    찾지 못하면 -1을 반환한다.
    """
    return mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_GEOM,
        geom_name,
    )


def print_body_position(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    body_name: str,
) -> np.ndarray | None:
    """
    body의 월드 좌표를 출력하고 복사본을 반환한다.
    """
    body_id = get_body_id(model, body_name)

    if body_id == -1:
        print(f"[WARN] body를 찾을 수 없습니다: {body_name}")
        return None

    position = data.xpos[body_id].copy()

    print(
        f"{body_name:25s} "
        f"id={body_id:3d}, "
        f"pos={position}"
    )

    return position


def print_geom_status(
    model: mujoco.MjModel,
    geom_name: str,
) -> None:
    """
    geom의 존재 여부와 충돌 설정을 출력한다.
    """
    geom_id = get_geom_id(model, geom_name)

    if geom_id == -1:
        print(f"[WARN] geom을 찾을 수 없습니다: {geom_name}")
        return

    print(
        f"{geom_name:28s} "
        f"id={geom_id:3d}, "
        f"contype={model.geom_contype[geom_id]}, "
        f"conaffinity={model.geom_conaffinity[geom_id]}"
    )


def main() -> None:
    # ------------------------------------------------------------
    # 1. 골프백이 추가된 통합 Scene 경로
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

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    print("[SUCCESS] 골프백 및 랙 포함 Scene 로딩 성공")

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

    # 초기 월드 좌표 계산
    mujoco.mj_forward(model, data)

    # ------------------------------------------------------------
    # 4. 골프백 관련 body 위치 확인
    # ------------------------------------------------------------
    print("\n========== GOLF BAG BODY POSITIONS ==========")

    rack_position_before = print_body_position(
        model,
        data,
        "golf_bag_rack_root",
    )

    bag_position_before = print_body_position(
        model,
        data,
        "golf_bag_body",
    )

    # ------------------------------------------------------------
    # 5. 골프백 관련 geom 존재 여부 확인
    # ------------------------------------------------------------
    print("\n========== GOLF BAG GEOM STATUS ==========")

    golf_bag_geom_names = [
        "golf_bag_rack_base",
        "golf_bag_rack_left",
        "golf_bag_rack_right",
        "golf_bag_body_geom",
        "golf_bag_top_trim",
        "golf_club_01_shaft",
        "golf_club_01_head",
        "golf_club_02_shaft",
        "golf_club_02_head",
        "golf_club_03_shaft",
        "golf_club_03_head",
    ]

    for geom_name in golf_bag_geom_names:
        print_geom_status(
            model,
            geom_name,
        )

    # ------------------------------------------------------------
    # 6. 시뮬레이션 200 step 실행
    # ------------------------------------------------------------
    for _ in range(200):
        mujoco.mj_step(model, data)

    # ------------------------------------------------------------
    # 7. 200 step 후 위치 확인
    # ------------------------------------------------------------
    print("\n========== AFTER 200 STEPS ==========")

    rack_position_after = print_body_position(
        model,
        data,
        "golf_bag_rack_root",
    )

    bag_position_after = print_body_position(
        model,
        data,
        "golf_bag_body",
    )

    # ------------------------------------------------------------
    # 8. 고정 상태 검증
    # ------------------------------------------------------------
    print("\n========== STABILITY CHECK ==========")

    if (
        rack_position_before is not None
        and rack_position_after is not None
    ):
        rack_movement = np.linalg.norm(
            rack_position_after - rack_position_before
        )

        print(
            "golf_bag_rack_root 이동 거리 "
            f"= {rack_movement:.10f} m"
        )

    if (
        bag_position_before is not None
        and bag_position_after is not None
    ):
        bag_movement = np.linalg.norm(
            bag_position_after - bag_position_before
        )

        print(
            "golf_bag_body 이동 거리 "
            f"= {bag_movement:.10f} m"
        )

    print("\n[SUCCESS] 골프백 및 랙 200 step 실행 성공")


if __name__ == "__main__":
    main()