
import re
import pandas as pd
from typing import Optional, Dict

def parse_action(action):
    match = re.match(r"(\d+[DT])\s*→\s*(\d+[DT])", str(action))
    if match:
        return match.group(1).upper(), match.group(2).upper()
    return None, None

def build_action_db(timeline_data: Dict[str, pd.DataFrame]):
    all_rows = []
    for cc_name, df in timeline_data.items():
        df = df.copy()
        df["CC"] = cc_name
        df["source"], df["dest"] = zip(*df["Hành động"].apply(parse_action))
        all_rows.append(df)
    action_db = pd.concat(all_rows, ignore_index=True)
    return action_db.dropna(subset=["source", "dest"])

def find_first_last_position_from_marker(timeline_data: Dict[str, pd.DataFrame]):
    cc1_name = [name for name in timeline_data if "cc1" in name.lower()][0]
    df_cc1 = timeline_data[cc1_name].copy()
    ghi_chu_col = [col for col in df_cc1.columns if "ghi" in col.lower()][0]
    df_cc1["source"], df_cc1["dest"] = zip(*df_cc1["Hành động"].apply(parse_action))
    first_pos, last_pos = None, None
    for _, row in df_cc1.iterrows():
        marker = str(row[ghi_chu_col]).lower()
        match = re.search(r"vị trí (\d+d)", marker)
        if not match:
            continue
        pos = match.group(1).upper()
        if "nạp hàng" in marker and row["source"].upper() == pos:
            first_pos = pos
        elif "tháo hàng" in marker and row["dest"].upper() == pos:
            last_pos = pos
    if first_pos is None or last_pos is None:
        raise ValueError("Không tìm thấy marker chính xác cho nạp hoặc tháo hàng.")
    return first_pos, last_pos

def extract_positions_from_action_db(action_db: pd.DataFrame, first_pos: str, last_pos: str):
    visited = [first_pos]
    current = first_pos
    while current != last_pos:
        step1 = action_db[(action_db["source"] == current) &
                          (action_db["dest"] == current.replace("D", "T"))]
        if step1.empty:
            raise ValueError(f"Không tìm thấy bước nâng từ {current}")
        xt = current.replace("D", "T")
        step2 = action_db[(action_db["source"] == xt) &
                          (action_db["dest"].str.endswith("T")) &
                          (action_db["dest"] != xt)]
        if step2.empty:
            raise ValueError(f"Không tìm thấy bước chuyển ngang từ {xt}")
        yt = step2.iloc[0]["dest"]
        step3 = action_db[(action_db["source"] == yt) &
                          (action_db["dest"] == yt.replace("T", "D"))]
        if step3.empty:
            raise ValueError(f"Không tìm thấy bước hạ từ {yt}")
        yd = yt.replace("T", "D")
        visited.append(yd)
        current = yd
    return visited

def request_cc_by_index(index: int, timeline_data: Dict[str, pd.DataFrame]) -> Optional[pd.DataFrame]:
    for name in timeline_data:
        if f"cc{index}" in name.lower():
            df = timeline_data[name].copy()
            df["source"], df["dest"] = zip(*df["Hành động"].apply(parse_action))
            df["CC"] = name
            return df
    return None

def process_position(pos, cc_pool, current_cc, first_pos, last_pos, timeline_data):
    df_current = cc_pool.get(current_cc)
    if df_current is None:
        return None, current_cc, False

    T_in = T_out = cc_in = cc_out = chuyển_cc = None

    if pos != first_pos:
        df_in = df_current[(df_current["dest"] == pos) &
                           (df_current["source"] == pos.replace("D", "T"))]
        if not df_in.empty:
            T_in = df_in["Thời điểm (s)"].min()
            cc_in = current_cc

    if pos != last_pos:
        df_out = df_current[(df_current["source"] == pos) &
                            (df_current["dest"] == pos.replace("D", "T"))]
        if not df_out.empty:
            raw_out = df_out["Thời điểm (s)"].min()
            T_out = raw_out - 10
            cc_out = current_cc

        if T_in is not None and T_out is not None and T_out < T_in:
            chuyển_cc = True
            cc_index_match = re.search(r"cc(\d+)", current_cc.lower())
            if not cc_index_match:
                return "NEED_MORE_DATA", current_cc, True
            cc_index = int(cc_index_match.group(1))
            next_df = request_cc_by_index(cc_index + 1, timeline_data)
            if next_df is None:
                return "NEED_MORE_DATA", current_cc, True
            next_cc_name = next_df["CC"].iloc[0]
            cc_pool[next_cc_name] = next_df
            current_cc = next_cc_name
            df_next = next_df
            df_out_next = df_next[(df_next["source"] == pos) &
                                  (df_next["dest"] == pos.replace("D", "T"))]
            if not df_out_next.empty:
                raw_out = df_out_next["Thời điểm (s)"].min()
                T_out = raw_out - 10
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

def timeline_rack_v5(timeline_data: Dict[str, pd.DataFrame]):
    cc_pool = {}
    timeline_result = []
    first_pos, last_pos = find_first_last_position_from_marker(timeline_data)
    initial_cc = [name for name in timeline_data if "cc1" in name.lower()][0]
    cc_pool[initial_cc] = build_action_db({initial_cc: timeline_data[initial_cc]})
    current_cc = initial_cc
    positions = extract_positions_from_action_db(cc_pool[initial_cc], first_pos, last_pos)

    for pos in positions:
        result, current_cc, need_more = process_position(pos, cc_pool, current_cc, first_pos, last_pos, timeline_data)
        if need_more:
            print(f"DỪNG TẠI {pos} – CẦN NẠP THÊM DỮ LIỆU CC")
            break
        if result:
            timeline_result.append(result)

    return pd.DataFrame(timeline_result)
