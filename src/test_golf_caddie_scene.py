from pathlib import Path

import mujoco


def get_body_id(model: mujoco.MjModel, body_name: str) -> int:
    """
    body 이름으로 MuJoCo body ID를 찾는다.
    """
    return mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_BODY,
        body_name,
    )


def print_body_position(
    model: mujoco.MjModel,
    data: mujoco.MjData,
    body_name: str,
) -> None:
    """
    지정한 body의 월드 좌표를 출력한다.
    """
    body_id = get_body_id(model, body_name)

    if body_id == -1:
        print(f"[WARN] body를 찾을 수 없습니다: {body_name}")
        return

    position = data.xpos[body_id]

    print(
        f"{body_name:25s} "
        f"id={body_id:3d}, "
        f"pos={position}"
    )


def main() -> None:
    # ------------------------------------------------------------
    # 1. TIAGo + 골프장 통합 XML 경로
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
    # 2. MuJoCo 통합 모델 로딩
    # ------------------------------------------------------------
    print(f"[INFO] XML 로딩 시작: {xml_path}")

    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    print("[SUCCESS] TIAGo + 골프장 통합 scene 로딩 성공")

    # ------------------------------------------------------------
    # 3. 모델 기본 정보 출력
    # ------------------------------------------------------------
    print("\n========== MODEL INFO ==========")
    print(f"nbody   = {model.nbody}")
    print(f"ngeom   = {model.ngeom}")
    print(f"njnt    = {model.njnt}")
    print(f"nq      = {model.nq}")
    print(f"nv      = {model.nv}")
    print(f"nu      = {model.nu}")
    print(f"nsensor = {model.nsensor}")

    # 초기 body 위치를 계산한다.
    mujoco.mj_forward(model, data)

    # ------------------------------------------------------------
    # 4. 골프장 주요 body 위치 확인
    # ------------------------------------------------------------
    print("\n========== GOLF OBJECT POSITIONS ==========")

    golf_body_names = [
        "golf_ball",
        "golfer_target",
        "hole_cup",
        "flag_pole",
        "obstacle_tree_01",
        "obstacle_tree_02",
        "obstacle_marker_box",
    ]

    for body_name in golf_body_names:
        print_body_position(
            model,
            data,
            body_name,
        )

    # ------------------------------------------------------------
    # 5. TIAGo 주요 body 존재 여부 확인
    # ------------------------------------------------------------
    print("\n========== TIAGO BODY POSITIONS ==========")

    tiago_body_names = [
        "base_link",
        "torso_fixed_link",
        "torso_lift_link",
        "head_1_link",
        "head_2_link",
    ]

    for body_name in tiago_body_names:
        print_body_position(
            model,
            data,
            body_name,
        )

    # ------------------------------------------------------------
    # 6. 시뮬레이션 100 step 실행
    # ------------------------------------------------------------
    for _ in range(100):
        mujoco.mj_step(model, data)

    # ------------------------------------------------------------
    # 7. 100 step 후 골프공 위치 확인
    # ------------------------------------------------------------
    print("\n========== AFTER 100 STEPS ==========")

    print_body_position(
        model,
        data,
        "golf_ball",
    )

    print("\n[SUCCESS] 통합 환경 100 step 실행 성공")


if __name__ == "__main__":
    main()