import re
import sys
import pandas as pd  # ✅ bổ sung để dùng to_numeric

# VERSION: v2.4+
# STEP 4 – Tính timer thực tế tại marker "timer time lưu" sử dụng toàn bộ timeline_all
# Tăng cường độ chặt: source phải == marker.replace("D", "T")



def find_robot_hạ_vào_marker(timeline_all: dict, marker: str, T_den: int, T_den_prev: int = None):
    expected_source = marker.replace("D", "T")
    for rb, df in timeline_all.items():
        df["start"] = pd.to_numeric(df["start"], errors="coerce")
        df["end"] = pd.to_numeric(df["end"], errors="coerce")
        df = df.dropna(subset=["start", "end"])  # ✅ loại bỏ dòng lỗi cho cả 2 nhánh

        if T_den_prev is None:
            if "D" in marker:
                rows = df[
                    (df["dest"] == marker) &
                    (df["source"] == expected_source) &
                    (df["action"].str.contains("→")) &
                    (df["end"] <= T_den)
                ]
            else:
                rows = df[
                    (df["dest"] == marker) &
                    (df["source"] == expected_source) &
                    (df["action"].str.contains("→")) &
                    (df["start"] <= T_den)
                ]
        else:
            if "D" in marker:
                rows = df[
                    (df["dest"] == marker) &
                    (df["source"] == expected_source) &
                    (df["action"].str.contains("→")) &
                    (df["end"] > T_den_prev) &
                    (df["end"] <= T_den)
                ]
            else:
                rows = df[
                    (df["dest"] == marker) &
                    (df["source"] == expected_source) &
                    (df["action"].str.contains("→")) &
                    (df["start"] > T_den_prev) &
                    (df["start"] <= T_den)
                ]
        if not rows.empty:
            return rb, rows
    return None, None  # Không tìm thấy



def calculate_timer_time_luu_from_all(
    robot: str,
    marker_full_text: str,
    T_den: int,
    timeline_all: dict,
    time_luu_dict: dict,
    cc_label: str,
    output_dir: str = "output"
):
    cc_label = str(cc_label)  # 🔒 Chuẩn hóa để so sánh chính xác

    from sup_marker_utils import find_T_in

    match = re.search(r"vị trí\s+(\d+[TD])", marker_full_text, re.IGNORECASE)
    if not match:
        raise ValueError(f"❌ Không tìm thấy vị trí trong marker_text: {marker_full_text}")
    marker = match.group(1).upper()

    # Tìm robot đã thực hiện bước hạ bằng wrapper hỗ trợ xuyên CC
    timeline_current = timeline_all
    rb_hạ, rows_in = find_T_in(timeline_current, cc_label, marker, T_den, output_dir, robot)

    if marker not in time_luu_dict:
        raise ValueError(f"❌ Không có giá trị time_luu yêu cầu cho marker {marker}")

    time_luu = time_luu_dict[marker]

    if rows_in is None:
        if cc_label == "1":
            # ✅ CC1 – không có bước hạ → rack đã nằm sẵn
            return {
                "robot": robot,
                "marker": marker,
                "marker_full": marker_full_text,
                "T_in": None,
                "T_den": T_den,
                "time_luu": time_luu,
                "time_da_nam": None,
                "timer_thuc_te": 0
            }
        else:
            raise ValueError(f"[LỖI STEP4] Không tìm thấy bước hạ vào {marker} trong timeline của CC {cc_label}")

    T_in = rows_in["end"].max()
    time_da_nam = T_den - T_in
    timer_thuc_te = max(0, time_luu - time_da_nam)

    return {
        "robot": robot,
        "marker": marker,
        "marker_full": marker_full_text,
        "T_in": T_in,
        "T_den": T_den,
        "time_luu": time_luu,
        "time_da_nam": time_da_nam,
        "timer_thuc_te": timer_thuc_te
    }

