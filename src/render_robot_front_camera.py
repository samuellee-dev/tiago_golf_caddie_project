from pathlib import Path

import imageio.v2 as imageio
import mujoco


MODEL_PATH = Path(
    "models/custom/golf_caddie_tiago/"
    "pal_tiago_dual_golf/"
    "golf_caddie_tiago_scene.xml"
)

OUTPUT_PATH = Path(
    "outputs/camera/robot_front_camera.png"
)

CAMERA_NAME = "robot_front_camera"

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720


def main():
    """
    TIAGo에 추가한 robot_front_camera 영상을
    MuJoCo Renderer로 렌더링하여 PNG 파일로 저장한다.
    """

    # ---------------------------------------------------------
    # 1. 통합 Scene XML 확인
    # ---------------------------------------------------------
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"통합 Scene XML을 찾을 수 없습니다: {MODEL_PATH}"
        )

    # ---------------------------------------------------------
    # 2. 출력 폴더 생성
    # ---------------------------------------------------------
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ---------------------------------------------------------
    # 3. MuJoCo 모델 및 데이터 생성
    # ---------------------------------------------------------
    print(f"[INFO] XML 로딩 시작: {MODEL_PATH}")

    model = mujoco.MjModel.from_xml_path(
        str(MODEL_PATH)
    )
    data = mujoco.MjData(model)

    # ---------------------------------------------------------
    # 4. 전방 카메라 존재 여부 확인
    # ---------------------------------------------------------
    camera_id = mujoco.mj_name2id(
        model,
        mujoco.mjtObj.mjOBJ_CAMERA,
        CAMERA_NAME,
    )

    if camera_id == -1:
        raise ValueError(
            f"카메라를 찾을 수 없습니다: {CAMERA_NAME}"
        )

    print(
        f"[INFO] 카메라 확인: "
        f"name={CAMERA_NAME}, id={camera_id}"
    )

    # ---------------------------------------------------------
    # 5. 초기 상태의 body 및 camera 위치 계산
    # ---------------------------------------------------------
    mujoco.mj_forward(model, data)

    # ---------------------------------------------------------
    # 6. Renderer 생성
    # ---------------------------------------------------------
    renderer = mujoco.Renderer(
        model,
        height=IMAGE_HEIGHT,
        width=IMAGE_WIDTH,
    )

    try:
        # -----------------------------------------------------
        # 7. robot_front_camera 기준 Scene 업데이트
        # -----------------------------------------------------
        renderer.update_scene(
            data,
            camera=CAMERA_NAME,
        )

        # -----------------------------------------------------
        # 8. RGB 이미지 렌더링
        # -----------------------------------------------------
        image_rgb = renderer.render()

        # -----------------------------------------------------
        # 9. PNG 이미지 저장
        # -----------------------------------------------------
        imageio.imwrite(
            OUTPUT_PATH,
            image_rgb,
        )

    finally:
        renderer.close()

    # ---------------------------------------------------------
    # 10. 실행 결과 출력
    # ---------------------------------------------------------
    print(
        "[SUCCESS] 로봇 전방 카메라 이미지 저장 완료"
    )
    print(f"[INFO] 저장 경로: {OUTPUT_PATH}")
    print(f"[INFO] image shape: {image_rgb.shape}")
    print(f"[INFO] camera: {CAMERA_NAME}")


if __name__ == "__main__":
    main()