from pathlib import Path

import mujoco


def get_joint_name(
    model: mujoco.MjModel,
    joint_id: int,
) -> str:
    """
    joint ID를 이용해 joint 이름을 반환한다.

    이름이 없는 joint는 "(unnamed)"으로 표시한다.
    """
    joint_name = mujoco.mj_id2name(
        model,
        mujoco.mjtObj.mjOBJ_JOINT,
        joint_id,
    )

    if joint_name is None:
        return "(unnamed)"

    return joint_name


def get_joint_type_name(
    joint_type: int,
) -> str:
    """
    MuJoCo joint type 숫자를 사람이 읽기 쉬운 이름으로 변환한다.
    """
    joint_type_names = {
        int(mujoco.mjtJoint.mjJNT_FREE): "free",
        int(mujoco.mjtJoint.mjJNT_BALL): "ball",
        int(mujoco.mjtJoint.mjJNT_SLIDE): "slide",
        int(mujoco.mjtJoint.mjJNT_HINGE): "hinge",
    }

    return joint_type_names.get(
        int(joint_type),
        f"unknown({joint_type})",
    )


def main() -> None:
    # ------------------------------------------------------------
    # 1. 현재 사용하는 TIAGo + 골프장 + 골프백 통합 Scene 경로
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

    print("[SUCCESS] 통합 Scene 로딩 성공")

    # ------------------------------------------------------------
    # 3. 모델 joint 기본 정보
    # ------------------------------------------------------------
    print("\n========== JOINT INFO ==========")
    print(f"njnt = {model.njnt}")
    print(f"nq   = {model.nq}")
    print(f"nv   = {model.nv}")

    # ------------------------------------------------------------
    # 4. 모든 joint 정보 출력
    # ------------------------------------------------------------
    print("\n========== ALL JOINTS ==========")

    for joint_id in range(model.njnt):
        joint_name = get_joint_name(
            model,
            joint_id,
        )

        joint_type = int(
            model.jnt_type[joint_id]
        )

        joint_type_name = get_joint_type_name(
            joint_type
        )

        qpos_address = int(
            model.jnt_qposadr[joint_id]
        )

        dof_address = int(
            model.jnt_dofadr[joint_id]
        )

        body_id = int(
            model.jnt_bodyid[joint_id]
        )

        body_name = mujoco.mj_id2name(
            model,
            mujoco.mjtObj.mjOBJ_BODY,
            body_id,
        )

        if body_name is None:
            body_name = "(unnamed)"

        print(
            f"id={joint_id:2d} | "
            f"name={joint_name:35s} | "
            f"type={joint_type_name:5s} | "
            f"body={body_name:25s} | "
            f"qposadr={qpos_address:2d} | "
            f"dofadr={dof_address:2d}"
        )

    # ------------------------------------------------------------
    # 5. wheel 관련 joint 검색
    # ------------------------------------------------------------
    print("\n========== WHEEL JOINTS ==========")

    wheel_count = 0

    for joint_id in range(model.njnt):
        joint_name = get_joint_name(
            model,
            joint_id,
        )

        if "wheel" not in joint_name.lower():
            continue

        joint_type_name = get_joint_type_name(
            int(model.jnt_type[joint_id])
        )

        qpos_address = int(
            model.jnt_qposadr[joint_id]
        )

        dof_address = int(
            model.jnt_dofadr[joint_id]
        )

        print(
            f"id={joint_id:2d} | "
            f"name={joint_name:35s} | "
            f"type={joint_type_name:5s} | "
            f"qposadr={qpos_address:2d} | "
            f"dofadr={dof_address:2d}"
        )

        wheel_count += 1

    if wheel_count == 0:
        print("[WARN] wheel 관련 joint가 없습니다.")

    # ------------------------------------------------------------
    # 6. free joint 검색
    # ------------------------------------------------------------
    print("\n========== FREE JOINTS ==========")

    free_joint_count = 0

    for joint_id in range(model.njnt):
        joint_type = int(
            model.jnt_type[joint_id]
        )

        if joint_type != int(
            mujoco.mjtJoint.mjJNT_FREE
        ):
            continue

        joint_name = get_joint_name(
            model,
            joint_id,
        )

        qpos_address = int(
            model.jnt_qposadr[joint_id]
        )

        dof_address = int(
            model.jnt_dofadr[joint_id]
        )

        body_id = int(
            model.jnt_bodyid[joint_id]
        )

        body_name = mujoco.mj_id2name(
            model,
            mujoco.mjtObj.mjOBJ_BODY,
            body_id,
        )

        if body_name is None:
            body_name = "(unnamed)"

        print(
            f"id={joint_id:2d} | "
            f"name={joint_name:35s} | "
            f"body={body_name:25s} | "
            f"qposadr={qpos_address:2d} | "
            f"dofadr={dof_address:2d}"
        )

        free_joint_count += 1

    if free_joint_count == 0:
        print("[INFO] free joint가 없습니다.")

    print("\n[SUCCESS] joint 검사 완료")


if __name__ == "__main__":
    main()