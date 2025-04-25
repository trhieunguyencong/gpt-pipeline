import sys
from typing import Dict, List
import re
from collections import defaultdict
from typing import List, Dict
from docx import Document

# Hàm từ v3_1_fixed

import re

def extract_timer_time_luu_positions(route_steps):
    timer_time_luu_positions = []
    for step in route_steps:
        if "(vị trí" in step.lower() and "timer time lưu" in step.lower():
            dest = step.split("→")[-1].split("(")[0].strip()
            timer_time_luu_positions.append(dest)
    return timer_time_luu_positions

def extract_timer_positions_corrected(route_steps, base_timer_dict=None):
    timer_dict = {}
    for step in route_steps:
        if isinstance(step, str):
            match = re.search(r"vị trí\s*(\w+):\s*timer", step.lower())
            if match:
                pos = match.group(1).upper()
                if base_timer_dict and pos in base_timer_dict:
                    timer_dict[pos] = base_timer_dict[pos]
                else:
                    timer_dict[pos] = 0
    return timer_dict



# ============================== VERSION UPDATE ==============================
# ✅ Phiên bản cập nhật theo format word mới (ver: Mar 2025)
# ✅ Mỗi file docx là 1 luồng duy nhất
# ✅ Trích route theo từng robot: R1, R2, R3...
# ✅ Không còn xử lý bảng hay phân tích nhiều luồng trong 1 file
# ===========================================================================

# ============================== VERSION UPDATE ==============================
# ✅ Phiên bản cập nhật theo format word mới (ver: Mar 2025)
# ✅ Trích route từ đoạn văn bản, không dùng bảng
# ✅ Trả về định dạng cũ: Dict[str, List[str]] (mỗi step là một dòng string)
# ===========================================================================

def extract_routes_by_luong_from_docx(docx_path):
    from docx import Document
    import re

    doc = Document(docx_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    result = {}
    current_robot = None
    in_route = False

    for line in paragraphs:
        # Xác định bắt đầu robot
        if re.match(r'^R[1-9]$', line):
            current_robot = line
            result[current_robot] = []
            continue

        if line.lower().startswith("bắt đầu"):
            in_route = True
            continue
        elif line.lower().startswith("kết thúc"):
            in_route = False
            continue

        if in_route and current_robot:
            if line.startswith("#route_"):
                result[current_robot].append(line.strip())
            else:
                match = re.match(r'(\w+)\s*→\s*(\w+)(.*)', line)
                if match:
                    source, dest, note = match.groups()
                    line_str = f"{source} → {dest}"
                    if note.strip():
                        line_str += f" {note.strip()}"
                    result[current_robot].append(line_str)

    if not result:
        raise ValueError("Không tìm thấy dữ liệu route trong file Word.")

    return result
import pandas as pd

def extract_timer_config_from_excel(excel_path: str):
    """
    Đọc file Excel chứa timer và timer time lưu, trả về hai dict:
    - base_timer_dict: cho timer thông thường
    - time_luu_dict: cho marker 'timer time lưu'
    """
    df = pd.read_excel(excel_path)

    # Làm sạch dữ liệu
    df["marker"] = df["marker"].astype(str).str.strip().str.upper()
    df["loai_timer"] = df["loai_timer"].astype(str).str.strip().str.lower()
    df["gia_tri_thoi_gian"] = pd.to_numeric(df["gia_tri_thoi_gian"], errors="coerce")

    # Tạo dict cho timer_base
    base_timer_dict = {
        row["marker"]: int(row["gia_tri_thoi_gian"])
        for _, row in df[df["loai_timer"] == "timer_base"].iterrows()
    }

    # Tạo dict cho timer_time_luu
    time_luu_dict = {
        row["marker"]: int(row["gia_tri_thoi_gian"])
        for _, row in df[df["loai_timer"] == "timer_time_luu"].iterrows()
    }

    return base_timer_dict, time_luu_dict


def default_robot_classification(all_routes: dict) -> dict:
    """
    Phân loại robot theo thứ tự xuất hiện trong all_routes.
    Không phân biệt R1 là robot dùng chung – tất cả đều xử lý như nhau.
    """
    classification = {}
    for idx, rb in enumerate(all_routes.keys()):
        classification[f'robot_{idx+1}'] = rb
    return classification
