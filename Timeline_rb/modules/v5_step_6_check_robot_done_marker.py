from timeline_rb_v4_3_1 import generate_timeline_rb_v4_3
from module_luong_core_v1_2 import extract_timer_positions_corrected

import re

def extract_user_defined_timers_from_route_steps(route_steps: list[str]) -> dict[str, int]:
    """
    Trích xuất timer từ các bước có định dạng (Vị trí XX: timer(YY))
    - Chỉ lấy những timer có chứa số.
    - Bỏ qua marker timer không có số.
    """
    timer_dict = {}

    for step in route_steps:
        # Chỉ lấy timer có số cụ thể
        match = re.search(r"\(Vị trí\s+(\w+):\s*timer\((\d+)\)", step, re.IGNORECASE)
        if match:
            position = match.group(1).upper()
            timer_val = int(match.group(2))
            timer_dict[position] = timer_val
        # Bỏ qua marker timer không có số, không raise nữa
    return timer_dict


def check_robot_done_and_generate_v4(
    robot: str,
    processed_markers_by_robot: dict,
    markers_by_robot: dict,
    route_steps_by_robot: dict,
    base_timer_dict: dict = None,
    start_time: int = 0
):

    # ✅ Ghi log robot được xử lý tại Step6
    with open("log_step6_robot.txt", "a", encoding="utf-8") as f:
        f.write(f"[STEP6] Đang xử lý robot: {robot}\n")

    """
    ✅ Step 6 mở rộng:
    - Kiểm tra robot đã xử lý xong marker chưa.
    - Nếu xong, gọi V4 để tính timeline riêng cho robot đó.

    Trả về:
        - None nếu robot chưa xử lý xong
        - timeline_df nếu đã xử lý xong và V4 được gọi
    """
    # Kiểm tra robot đã xử lý xong marker chưa
    expected = [m["marker_text"] for m in markers_by_robot.get(robot, [])]
    actual = [m["marker_text"] for m in processed_markers_by_robot.get(robot, [])]
    if set(actual) != set(expected):
        return None  # chưa xong

    # Nếu đã xử lý xong, gọi V4 để tính timeline
    route_steps = route_steps_by_robot[robot]
    timer_positions = extract_timer_positions_corrected(route_steps)
    user_defined_timers_from_route = extract_user_defined_timers_from_route_steps(route_steps)
    print(f"[LOG] 🔍 Timer từ route ({robot}):", user_defined_timers_from_route)
    user_defined_timers = base_timer_dict.copy()
    print(f"[LOG] 📋 Timer gốc từ base_timer_dict ({robot}):", user_defined_timers)
    user_defined_timers.update(user_defined_timers_from_route)
    print(f"[LOG] ✅ Timer sau khi gộp ({robot}):", user_defined_timers)

    timeline_df = generate_timeline_rb_v4_3(
        robot_name=robot,
        route_steps=route_steps,
        timer_positions=timer_positions,
        user_defined_timers=user_defined_timers,
        start_time=start_time
    )
    timeline_df["robot"] = robot

    with open("log_timeline_df_sttep6.txt", "a", encoding="utf-8") as f:
        f.write(f"🧾 Timeline V4 cho robot {robot}:\n")
        f.write(timeline_df.to_string(index=False))
        f.write("\n" + "="*60 + "\n\n")

    return timeline_df

def check_all_robot_done_marker(processed_markers_by_robot: dict, markers_by_robot: dict) -> bool:
    """
    ✅ Hàm bổ sung cho step 6 – Kiểm tra toàn bộ robot đã xử lý xong marker hay chưa.
    
    Dùng trong vòng lặp (loop), thay thế việc gọi từng robot riêng lẻ.
    
    Trả về:
        - True nếu tất cả robot đã xử lý xong.
        - False nếu còn ít nhất một robot chưa xử lý xong.
    """
    for rb in markers_by_robot:
        full_set = set(marker["marker_text"] for marker in markers_by_robot.get(rb, []))
        done_set = set(m["marker_text"] for m in processed_markers_by_robot.get(rb, []))
        if full_set != done_set:
            return False
    return True
