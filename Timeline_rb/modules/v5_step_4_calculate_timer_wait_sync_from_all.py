import os
import sys

def calculate_timer_wait_sync_from_all(
    robot: str,
    marker_obj: dict,
    T_den: int,
    timeline_all: dict,
    cc_label: str,
    log_dir: str = None
) -> dict:
    """
    Tính toán timer_thuc_te cho marker loại "wait_sync"
    """

    parsed = marker_obj["parsed_data"]
    target_rb = parsed["robot"]
    source = parsed["source"].strip().upper()
    dest = parsed["dest"].strip().upper()
    trigger_mode = parsed.get("trigger") or parsed.get("trigger_time")

    if trigger_mode not in ("start", "end"):
        raise ValueError(f"❌ trigger_mode không hợp lệ: {trigger_mode}")

    # Tìm bước trigger trong timeline của robot kích hoạt
    timeline_rb = timeline_all.get(target_rb.upper(), None)
    if timeline_rb is None:
        raise ValueError(f"❌ Không có timeline cho robot {target_rb} trong CC{cc_label}")

    T_trigger = None
    for _, step in timeline_rb.iterrows():
        step_source = str(step["source"]).strip().upper()
        step_dest = str(step["dest"]).strip().upper()

        if step_source == source and step_dest == dest:
            T_trigger = step[trigger_mode]
            break

    if T_trigger is None:
        raise ValueError(
            f"❌ Không tìm thấy trigger từ {target_rb} {source} → {dest} ({trigger_mode}) trong timeline CC{cc_label}"
        )

    # Tính thời gian chờ
    timer_thuc_te = max(0, T_trigger - T_den)

    # Chuẩn bị kết quả trả về
    result = {
        "robot": robot,
        "marker": marker_obj["position"],
        "marker_full": marker_obj["marker_text"],
        "T_den": T_den,
        "T_trigger": T_trigger,
        "timer_thuc_te": timer_thuc_te,
        "trigger_from": f"{target_rb} {source} → {dest} ({trigger_mode})"
    }

    # Ghi log nếu cần
    print(f"[{cc_label}] {robot} | marker {result['marker']} | wait sync from {result['trigger_from']}")
    print(f"    T_den = {T_den}, T_trigger = {T_trigger}, timer_thuc_te = {timer_thuc_te}")

    return result
