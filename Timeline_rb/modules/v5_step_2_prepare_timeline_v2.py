import sys

# VERSION: v2.2
# ✅ Tách hàm cut_route_to_marker() để dễ bảo trì và test

from sup_marker_utils import get_next_marker
from timeline_rb_v4_3_1 import generate_timeline_rb_v4_3
from module_luong_core_v1_2 import extract_timer_positions_corrected, extract_timer_time_luu_positions

def parse_source_dest(step: str) -> tuple:
    if "→" not in step:
        return None, None
    move_part = step.split("→")
    source = move_part[0].strip().split("(")[0].strip()
    dest = move_part[1].strip().split("(")[0].strip()
    return source.upper(), dest.upper()

def cut_route_to_marker(route: list[str], marker: str) -> list[str]:
    """
    Cắt đoạn route từ đầu đến dòng chứa marker theo vị trí `marker`.
    Chỉ cắt nếu dòng đó thật sự là dòng chứa marker – xác định bằng từ khóa như "timer time lưu", "chờ đồng bộ".

    - Nếu marker trùng với `dest` trong bước di chuyển → giữ lại dòng này (cắt tới i+1).
    - Nếu marker trùng với `source` trong bước di chuyển → cắt trước dòng này (cắt tới i).

    Trả về đoạn route con phù hợp để tính timeline trước khi xử lý marker.
    """
    keywords = ["timer time lưu", "chờ đồng bộ"]  # Có thể mở rộng về sau
    cut_steps = []
    found = False
    marker = marker.upper().strip()

    for i, step in enumerate(route):
        step_lower = step.lower()
        if any(kw in step_lower for kw in keywords):
            source, dest = parse_source_dest(step)
            if dest == marker:
                cut_steps = route[:i+1]
                found = True
                break
            elif source == marker:
                cut_steps = route[:i]
                found = True
                break

    if not found:
        raise ValueError(f"❌ Không tìm thấy dòng chứa marker '{marker}' có từ khóa đặc trưng trong route")

    return cut_steps

def prepare_timeline_v2(route_steps_by_robot: dict,
                        timeline_by_robot: dict,
                        markers_by_robot: dict,
                        processed_markers_by_robot: dict,
                        robot_to_run=None,
                        base_timer_dict: dict = None,
                        start_time=0) -> dict:
    new_timeline_by_robot = {}

    robot_list = [robot_to_run] if robot_to_run else markers_by_robot.keys()
    for rb in robot_list:
        # Nếu đã xử lý hết marker thì bỏ qua
        next_marker = get_next_marker(rb, markers_by_robot, processed_markers_by_robot)
        if not next_marker:
            continue

        steps = route_steps_by_robot[rb]
        marker_pos = next_marker["position"]
        print(f"[DEBUG] ✅ Robot: {rb} | Pos: {marker_pos}")

        cut_steps = cut_route_to_marker(steps, marker_pos)

        # Tính timeline đoạn này
        timer_positions = extract_timer_positions_corrected(cut_steps)
        timeline_df = generate_timeline_rb_v4_3(
            robot_name=rb,
            route_steps=cut_steps,
            timer_positions=timer_positions,
            move_time=10,
            tdt_time=5,
            user_defined_timers=base_timer_dict,
            start_time=start_time
        )

        # ✅ GHI ĐÈ timeline đã có (KHÔNG gộp)
        timeline_by_robot[rb] = timeline_df

        # ✅ Ghi log timeline từng vòng nếu muốn theo dõi
        if "timeline_logger_by_robot" in globals():
            if rb not in timeline_logger_by_robot:
                timeline_logger_by_robot[rb] = []
            timeline_logger_by_robot[rb].append(timeline_df.copy())

        new_timeline_by_robot[rb] = timeline_by_robot[rb]

    
    current_marker_by_robot = {
        rb: get_next_marker(rb, markers_by_robot, processed_markers_by_robot)
        for rb in route_steps_by_robot
    }
    return timeline_by_robot, current_marker_by_robot
