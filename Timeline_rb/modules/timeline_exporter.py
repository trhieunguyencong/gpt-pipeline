import sys

import pandas as pd

def export_timeline(timeline_by_robot: dict, output_path: str, cc_label: str, selected_robots: list = None):
    """
    Xuất timeline ra file Excel theo định dạng chuẩn:
    - Gộp toàn bộ robot vào một sheet
    - Chỉ xuất robot được chỉ định, hoặc toàn bộ nếu không chỉ định
    """

    # Lọc robot theo yêu cầu (nếu có)
    if selected_robots is not None:
        timeline_by_robot = {k: v for k, v in timeline_by_robot.items() if k in selected_robots}

    # Gộp dữ liệu
    combined_df = pd.concat(
        [df.assign(robot=rb) for rb, df in timeline_by_robot.items()],
        ignore_index=True
    )
    combined_df = combined_df.sort_values(by=["robot", "start"]).reset_index(drop=True)

    # Xuất file Excel
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        combined_df.to_excel(writer, index=False)
