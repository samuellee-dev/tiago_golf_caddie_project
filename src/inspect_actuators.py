from pathlib import Path

import mujoco


def get_actuator_name(
    model: mujoco.MjModel,
    actuator_id: int,
) -> str:
    """
    actuator ID를 이용해 actuator 이름을 반환한다.

    이름이 없는 actuator라면 구분할 수 있도록
    "(unnamed)" 문자열을 반환한다.
    """
    actuator_name = mujoco.mj_id2name(
        model,
        mujoco.mjtObj.mjOBJ_ACTUATOR,
        actuator_id,
    )

    if actuator_name is None:
        return "(unnamed)"

    return actuator_name


def get_joint_name(
    model: mujoco.MjModel,
    joint_id: int,
) -> str:
    """
    joint ID를 이용해 joint 이름을 반환한다.

    이름이 없는 joint라면 구분할 수 있도록
    "(unnamed)" 문자열을 반환한다.
    """
    joint_name = mujoco.mj_id2name(
        model,
        mujoco.mjtObj.mjOBJ_JOINT,
        joint_id,
    )

    if joint_name is None:
        return "(unnamed)"

    return joint_name


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
    # 3. 모델의 actuator 개수 확인
    # ------------------------------------------------------------
    print("\n========== ACTUATOR INFO ==========")
    print(f"nu = {model.nu}")

    if model.nu == 0:
        print("[WARN] 모델에 actuator가 없습니다.")
        return

    # ------------------------------------------------------------
    # 4. 모든 actuator 정보 출력
    # ------------------------------------------------------------
    print("\n========== ALL ACTUATORS ==========")

    for actuator_id in range(model.nu):
        actuator_name = get_actuator_name(
            model,
            actuator_id,
        )

        # actuator가 연결된 transmission 대상 ID
        transmission_id = int(
            model.actuator_trnid[actuator_id, 0]
        )

        # 현재 모델에서는 대부분 joint transmission을 사용한다.
        if 0 <= transmission_id < model.njnt:
            joint_name = get_joint_name(
                model,
                transmission_id,
            )
        else:
            joint_name = "(not a joint transmission)"

        control_range = model.actuator_ctrlrange[
            actuator_id
        ]

        control_limited = bool(
            model.actuator_ctrllimited[actuator_id]
        )

        print(
            f"id={actuator_id:2d} | "
            f"name={actuator_name:35s} | "
            f"joint={joint_name:30s} | "
            f"ctrl_limited={control_limited} | "
            f"ctrlrange={control_range}"
        )

    # ------------------------------------------------------------
    # 5. base 또는 wheel 관련 actuator 후보 검색
    # ------------------------------------------------------------
    candidate_keywords = [
        "base",
        "wheel",
        "caster",
        "left",
        "right",
    ]

    candidate_count = 0

    print(
        "\n========== BASE / WHEEL CANDIDATES =========="
    )

    for actuator_id in range(model.nu):
        actuator_name = get_actuator_name(
            model,
            actuator_id,
        )

        lower_name = actuator_name.lower()

        if any(
            keyword in lower_name
            for keyword in candidate_keywords
        ):
            transmission_id = int(
                model.actuator_trnid[actuator_id, 0]
            )

            if 0 <= transmission_id < model.njnt:
                joint_name = get_joint_name(
                    model,
                    transmission_id,
                )
            else:
                joint_name = "(not a joint transmission)"

            print(
                f"id={actuator_id:2d} | "
                f"actuator={actuator_name} | "
                f"joint={joint_name}"
            )

            candidate_count += 1

    if candidate_count == 0:
        print(
            "[INFO] 이름에 base 또는 wheel 관련 문자열이 "
            "포함된 actuator가 없습니다."
        )

    print("\n[SUCCESS] actuator 검사 완료")


if __name__ == "__main__":
    main()