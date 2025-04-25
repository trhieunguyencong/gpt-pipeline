
import os
import pandas as pd

def get_start_time_from_prev_cc(cc_label: int, output_dir: str) -> int:
    """
    Đọc file timeline_output_cc{cc_label-1}.xlsx và trả về giá trị max(end)
    để dùng làm start_time cho CC hiện tại.

    Args:
        cc_label (int): Nhãn CC hiện tại (ví dụ: 2 để đọc CC1).
        output_dir (str): Đường dẫn tới thư mục chứa file output.

    Returns:
        int: Giá trị start_time = max(end) từ CC trước.
    """
    prev_cc_label = cc_label - 1
    prev_file_path = os.path.join(output_dir, f"timeline_output_cc{prev_cc_label}.xlsx")
    
    if not os.path.exists(prev_file_path):
        raise FileNotFoundError(f"Không tìm thấy file timeline CC{prev_cc_label}: {prev_file_path}")
    
    # Đọc tất cả sheet và tìm max(end)
    max_end = 0
    xl = pd.ExcelFile(prev_file_path)
    for sheet_name in xl.sheet_names:
        df = xl.parse(sheet_name)
        if 'end' in df.columns:
            max_end_sheet = df['end'].max()
            if pd.notna(max_end_sheet):
                max_end = max(max_end, int(max_end_sheet))

    return max_end
