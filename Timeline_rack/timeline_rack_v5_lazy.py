import os
import sys
import pandas as pd
import re
from typing import Dict, Optional, Callable, List, Tuple

# Lấy thư mục gốc là timeline_rack
base_dir = os.path.dirname(os.path.abspath(__file__))
Modules_dir = os.path.join(base_dir, "Modules")

def parse_action(action: str):
    match = re.match(r"(\d+[DT])\s*→\s*(\d+[DT])", str(action))
    if match:
        return match.group(1).upper(), match.group(2).upper()
    return None, None

def build_action_db(df: pd.DataFrame, cc_name: str) -> pd.DataFrame:
    df = df.copy()
    df["CC"] = cc_name
    df["source"], df["dest"] = zip(*df["action"].apply(parse_action))
    return df.dropna(subset=["source", "dest"])

#def find_first_last_position_from_marker(df_cc1: pd.DataFrame) -> Tuple[str, str]:
#    ghi_chu_col = [col for col in df_cc1.columns if "ghi" in col.lower()][0]
#    df_cc1["source"], df_cc1["dest"] = zip(*df_cc1["action"].apply(parse_action))
#    first_pos = last_pos = None
#    for _, row in df_cc1.iterrows():
#        marker = str(row[ghi_chu_col]).lower()
#        match = re.search(r"vị trí (\d+d)", marker)
#        if not match:
#            continue
#        pos = match.group(1).upper()
#        if "nạp hàng" in marker and row["source"].upper() == pos:
#            first_pos = pos
#        elif "tháo hàng" in marker and row["dest"].upper() == pos:
#            last_pos = pos
#    if not first_pos or not last_pos:
#        raise ValueError("Không tìm thấy vị trí nạp/tháo hàng.")
#    return first_pos, last_pos

def extract_positions(action_db: pd.DataFrame, first_pos: str, last_pos: str) -> List[str]:
    visited = [first_pos]
    current = first_pos

    with open("log_extract_positions.txt", "w", encoding="utf-8") as log:
        log.write(f"🚀 Bắt đầu truy vết từ {first_pos} đến {last_pos}\n")

        while current != last_pos:
            xt = current.replace("D", "T")
            log.write(f"\n🔍 current = {current} → xt = {xt}\n")

            step2 = action_db[
                (action_db["source"] == xt) &
                (action_db["dest"].str.endswith("T")) &
                (action_db["dest"] != xt)
            ]

            if step2.empty:
                log.write(f"❌ Không tìm thấy bước từ {xt} → xT khác\n")
                break

            yt = step2.iloc[0]["dest"]
            yd = yt.replace("T", "D")

            log.write(f"✅ Tìm thấy: {xt} → {yt} → {yd}\n")
            visited.append(yd)
            current = yd

        log.write(f"\n✅ visited = {visited}\n")

    return visited

def process_position(
    pos: str,
    cc_pool: Dict[str, pd.DataFrame],
    current_cc: str,
    first_pos: str,
    last_pos: str,
    request_cc_fn: Callable[[int], Optional[pd.DataFrame]]
) -> Tuple[Optional[dict], str, bool]:
    df_current = cc_pool.get(current_cc)
    if df_current is None:
        return None, current_cc, True

    T_in = T_out = cc_in = cc_out = chuyển_cc = None

    if pos != first_pos:
        df_in = df_current[(df_current["dest"] == pos) & 
                           (df_current["source"] == pos.replace("D", "T"))]
        if not df_in.empty:
            T_in = df_in["end"].min()
            cc_in = current_cc

    if pos != last_pos:
        df_out = df_current[(df_current["source"] == pos) &
                            (df_current["dest"] == pos.replace("D", "T"))]
        if not df_out.empty:
            raw_out = df_out["start"].min()
            T_out = raw_out - 0 #sửa chửa cháy
            cc_out = current_cc

        if T_in is not None and T_out is not None and T_out < T_in:
            chuyển_cc = True
            cc_index = int(re.search(r"(\d+)", current_cc.lower()).group(1))
            next_df = request_cc_fn(cc_index + 1)
            if next_df is None:
                return None, current_cc, True
            next_cc_name = f"CC{cc_index + 1}"
            cc_pool[next_cc_name] = build_action_db(next_df, next_cc_name)
            current_cc = next_cc_name
            df_next = cc_pool[current_cc]
            df_out_next = df_next[(df_next["source"] == pos) &
                                  (df_next["dest"] == pos.replace("D", "T"))]
            if not df_out_next.empty:
                raw_out = df_out_next["start"].min()
                T_out = raw_out - 0 #sửa chửa cháy
                cc_out = current_cc

    thời_gian_lưu = T_out - T_in if T_in is not None and T_out is not None else None

    return {
        "Vị trí": pos,
        "T_in": T_in,
        "CC của T_in": cc_in,
        "T_out": T_out,
        "CC của T_out": cc_out,
        "Chuyển CC": chuyển_cc,
        "Thời gian lưu (s)": thời_gian_lưu
    }, current_cc, False

def timeline_rack_v5_lazy(request_cc_fn: Callable[[int], Optional[pd.DataFrame]]) -> pd.DataFrame:
    cc_pool = {}
    timeline_result = []

    # Bước 1: lấy CC1
    df_cc1 = request_cc_fn(1)
    if df_cc1 is None:
        raise ValueError("Không có dữ liệu CC1")

    cc_pool["CC1"] = build_action_db(df_cc1, "CC1")
    # ✅ Ghi nội dung cc_pool["CC1"] ra file log
    with open("log_cc_pool_CC1.txt", "w", encoding="utf-8") as f:
        f.write("📋 Nội dung cc_pool['CC1']:\n")
        f.write(cc_pool["CC1"].to_string(index=False))


    # Bước 2: xác định vị trí đầu/cuối
    # Thêm Modules vào sys.path nếu chưa có
    if Modules_dir not in sys.path:
        sys.path.insert(0, Modules_dir)
    from marker_utils import find_first_last_position_from_marker
    
    first_pos, last_pos = find_first_last_position_from_marker(df_cc1)
    print(f"✅ Marker xác định: Vị trí đầu = {first_pos}, Vị trí cuối = {last_pos}")

    # Bước 3: tạo danh sách các vị trí rack đi qua
    positions = extract_positions(cc_pool["CC1"], first_pos, last_pos)
    print(f"📦 Vị trí rack đi qua ({len(positions)} vị trí): {positions}")

    # Bước 4: duyệt từng vị trí (pos)
    current_cc = "CC1"      # gán cc đầu tiên luôn là 1. tự cập nhật khi chạy process_position
    i = 0
    while i < len(positions):
        pos = positions[i]
        result, current_cc, need_more = process_position(
            pos, cc_pool, current_cc, first_pos, last_pos, request_cc_fn
        )

        if need_more:
            next_cc_index = int(current_cc[2:]) + 1
            next_cc_name = f"CC{next_cc_index}"

            if next_cc_name not in cc_pool:
                next_df = request_cc_fn(next_cc_index)
                cc_pool[next_cc_name] = build_action_db(next_df, next_cc_name)

            current_cc = next_cc_name
            continue  # quay lại xử lý lại chính pos hiện tại

        if result:
            timeline_result.append(result)

        i += 1  # chỉ tăng khi đã xử lý xong pos

    # Bước 5: tạo DataFrame kết quả
    df_result = pd.DataFrame(timeline_result)

    # ✅ Đảm bảo thư mục 'output' nằm cùng cấp với file .bat tồn tại
    import os
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    # ✅ Ghi file Excel
    output_path = os.path.join(output_dir, "timeline_rack_lazy_result.xlsx")
    df_result.to_excel(output_path, index=False)
    print(f"✅ Đã lưu kết quả vào: {output_path}")

    return pd.DataFrame(timeline_result)
