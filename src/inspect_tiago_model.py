from pathlib import Path

import mujoco


def get_names(model, object_type, count):
    """
    MuJoCo 모델 안에 있는 body, joint, actuator 등의 이름을
    출력하기 위한 함수.

    object_type 예:
    - mujoco.mjtObj.mjOBJ_BODY
    - mujoco.mjtObj.mjOBJ_JOINT
    - mujoco.mjtObj.mjOBJ_ACTUATOR
    """

    names = []

    for i in range(count):
        name = mujoco.mj_id2name(
            model,
            object_type,
            i,
        )

        if name:
            names.append(name)

    return names


def main():
    xml_path = Path(
        "models/mujoco_menagerie/"
        "pal_tiago_dual/scene_position.xml"
    )

    if not xml_path.exists():
        raise FileNotFoundError(
            f"{xml_path} 파일이 없습니다. "
            "실제 XML 파일명을 확인한 뒤 경로를 수정하세요."
        )

    model = mujoco.MjModel.from_xml_path(str(xml_path))

    body_names = get_names(
        model,
        mujoco.mjtObj.mjOBJ_BODY,
        model.nbody,
    )

    joint_names = get_names(
        model,
        mujoco.mjtObj.mjOBJ_JOINT,
        model.njnt,
    )

    actuator_names = get_names(
        model,
        mujoco.mjtObj.mjOBJ_ACTUATOR,
        model.nu,
    )

    geom_names = get_names(
        model,
        mujoco.mjtObj.mjOBJ_GEOM,
        model.ngeom,
    )

    print("\n========== BODY NAMES ==========")

    for name in body_names:
        print(name)

    print("\n========== JOINT NAMES ==========")

    for name in joint_names:
        print(name)

    print("\n========== ACTUATOR NAMES ==========")

    for name in actuator_names:
        print(name)

    print("\n========== GEOM NAMES ==========")

    for name in geom_names:
        print(name)


if __name__ == "__main__":
    main()