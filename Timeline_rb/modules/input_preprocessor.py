import sys

import os
from module_luong_core_v1_2 import (
    extract_routes_by_luong_from_docx,
    extract_timer_config_from_excel
)

def find_timer_config_file(input_dir: str) -> str:
    for fname in os.listdir(input_dir):
        if "timer" in fname.lower() and fname.endswith(".xlsx"):
            return os.path.join(input_dir, fname)
    raise FileNotFoundError("Không tìm thấy file timer config trong thư mục input.")

def find_docx_file(input_dir: str) -> str:
    for fname in os.listdir(input_dir):
        if fname.endswith(".docx"):
            return os.path.join(input_dir, fname)
    raise FileNotFoundError("Không tìm thấy file .docx trong thư mục input.")

def extract_inputs(input_dir: str):
    """
    Trả về:
        - route_steps_by_robot (dict)
        - base_timer_dict (dict)
        - time_luu_dict (dict)
        - luong (str)
        - marker_docx_path (str)
        - selected_robots (list)
    """
    marker_docx_path = find_docx_file(input_dir)
    timer_excel_path = find_timer_config_file(input_dir)

    base_timer_dict, time_luu_dict = extract_timer_config_from_excel(timer_excel_path)

    raw_routes = extract_routes_by_luong_from_docx(marker_docx_path)
    from route_condition_resolver import resolve_static_route_conditions
    route_steps_by_robot = resolve_static_route_conditions(raw_routes, base_timer_dict)

#    luong = list(raw_routes.keys())[0]


    selected_robots = list(route_steps_by_robot.keys())

    return route_steps_by_robot, base_timer_dict, time_luu_dict, marker_docx_path, selected_robots
