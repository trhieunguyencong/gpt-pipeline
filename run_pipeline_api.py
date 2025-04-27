from fastapi import FastAPI
from Timeline_rack.timeline_rack_v5_lazy import timeline_rack_v5_lazy
from Timeline_rack.request_cc_from_robot_pipeline import request_cc_from_robot_pipeline
import numpy as np
import json
import os
from pydantic import BaseModel

app = FastAPI()

class PipelineInput(BaseModel):
    route: dict
    base_timer_config: dict

@app.post("/run")
async def run_pipeline(payload: PipelineInput):
    # Bước 1: Nhận JSON từ payload
    data = payload.dict()

    # Bước 2: Ghi dữ liệu vào file tạm input_data.json
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(base_dir, "Timeline_rb", "input_data.json")

    with open(input_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Đã ghi input_data.json thành công tại {input_file_path}")

    # Bước 3: Gọi pipeline rack
    timeline_rack_v5_lazy(
        request_cc_fn=request_cc_from_robot_pipeline
    )

    import pandas as pd
    import glob

    # Base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Path đến thư mục chứa các file output
    timeline_rb_output_dir = os.path.join(base_dir, "Timeline_rb", "output")
    timeline_rack_output_path = os.path.join(base_dir, "Timeline_rack", "output",     "timeline_rack_lazy_result.xlsx")

    # Dictionary để chứa toàn bộ nội dung file
    timeline_files_data = {}

    # Quét tất cả các file dạng timeline_output_cc*.xlsx trong output
    file_pattern = os.path.join(timeline_rb_output_dir, "timeline_output_cc*.xlsx")
    timeline_files = glob.glob(file_pattern)

    # Đọc từng file
    for file_path in timeline_files:
        file_name = os.path.basename(file_path)
        df = pd.read_excel(file_path)
        df = df.replace({np.nan: None})
        timeline_files_data[file_name] = df.to_dict(orient="records")

    # Đọc thêm file timeline rack
    if os.path.exists(timeline_rack_output_path):
        df_rack = pd.read_excel(timeline_rack_output_path)
        df_rack = df_rack.replace({np.nan: None})
        timeline_files_data["timeline_rack_lazy_result.xlsx"] = df_rack.to_dict(orient="records")

    # Trả JSON cho GPT
    return {
        "status": "success",
        "message": "Pipeline xử lý thành công!",
        "timelines": timeline_files_data
    }
