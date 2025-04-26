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


# Điều chỉnh lấy thông tin input từ json N8N

from module_luong_core_v1_2 import extract_timer_time_luu_positions

def extract_inputs_from_json(data: dict):
    """
    Trích xuất dữ liệu từ JSON để phục vụ pipeline Cloud.
    
    Trả ra:
    - route_steps_by_robot: dict[str, list[dict]]
    - base_timer_dict: dict[str, int]
    - time_luu_dict: dict[str, int]
    - marker_docx_path: str ('from_json')
    - selected_robots: list[str]
    """

    # 1. Parse route
    route_steps_by_robot = data.get("route", {})
    if not isinstance(route_steps_by_robot, dict):
        raise ValueError("Dữ liệu 'route' trong JSON không hợp lệ!")

    # 2. Parse base_timer_dict
    base_timer_config = data.get("base_timer_config", {})
    base_timer_dict = {}

    for pos, value in base_timer_config.items():
        if isinstance(value, dict) and "timer_base" in value:
            base_timer_dict[pos] = int(value["timer_base"])
        elif isinstance(value, int):
            base_timer_dict[pos] = value
        else:
            base_timer_dict[pos] = 0  # Mặc định nếu dữ liệu không chuẩn

    # 3. Tự sinh time_luu_dict từ route_steps_by_robot
    time_luu_dict = {}
    for robot, steps in route_steps_by_robot.items():
        if not isinstance(steps, list):
            raise ValueError(f"Dữ liệu steps của robot {robot} không phải list!")

        timer_luu_positions = extract_timer_time_luu_positions(steps)
        for pos in timer_luu_positions:
            if pos not in time_luu_dict:
                time_luu_dict[pos] = 0  # Giá trị mặc định 0, sau này pipeline xử lý gán giá trị chuẩn

    # 4. marker_docx_path: set mặc định
    marker_docx_path = "from_json"

    # 5. selected_robots: từ keys của route
    selected_robots = list(route_steps_by_robot.keys())

    return route_steps_by_robot, base_timer_dict, time_luu_dict, marker_docx_path, selected_robots

