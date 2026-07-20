from pathlib import Path

import cv2


def main():
    # ------------------------------------------------------------
    # 1. 읽을 이미지 경로
    # ------------------------------------------------------------
    image_path = Path(
        "outputs/camera/single_frame.png"
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"{image_path} 파일이 없습니다. "
            "먼저 render_single_frame.py를 실행하세요."
        )

    # ------------------------------------------------------------
    # 2. OpenCV로 이미지 읽기
    # ------------------------------------------------------------
    # OpenCV는 기본적으로 BGR 형식으로 이미지를 읽는다.
    image_bgr = cv2.imread(
        str(image_path)
    )

    if image_bgr is None:
        raise RuntimeError(
            f"OpenCV가 이미지를 읽지 못했습니다: "
            f"{image_path}"
        )

    # ------------------------------------------------------------
    # 3. 이미지 정보 출력
    # ------------------------------------------------------------
    print(
        f"[SUCCESS] OpenCV 이미지 읽기 성공: "
        f"{image_path}"
    )

    print(
        f"[INFO] image shape = "
        f"{image_bgr.shape}"
    )

    height, width, channels = image_bgr.shape

    center_pixel = image_bgr[
        height // 2,
        width // 2,
    ]

    print(
        f"[INFO] center pixel BGR = "
        f"{center_pixel}"
    )


if __name__ == "__main__":
    main()