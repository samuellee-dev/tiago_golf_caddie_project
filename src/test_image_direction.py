from vision.image_geometry import estimate_horizontal_direction


def main():
    image_width = 1280

    test_points = [
        300,
        620,
        640,
        700,
        1000,
    ]

    for x in test_points:
        direction = estimate_horizontal_direction(
            object_center_x=x,
            image_width=image_width,
            dead_zone=50,
        )

        print(
            f"x={x:4d} "
            f"→ direction={direction}"
        )


if __name__ == "__main__":
    main()