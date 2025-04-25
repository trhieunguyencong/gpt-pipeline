import json
from pathlib import Path

def write_t_den_for_selected_marker(cc_label: str, selected_rb: str, selected_marker: str,
                                     t_den_value: int, output_dir: str = "output") -> None:
    """
    Ghi T_den của 1 marker đã xử lý vào file t_den_tracker.json theo cấu trúc:
    {
        "CC2": {
            "R2": {
                "15D": 265
            }
        }
    }
    """
    # ✅ Debug kiểu dữ liệu
    print("🔍 DEBUG TYPE CHECK")
    print(f"  cc_label: {cc_label} ({type(cc_label)})")
    print(f"  selected_rb: {selected_rb} ({type(selected_rb)})")
    print(f"  selected_marker: {selected_marker} ({type(selected_marker)})")
    print(f"  t_den_value: {t_den_value} ({type(t_den_value)})")

    # Chuẩn hóa nhãn CC
    cc_label = str(cc_label)
    cc_key = f"CC{cc_label}" if not cc_label.startswith("CC") else cc_label

    # Đảm bảo thư mục output tồn tại
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Đường dẫn file JSON
    tracker_path = output_dir / "t_den_tracker.json"

    # Đọc dữ liệu cũ nếu có
    if tracker_path.exists():
        with open(tracker_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON decode error: {e}")
                data = {}
    else:
        data = {}

    # Ghi dữ liệu mới vào cấu trúc
    data.setdefault(str(cc_key), {}).setdefault(str(selected_rb), {})
    data[str(cc_key)][str(selected_rb)][str(selected_marker)] = int(t_den_value)

    # Ghi lại ra file
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
