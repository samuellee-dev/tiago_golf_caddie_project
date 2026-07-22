from vision.camera_targeting import CameraTargeting


def main():
    """
    CameraTargeting의 방향 판단 기능을
    MuJoCo 없이 단독으로 테스트한다.
    """

    targeting = CameraTargeting(
        image_width=1280,
        dead_zone=50,
    )

    test_centers = [
        None,
        (300, 360),
        (620, 360),
        (640, 360),
        (700, 360),
        (1000, 360),
    ]

    for center in test_centers:
        result = targeting.decide_from_detection(center)

        print(
            f"target_center={center}, "
            f"detected={result.detected}, "
            f"direction={result.direction}, "
            f"error={result.center_error_normalized:.3f}"
        )


if __name__ == "__main__":
    main()