import sys

# VERSION: v1.6 - ĐÃ CẢI TIẾN: Dùng lại kết quả marker từ Step 2 thay vì gọi lại get_next_marker()

def update_t_den_by_robot(current_marker_by_robot, timeline_by_robot):
    """
    Với mỗi robot:
    - Đã biết marker đang xử lý (do Step 2 đã xác định)
    - Đã có timeline bán phần ứng với marker đó

    Trả về:
        {
            "R1": ("5D: timer time lưu", T_đến),
            ...
        }
    """
    t_den_by_robot = {}
    for rb in current_marker_by_robot:
        marker_full = current_marker_by_robot[rb]
        timeline_df = timeline_by_robot.get(rb)
        if marker_full and timeline_df is not None and not timeline_df.empty:
            T_den = timeline_df["end"].max()  # lấy T_đến từ timeline bán phần
            t_den_by_robot[rb] = (marker_full, T_den)
    return t_den_by_robot


def select_next_marker(t_den_by_robot: dict):
    """
    Chọn marker có T_đến nhỏ nhất trong toàn hệ
    Nếu chỉ còn 1 robot có marker → trả thẳng
    """
    if not t_den_by_robot:
        return None

    if len(t_den_by_robot) == 1:
        rb, (marker, T_den) = list(t_den_by_robot.items())[0]
        return rb, marker, T_den

    candidates = [(rb, marker, T_den) for rb, (marker, T_den) in t_den_by_robot.items()]
    rb_min, marker_min, T_den_min = min(candidates, key=lambda x: x[2])
    return rb_min, marker_min, T_den_min
