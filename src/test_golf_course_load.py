from pathlib import Path

import mujoco


def main():
    # ------------------------------------------------------------
    # 1. 골프장 환경 XML 경로
    # ------------------------------------------------------------
    xml_path = Path(
        "models/custom/golf_caddie_tiago/golf_course_scene.xml"
    )

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {xml_path}"
        )

    # ------------------------------------------------------------
    # 2. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    # XML에 정의된 초기 body 월드 좌표를 계산한다.
    mujoco.mj_forward(model, data)

    print("[SUCCESS] 골프장 기본 환경 로딩 성공")
    print(f"nbody = {model.nbody}")
    print(f"ngeom = {model.ngeom}")
    print(f"njnt = {model.njnt}")
    print(f"nq = {model.nq}")
    print(f"nv = {model.nv}")

    # ------------------------------------------------------------
    # 3. 주요 body 이름 확인
    # ------------------------------------------------------------
    important_bodies = [
        "golf_ball",
        "golfer_target",
        "hole_cup",
        "flag_pole",
        "obstacle_tree_01",
        "obstacle_tree_02",
        "obstacle_marker_box",
    ]

    print("\n[INFO] 주요 body ID 확인")

    for body_name in important_bodies:
        body_id = mujoco.mj_name2id(
            model,
            mujoco.mjtObj.mjOBJ_BODY,
            body_name,
        )

        if body_id == -1:
            print(f"[WARN] body를 찾을 수 없음: {body_name}")
        else:
            pos = data.xpos[body_id]
            print(
                f"{body_name:25s} "
                f"id={body_id:3d}, pos={pos}"
            )

    # ------------------------------------------------------------
    # 4. 시뮬레이션 몇 step 실행
    # ------------------------------------------------------------
    for step in range(100):
        mujoco.mj_step(model, data)

    # ------------------------------------------------------------
    # 5. 골프공 위치 출력
    # ------------------------------------------------------------
    ball_id = mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_BODY,
        "golf_ball",
    )

    ball_pos = data.xpos[ball_id]

    print(
        f"\n[INFO] 100 step 후 golf_ball 위치: "
        f"{ball_pos}"
    )

    print("[SUCCESS] 골프장 환경 100 step 실행 성공")


if __name__ == "__main__":
    main()