import sys

# MODULE: sup_marker_utils.py
# 📦 Chứa các hàm tiện ích hỗ trợ xử lý marker trong pipeline V5

def get_next_marker(rb, markers_by_robot, processed_markers_by_robot):
    """
    Trả về marker kế tiếp cần xử lý của robot `rb`, dựa trên thứ tự trong Step 1.

    Parameters:
        rb (str): Tên robot
        markers_by_robot (dict): Danh sách marker đã quét được từ Step 1, đúng thứ tự route
        processed_markers_by_robot (dict): Danh sách marker đã xử lý từng robot

    Returns:
        str | None: Marker kế tiếp cần xử lý hoặc None nếu đã xử lý hết
    """
    all_markers = markers_by_robot.get(rb, [])
    processed = processed_markers_by_robot.get(rb, [])
    if len(processed) >= len(all_markers):
        return None
    return all_markers[len(processed)]


# === Wrapper xuyên CC để tìm T_in ===

import os
import json
import pandas as pd

def load_timeline_from_previous_cc(cc_label: str, output_dir: str = "output") -> dict[str, pd.DataFrame]:
    import pandas as pd
    import os

    REQUIRED_COLUMNS = ["start", "end", "source", "dest", "action"]
    cc_prev = int(cc_label) - 1
    file_path = os.path.join(output_dir, f"timeline_output_cc{cc_prev}.xlsx")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file timeline_output_cc{cc_prev}.xlsx")

    xl = pd.ExcelFile(file_path)
    timeline_by_robot = {}

    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)

        # Kiểm tra các cột bắt buộc
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                raise ValueError(f"Lỗi: Sheet '{sheet_name}' trong file CC{cc_prev} thiếu cột bắt buộc: '{col}'")

        # Chuẩn hóa kiểu dữ liệu
        df["start"] = pd.to_numeric(df["start"], errors="coerce")
        df["end"] = pd.to_numeric(df["end"], errors="coerce")
        df = df.dropna(subset=["start", "end"])
        df = df.sort_values("start")

        timeline_by_robot[sheet_name] = df

    return timeline_by_robot

def find_T_in_chia_2_vung(marker: str, T_den: int, T_den_prev: int, timeline_current: dict, timeline_prev: dict):
    from v5_step_4_calculate_timer import find_robot_hạ_vào_marker

    # Quét vùng 1: [T_den_prev, T_den] trong CC hiện tại
    rb, rows = find_robot_hạ_vào_marker(timeline_current, marker, T_den, T_den_prev)
    if rb is not None:
        return rb, rows

    # Quét vùng 2: [T_den_prev, ∞] trong CC trước
    rb, rows = find_robot_hạ_vào_marker(timeline_prev, marker, float('inf'), T_den_prev)
    return rb, rows

def find_T_in(timeline_current: dict, cc_label: str, marker: str, T_den: int, output_dir: str = "output", robot: str = None):
    cc_int = int(cc_label)

    # Nếu đang xử lý CC1 → không cần tracker, chỉ tra trong CC hiện tại
    if cc_int == 1:
        from v5_step_4_calculate_timer import find_robot_hạ_vào_marker
        return find_robot_hạ_vào_marker(timeline_current, marker, T_den)

    # Với CC > 1 → bắt buộc phải có file tracker
    t_den_path = os.path.join(output_dir, "t_den_tracker.json")
    if not os.path.exists(t_den_path):
        raise FileNotFoundError(f"Thiếu file tracker: {t_den_path} (bắt buộc với CC > 1)")

    # Đọc T_den_prev từ tracker
    with open(t_den_path, "r", encoding="utf-8") as f:
        t_den_data = json.load(f)

    cc_prev = int(cc_label) - 1                      # 🔧 Thêm dòng này để phục vụ debug
    cc_prev_key = f"CC{cc_prev}"                     # 🔒 Khóa chính xác trong file tracker
    T_den_prev = t_den_data.get(cc_prev_key, {}).get(robot, {}).get(marker, None)

    if T_den_prev is None:
        raise ValueError(f"T_den_prev không tồn tại trong tracker cho marker {marker} tại {cc_prev_key}")

    # Load timeline của CC trước
    timeline_prev = load_timeline_from_previous_cc(cc_label, output_dir)

    # Tìm theo chia 2 vùng
    return find_T_in_chia_2_vung(marker, T_den, T_den_prev, timeline_current, timeline_prev)

