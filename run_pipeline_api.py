from fastapi import FastAPI, Request
from Timeline_rack.timeline_rack_v5_lazy import timeline_rack_v5_lazy
from Timeline_rack.request_cc_from_robot_pipeline import request_cc_from_robot_pipeline
import json

app = FastAPI()

@app.post("/run")
async def run_pipeline(request: Request):
    # Bước 1: Nhận JSON từ request
    data = await request.json()

    # Bước 2: Ghi dữ liệu vào file tạm input_data.json
    import os
    base_dir = os.path.dirname(os.path.abspath(__file__))

    input_file_path = os.path.join(base_dir, "Timeline_rb", "input_data.json")

    with open(input_file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Đã ghi input_data.json thành công tại {input_file_path}")

    # Bước 3: Gọi pipeline rack
    timeline_rack_v5_lazy(
        request_cc_fn=request_cc_from_robot_pipeline
    )

    return {
        "status": "success",
        "message": "Timeline rack xử lý thành công!"
    }
