from pathlib import Path

import imageio.v2 as imageio


def main():
    # ------------------------------------------------------------
    # 1. 입력 프레임 폴더와 출력 동영상 경로
    # ------------------------------------------------------------
    frame_dir = Path(
        "outputs/camera/follow_sequence"
    )

    output_video = Path(
        "outputs/camera/follow_sequence.mp4"
    )

    # ------------------------------------------------------------
    # 2. frame 이미지 목록 불러오기
    # ------------------------------------------------------------
    frame_paths = sorted(
        frame_dir.glob("frame_*.png")
    )

    if not frame_paths:
        raise FileNotFoundError(
            f"frame 이미지를 찾을 수 없습니다: {frame_dir}"
        )

    # ------------------------------------------------------------
    # 3. 모든 frame 이미지 읽기
    # ------------------------------------------------------------
    frames = []

    for path in frame_paths:
        frame = imageio.imread(path)
        frames.append(frame)

    # ------------------------------------------------------------
    # 4. MP4 동영상 저장
    # ------------------------------------------------------------
    imageio.mimsave(
        output_video,
        frames,
        fps=5,
    )

    print(
        f"[SUCCESS] 동영상 저장 완료: {output_video}"
    )

    print(
        f"[INFO] frame count = {len(frames)}"
    )


if __name__ == "__main__":
    main()