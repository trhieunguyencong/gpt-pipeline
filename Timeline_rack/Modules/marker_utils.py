
import unicodedata
import re
import pandas as pd

def normalize_text(s: str) -> str:
    """
    Chuẩn hóa văn bản: xóa dấu, lowercase, bỏ khoảng thừa
    """
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.lower()
    s = re.sub(r"\s+", "", s)  # xóa mọi khoảng trắng
    return s

def find_first_last_position_from_marker(df: pd.DataFrame) -> tuple[str, str]:

    # [DEBUG] In cấu trúc bảng vào log file
    with open("debug_marker_df.txt", "w", encoding="utf-8") as f:
        f.write("🧪 CÁC CỘT:\n")
        f.write(str(df.columns.tolist()) + "\n\n")
        f.write("🧪 10 DÒNG ĐẦU:\n")
        f.write(df.head(10).to_string(index=False))

    # [AN TOÀN] Kiểm tra bắt buộc cột 'action'
    if "action" not in df.columns:
        raise ValueError(f"❌ Không tìm thấy cột 'action'. Cột hiện có: {df.columns.tolist()}")


    """
    Trích xuất vị trí nạp hàng và tháo hàng từ cột 'action' trong DataFrame
    bằng cách dò marker dạng 'Vị trí 1D: nạp hàng', không phân biệt hoa thường, dấu tiếng Việt, khoảng trắng.
    """
    pos_nap = None
    pos_thao = None

    for val in df["action"].astype(str):
        text = normalize_text(val)

        if "vitri" in text and "naphang" in text:
            match = re.search(r"vitri(\d+)", text)
            if match:
                pos_nap = match.group(1)
        elif "vitri" in text and "thaohang" in text:
            match = re.search(r"vitri(\d+)", text)
            if match:
                pos_thao = match.group(1)

    if not pos_nap or not pos_thao:
        raise ValueError("❌ Không tìm được marker nạp hàng hoặc tháo hàng trong file timeline.")

    return f"{pos_nap}D", f"{pos_thao}D"
