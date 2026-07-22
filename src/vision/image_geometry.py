def estimate_horizontal_direction(
    object_center_x: int,
    image_width: int,
    dead_zone: int = 50,
) -> str:
    """
    이미지 안에서 객체가 왼쪽, 중앙, 오른쪽 중
    어느 위치에 있는지 판단한다.

    Args:
        object_center_x:
            검출된 객체 중심의 x좌표

        image_width:
            입력 이미지의 전체 너비

        dead_zone:
            화면 중앙에서 CENTER로 판단할 허용 범위

    Returns:
        "LEFT", "CENTER", "RIGHT" 중 하나
    """

    image_center_x = image_width // 2

    if object_center_x < image_center_x - dead_zone:
        return "LEFT"

    if object_center_x > image_center_x + dead_zone:
        return "RIGHT"

    return "CENTER"

def normalize_center_error(
    object_center_x: int,
    image_width: int,
) -> float:
    """
    객체 중심 x좌표를
    화면 중심 기준 [-1, 1] 범위로 정규화한다.

    Returns:
        -1.0 : 화면 가장 왼쪽
         0.0 : 화면 중앙
         1.0 : 화면 가장 오른쪽
    """

    image_center_x = image_width / 2.0

    error_x = object_center_x - image_center_x

    normalized_error = error_x / image_center_x

    return float(normalized_error)