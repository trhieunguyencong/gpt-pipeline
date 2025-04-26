import json
import sys
import os
import importlib.util
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Nạp lệnh chạy cc từ pipeline khác
try:
    cc_label = int(sys.argv[1])
except (IndexError, ValueError):
    cc_label = 1    # Nhập tay lệnh chạy CC hoặc lệnh tự động từ hàm khác



# Thiết lập đường dẫn
base_dir = os.path.dirname(os.path.abspath(__file__))
modules_dir = os.path.join(base_dir, "modules")
input_dir = os.path.join(base_dir, "input")
output_path = os.path.join(base_dir, "output", f"timeline_output_cc{cc_label}.xlsx")

# Xóa file log t_den_tracker.json nếu tồn tại
t_den_path = os.path.join(base_dir, "t_den_tracker.json")
if os.path.exists(t_den_path):
    os.remove(t_den_path)

# ✅ Thêm thư mục chứa module vào sys.path
sys.path.insert(0, modules_dir)

# Tự động nạp tất cả module trong thư mục modules
def load_all_modules(modules_path):
    for filename in os.listdir(modules_path):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            file_path = os.path.join(modules_path, filename)
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            sys.modules[module_name] = module
            globals()[module_name] = module

# Nạp module
load_all_modules(modules_dir)

# Nạp start_time tự động
output_dir = os.path.join(base_dir, "output")
if cc_label == 1:
    start_time = 0
else:
    from get_start_time_from_prev_cc import get_start_time_from_prev_cc
    start_time = get_start_time_from_prev_cc(cc_label, output_dir)

# ✅Kiểm tra file input_data.json tồn tại
if not os.path.exists("input_data.json"):
    raise ValueError("Không tìm thấy file input_data.json!")

# Đọc dữ liệu từ file input_data.json
with open("input_data.json", "r", encoding="utf-8") as f:
    global_input_data = json.load(f)

# Kiểm tra dữ liệu đã đọc
if not global_input_data:
    raise ValueError("Không có dữ liệu global input!")

print("\n✅ Đã đọc dữ liệu global_input_data từ file thành công!")

# ✅Import và gọi pipeline
main_pipeline_v5_cloud
main_pipeline_v5_cloud.run_full_timeline_pipeline_from_json(
    data=global_input_data,
    output_path=output_path,
    cc_label=cc_label,
    verbose=True,
    start_time=start_time
)