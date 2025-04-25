import pandas as pd
from typing import Optional
import subprocess
import os


def run_timeline_robot_for_cc(index: int):
    """
    Gọi pipeline timeline robot để sinh file timeline_output_cc{index}.xlsx
    bằng cách chạy run_pipeline_local.py trong thư mục Timeline_rb.
    """
    try:
        print(f"[INFO] Đang gọi pipeline robot cho CC{index}...")
        subprocess.run(
            ["python", "run_pipeline_local.py", str(index)],
            check=True,
            cwd=os.path.join(os.path.dirname(__file__), "..", "Timeline_rb")
        )
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Pipeline robot bị lỗi khi chạy CC{index}: {e}")
        raise

def request_cc_from_robot_pipeline(index: int, output_folder: str = "../Timeline_rb/output") -> Optional[pd.DataFrame]:
    """
    Hàm tương thích với pipeline timeline_rack_v5_lazy.
    Gọi hệ thống sinh dữ liệu robot cho từng CC và nạp file kết quả đã sinh.
    """
    # Gọi pipeline robot sinh dữ liệu
    run_timeline_robot_for_cc(index)

    # Đường dẫn đến file đã sinh
    current_dir = os.path.dirname(__file__)
    file_path = os.path.abspath(os.path.join(current_dir, output_folder, f"timeline_output_cc{index}.xlsx"))

    # Kiểm tra file tồn tại
    if not os.path.exists(file_path):
        print(f"[WARN] Không tìm thấy file timeline_output_cc{index}.xlsx sau khi gọi robot.")
        return None

    # Đọc file
    df = pd.read_excel(file_path)

    # Gán tên CC
    df["CC"] = f"CC{index}"

    # Trả về dữ liệu chuẩn cho pipeline rack
    return df[["action", "start", "end", "CC"]]
