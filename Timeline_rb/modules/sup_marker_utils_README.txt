
# 📦 Module: sup_marker_utils.py

## 🎯 Mục tiêu
`sup_marker_utils.py` là **module tiện ích phụ trợ chuyên biệt** cho việc xử lý các marker `"timer time lưu"` trong pipeline V5.

Module này đóng vai trò:
- Tăng tính **tái sử dụng hàm**
- Giảm lặp lại logic ở các bước Step 2, Step 3, Step 4,...
- Dễ mở rộng khi cần bổ sung các thao tác khác với marker

---

## 📂 Cấu trúc ban đầu

### ✅ Hàm đã có:

#### `get_next_marker(rb, markers_by_robot, processed_markers_by_robot)`
- Trả về marker kế tiếp cần xử lý của một robot
- Dựa trên **thứ tự đã xác định trong Step 1**
- Tránh xử lý lại marker đã convert
- Trả về `None` nếu đã xử lý hết

---

## 🛠 Định hướng phát triển tiếp theo

| Hàm dự kiến | Mục tiêu |
|------------|----------|
| `has_unprocessed_marker(rb, ...)` | Kiểm tra xem robot còn marker chưa xử lý hay không |
| `count_pending_markers(rb, ...)` | Trả về số lượng marker còn lại |
| `get_marker_arrival_time(rb, marker, timeline_df)` | Trả về thời điểm `start` khi robot đến vị trí marker |
| `is_marker_line(step)` | Kiểm tra 1 dòng route có phải chứa marker không |
| `find_marker_line_index(route, marker)` | Trả về dòng index chứa marker bất kỳ trong route |

---

## 📌 Cách dùng tiêu chuẩn trong các step

```python
from sup_marker_utils import get_next_marker

next_marker = get_next_marker(rb, markers_by_robot, processed_markers_by_robot)
if next_marker is None:
    continue
```

---

## 📁 Lưu ý khi mở rộng
- Chỉ chứa các **hàm tiện ích không phụ thuộc context controller**
- Không chứa xử lý timeline hoặc chuyển đổi marker – các bước đó nên đặt ở `step_x` hoặc `convert_marker.py`
