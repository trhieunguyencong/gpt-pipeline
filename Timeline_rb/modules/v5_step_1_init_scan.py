from typing import Dict, List, Tuple, Any
import re
import sys
import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ✅ ĐÃ SỬA: Thêm robot_name vào lời gọi generate_timeline_rb_v4_3(rb, ...)

# VERSION: v1.2
# ✅ Hỗ trợ thứ tự marker theo dòng xuất hiện trong route
# ✅ Trả về markers_by_robot có thứ tự logic chính xác


from module_luong_core_v1_2 import extract_timer_positions_corrected
from timeline_rb_v4_3_1 import generate_timeline_rb_v4_3
from parse_marker_wait_sync import parse_marker_wait_sync

def scan_markers(route_steps_by_robot: Dict[str, List[str]]) -> Tuple[
    Dict[str, List[Dict[str, Any]]],
    Dict[str, List[str]],
    List[str]
]:
    """
    Phiên bản mới: trích xuất toàn bộ marker ("timer time lưu", "chờ đồng bộ") vào markers_by_robot

    Returns:
        - markers_by_robot: dict[robot, list[marker_obj]]
        - processed_markers_by_robot: dict[robot, list[str]] (rỗng ban đầu)
        - robots_sach_marker: list[str]
    """
    markers_by_robot = {}
    processed_markers_by_robot = {}
    robots_sach_marker = []

    for rb, steps in route_steps_by_robot.items():
        marker_objs = []

        for step in steps:
            step_lower = step.lower()

            # Case 1: timer time lưu
            if "(vị trí" in step_lower and "timer time lưu" in step_lower:
                match = re.search(r"vị trí\s+(\d+[TD])", step, re.IGNORECASE)
                if match:
                    pos = match.group(1).upper()
                    marker_objs.append({
                        "marker_text": step.strip(),
                        "type": "timer_time_luu",
                        "position": pos,
                        "parsed_data": None
                    })

            # Case 2: chờ đồng bộ
            elif "(vị trí" in step_lower and "chờ đồng bộ" in step_lower:
                match_pos = re.search(r"vị trí\s+(\d+[TD])", step, re.IGNORECASE)
                if match_pos:
                    pos = match_pos.group(1).upper()
                    parsed = parse_marker_wait_sync(step)
                    if parsed:
                        marker_objs.append({
                            "marker_text": step.strip(),
                            "type": "wait_sync",
                            "position": pos,
                            "parsed_data": parsed
                        })

        if marker_objs:
            markers_by_robot[rb] = marker_objs
            processed_markers_by_robot[rb] = []
        else:
            robots_sach_marker.append(rb)

    print("📌 DEBUG - MARKERS BY ROBOT:")
    for rb, markers in markers_by_robot.items():
        print(f"🔍 Robot: {rb}")
        for i, m in enumerate(markers):
            print(f"  [{i}] Pos = {m['position']}, Type = {m['type']}, Marker = {m['marker_text']}")

    return markers_by_robot, processed_markers_by_robot, robots_sach_marker


def handle_clean_robots_v1(robots_sach_marker, route_steps_by_robot, timer_dict):
    """
    Với các robot không có marker "timer time lưu", gọi V4.3 để tính toàn bộ timeline.
    """
    timeline_by_robot = {}
    for rb in robots_sach_marker:
        steps = route_steps_by_robot[rb]
        timer_positions = extract_timer_positions_corrected(steps)
        timeline_by_robot[rb] = generate_timeline_rb_v4_3(
            robot_name=rb,
            route_steps=steps,
            timer_positions=timer_positions,
            move_time=10,
            tdt_time=5,
            user_defined_timers=None
        )
    return timeline_by_robot





def handle_clean_robots(
    robots_sach_marker,
    route_steps_by_robot,
    base_timer_dict=None,
    start_time=0
):
    """
    Phiên bản cải tiến hỗ trợ truyền base_timer_dict – dùng cho pipeline V5

    Args:
        robots_sach_marker (list): danh sách robot không còn marker "timer time lưu"
        route_steps_by_robot (dict): route gốc của từng robot
        base_timer_dict (dict): dict chứa các timer cố định (VD: {"2D": 40, "5D": 60, ...})

    Returns:
        timeline_by_robot (dict): timeline đầy đủ của các robot sạch marker
    """
    from timeline_rb_v4_3_1 import generate_timeline_rb_v4_3
    from module_luong_core_v1_2 import extract_timer_positions_corrected

    timeline_by_robot = {}
    for rb in robots_sach_marker:
        route_steps = route_steps_by_robot[rb]
        timer_positions = extract_timer_positions_corrected(route_steps)
        timeline_df = generate_timeline_rb_v4_3(rb, route_steps, timer_positions, user_defined_timers=base_timer_dict, start_time=start_time)
        timeline_df["robot"] = rb
        timeline_by_robot[rb] = timeline_df
    return timeline_by_robot
