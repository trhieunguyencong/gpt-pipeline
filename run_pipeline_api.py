# run_pipeline_api.py

from fastapi import FastAPI, Request
from global_storage import global_input_data
from Timeline_rack.timeline_rack_v5_lazy import timeline_rack_v5_lazy
from Timeline_rack.request_cc_from_robot_pipeline import request_cc_from_robot_pipeline

app = FastAPI()

@app.post("/run")
async def run_pipeline(request: Request):
    global global_input_data

    # Bước 1: Nhận JSON từ GPT gửi lên
    data = await request.json()
    global_input_data = data  # ✅ Lưu vào global_input_data
    # ✅ Thêm log dữ liệu nhận được
    print("\n========== 📥 DỮ LIỆU NHẬN VÀO TỪ HTTP REQUEST ==========")
    print(global_input_data)
    print("=========================================================\n")

    # Bước 2: Gọi pipeline rack
    timeline_rack_v5_lazy(
        request_cc_fn=request_cc_from_robot_pipeline
    )

    return {
        "status": "success",
        "message": "Timeline rack xử lý thành công!"
    }
