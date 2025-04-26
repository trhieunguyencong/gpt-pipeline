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
def extract_inputs_from_json(data: dict):
    """
    Trích xuất dữ liệu từ JSON để phục vụ pipeline Cloud.

    Trả ra:
    - route_steps_by_robot: dict[str, list[str]] (đã convert về dạng "source → dest (marker)")
    - base_timer_dict: dict[str, int]
    - time_luu_dict: dict[str, int]
    - marker_docx_path: str ('from_json')
    - selected_robots: list[str]
    """

    # --- Hàm phụ để convert step ---
    def convert_route_steps_object_to_strings(route_steps_by_robot_obj):
        route_steps_by_robot_str = {}

        for robot, robot_data in route_steps_by_robot_obj.items():
            steps = robot_data.get("steps", [])
            step_strings = []

            for step in steps:
                source = step.get("source")
                dest = step.get("dest")
                marker = step.get("marker")
                special_tag = step.get("special_tag")

                # Nếu là dòng đặc biệt (#route_if, #route_else, #route_endif)
                if special_tag:
                    step_strings.append(special_tag.strip())
                    continue

                if source and dest:
                    line = f"{source} → {dest}"
                    if marker:
                        line += f" {marker.strip()}"
                    step_strings.append(line)
            
            route_steps_by_robot_str[robot] = step_strings

        return route_steps_by_robot_str

    # 1. Parse route
    raw_route_steps_by_robot = data.get("route", {})
    if not isinstance(raw_route_steps_by_robot, dict):
        raise ValueError("Dữ liệu 'route' trong JSON không hợp lệ!")

    # 1.1. Convert route object thành list strings
    route_steps_by_robot = convert_route_steps_object_to_strings(raw_route_steps_by_robot)

    # 2&3. Parse base_timer_dict và time_luu_dict
    base_timer_config = data.get("base_timer_config", {})
    base_timer_dict = {}
    time_luu_dict = {}
    
    for pos, value in base_timer_config.items():
        if isinstance(value, dict):
            if "timer_base" in value:
                base_timer_dict[pos] = int(value["timer_base"])
            if "timer_time_luu" in value:
                time_luu_dict[pos] = int(value["timer_time_luu"])
        elif isinstance(value, int):
            base_timer_dict[pos] = value

    # 4. marker_docx_path: set mặc định
    marker_docx_path = "from_json"

    # 5. selected_robots: từ keys của route
    selected_robots = list(route_steps_by_robot.keys())

    return route_steps_by_robot, base_timer_dict, time_luu_dict, marker_docx_path, selected_robots

