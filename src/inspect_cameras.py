from pathlib import Path

import mujoco


def main():
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {xml_path}"
        )

    model = mujoco.MjModel.from_xml_path(str(xml_path))

    print("========== CAMERA LIST ==========")
    print(f"camera 개수 = {model.ncam}")

    for camera_id in range(model.ncam):
        camera_name = mujoco.mj_id2name(
            model,
            mujoco.mjtObj.mjOBJ_CAMERA,
            camera_id,
        )

        if camera_name is None:
            camera_name = "(no name)"

        camera_pos = model.cam_pos[camera_id]

        print(
            f"id={camera_id:2d}  "
            f"name={camera_name:30s}  "
            f"pos={camera_pos}"
        )


if __name__ == "__main__":
    main()