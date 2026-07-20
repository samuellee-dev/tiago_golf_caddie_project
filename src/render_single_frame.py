from pathlib import Path

import imageio.v2 as imageio
import mujoco


def main():
    # ------------------------------------------------------------
    # 1. XML 경로와 출력 경로 설정
    # ------------------------------------------------------------
    xml_path = Path(
        "models/custom/golf_caddie_tiago/"
        "pal_tiago_dual_golf/"
        "golf_caddie_tiago_scene.xml"
    )

    output_path = Path("outputs/camera/single_frame.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not xml_path.exists():
        raise FileNotFoundError(
            f"XML 파일을 찾을 수 없습니다: {xml_path}"
        )

    # ------------------------------------------------------------
    # 2. MuJoCo 모델 로딩
    # ------------------------------------------------------------
    model = mujoco.MjModel.from_xml_path(str(xml_path))
    data = mujoco.MjData(model)

    # 초기 qpos를 기준으로 body와 geom의 위치를 계산한다.
    mujoco.mj_forward(model, data)

    # ------------------------------------------------------------
    # 3. Renderer 생성
    # ------------------------------------------------------------
    renderer = mujoco.Renderer(
        model,
        height=720,
        width=1280,
    )

    # ------------------------------------------------------------
    # 4. golf_overview_camera로 Scene 렌더링
    # ------------------------------------------------------------
    renderer.update_scene(
        data,
        camera="golf_overview_camera",
    )

    image = renderer.render()

    # ------------------------------------------------------------
    # 5. 이미지 저장
    # ------------------------------------------------------------
    imageio.imwrite(output_path, image)

    renderer.close()

    print(f"[SUCCESS] 단일 이미지 저장 성공: {output_path}")
    print(f"[INFO] image shape = {image.shape}")


if __name__ == "__main__":
    main()