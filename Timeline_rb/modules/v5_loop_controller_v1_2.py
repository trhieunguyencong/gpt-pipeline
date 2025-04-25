from v5_step_6_check_robot_done_marker import check_all_robot_done_marker
from v5_step_6_check_robot_done_marker import check_robot_done_and_generate_v4
from timeline_rb_v4_3_1 import generate_timeline_rb_v4_3
from v5_step_1_init_scan import scan_markers, handle_clean_robots
from v5_step_2_prepare_timeline_v2 import prepare_timeline_v2
from v5_step_3_select_marker import update_t_den_by_robot, select_next_marker
from write_t_den_tracker import write_t_den_for_selected_marker
import numpy as np
import os

def extract_T_den_value(T_den_raw):
    if isinstance(T_den_raw, tuple):
        for item in T_den_raw:
            if isinstance(item, (int, np.integer)):
                return int(item)
        raise ValueError(f"Không tìm thấy giá trị int trong tuple: {T_den_raw}")
    elif isinstance(T_den_raw, (int, np.integer)):
        return int(T_den_raw)
    else:
        raise ValueError(f"Định dạng T_den không hợp lệ: {T_den_raw}")

def run_pipeline_v5(route_steps_by_robot: dict, time_luu_dict: dict, base_timer_dict: dict, cc_label: str, verbose: bool = False, start_time=0):

    # ✅ Dọn log cũ khi bắt đầu chạy pipeline
    log_files = [
        "log_timeline_by_robot_step2.txt",
        "log_timeline_all.txt",
        "log_timer_value.txt",
        "log_route_steps_by_robot_step_5.txt",
        "log_processed_markers.txt",
        "log_step6_call.txt",
        "log_timeline_by_robot_step6.txt"
    ]

    for log_file in log_files:
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
        except Exception as e:
            print(f"Lỗi khi xóa {log_file}: {e}")


    # ✅ Ghi nhận danh sách robot cố định từ đầu
    all_robots_fixed = list(route_steps_by_robot.keys())


    # Step 1 – Quét marker
    if verbose:
        print("📍 Bắt đầu Step 1: Quét marker từ route")
    markers_by_robot, processed_markers_by_robot, robots_sach_marker = scan_markers(route_steps_by_robot)
    timeline_partial_by_robot = {}
    timeline_full = {}

    if verbose:
        print(f"📦 Step 1: Xử lý robot không có marker: {robots_sach_marker}")
    timeline_by_robot = handle_clean_robots(
        robots_sach_marker,
        route_steps_by_robot,
        base_timer_dict,
        start_time=start_time
    )
    for rb in robots_sach_marker:
        timeline_full[rb] = timeline_by_robot[rb]

    last_selected_rb = None
    while True:
        # ✅ Kiểm tra toàn cục: tất cả marker đã xử lý?
        all_done = check_all_robot_done_marker(processed_markers_by_robot, markers_by_robot)
        if all_done:
            if verbose:
                print('🏁 Đã xử lý xong tất cả marker cho mọi robot – kết thúc vòng lặp')
            break

        # Step 2 – Tính timeline bán phần
        if verbose:
            print("🔁 Step 2: Tính timeline bán phần & lấy current marker")
        timeline_by_robot, current_marker_by_robot = prepare_timeline_v2(
            route_steps_by_robot,
            timeline_by_robot,
            markers_by_robot,
            processed_markers_by_robot,
            last_selected_rb,
            base_timer_dict,
            start_time=start_time
        )

        # Ghi log kiểm tra timeline_by_robot
        with open("log_timeline_by_robot_step2.txt", "w", encoding="utf-8") as f:
            for rb, df in timeline_by_robot.items():
                f.write(f"--- Robot {rb} ---\\n")
                f.write(df.to_string(index=False))
                f.write("\\n\\n")

        if last_selected_rb is None:
            for rb in timeline_by_robot:
                timeline_partial_by_robot[rb] = timeline_by_robot[rb]
        else:
            if last_selected_rb in timeline_by_robot:
                timeline_partial_by_robot[last_selected_rb] = timeline_by_robot[last_selected_rb]

        # Step 3 – Tính thời điểm đến
        t_den_by_robot = update_t_den_by_robot(current_marker_by_robot, timeline_by_robot)
        if verbose:
            print(f"⏱ Step 3: Tính T_đến và chọn marker tiếp theo")
        result = select_next_marker(t_den_by_robot)
        if result is None:
            raise ValueError('⚠️ Vòng lặp dừng sai: còn marker chưa xử lý nhưng không chọn được marker khả thi!')
        next_rb, next_marker, _ = result

        if verbose:
            print(f"✅ Chọn marker: Robot = {next_rb}, Marker = {next_marker}")
        last_selected_rb = next_rb

        # Gom dữ liệu timeline
        timeline_all = {}
        all_robots = all_robots_fixed

        for rb in all_robots:
            if rb in timeline_full:
                timeline_all[rb] = timeline_full[rb]
                if rb in timeline_partial_by_robot:
                    del timeline_partial_by_robot[rb]
            elif rb in timeline_partial_by_robot:
                timeline_all[rb] = timeline_partial_by_robot[rb]

        # ✅ Gắn log TẠI ĐÂY – SAU khi timeline_all đã hoàn chỉnh
        with open("log_timeline_all.txt", "a", encoding="utf-8") as f:
            f.write(f"🌀 Sau vòng lặp CC = {cc_label}:\n")
            f.write(f"timeline_all gồm các robot: {list(timeline_all.keys())}\n\n")
            for rb, df in timeline_all.items():
                f.write(f"--- Robot {rb} ---\n")
                f.write(df.to_string(index=False))
                f.write("\n\n")
            f.write("="*60 + "\n\n")


        from v5_step_4_calculate_timer import calculate_timer_time_luu_from_all
        from v5_step_4_calculate_timer_wait_sync_from_all import calculate_timer_wait_sync_from_all

        T_den_raw = t_den_by_robot[next_rb]
        marker_from_t_den = T_den_raw[0]  # ✅ marker gốc từ step 3
        T_den = extract_T_den_value(T_den_raw[1])

        # ✅ Trích vị trí (position) từ marker gốc
        position = marker_from_t_den["position"]

        # ✅ Tìm lại marker gốc từ markers_by_robot để đảm bảo đúng loại
        marker_list = markers_by_robot.get(next_rb, [])
        matched_marker = next((m for m in marker_list if m["position"] == position), None)

        if matched_marker is None:
            raise ValueError(f"❌ Không tìm thấy marker có position = {position} trong                 markers_by_robot[{next_rb}]")

        # ✅ Phân nhánh xử lý dựa trên type của marker gốc
        if matched_marker["type"] == "timer_time_luu":
            timer_value = calculate_timer_time_luu_from_all(
                robot=next_rb,
                marker_full_text=matched_marker["marker_text"],
                T_den=T_den,
                timeline_all=timeline_all,
                time_luu_dict=time_luu_dict,
                cc_label=cc_label,
                output_dir="output"
            )

        elif matched_marker["type"] == "wait_sync":
            timer_value = calculate_timer_wait_sync_from_all(
                robot=next_rb,
                marker_obj=matched_marker,
                T_den=T_den,
                timeline_all=timeline_all,
                cc_label=cc_label,
                log_dir="output"
            )
        else:
            raise ValueError(f"❌ Marker chưa hỗ trợ: {matched_marker['marker_text']}")

        with open("log_timer_value.txt", "a", encoding="utf-8") as f:
            f.write(f"[{next_rb} - {next_marker}] timer_value = {timer_value}\n")

        # ✅ Ghi T_den sau khi đã xác định thành công
        marker_full = T_den_raw[0]
        short_marker = marker_full["position"]
        write_t_den_for_selected_marker(cc_label, next_rb, short_marker, T_den)

        from v5_step_5_apply_timer import apply_timer_to_route
        route_steps_by_robot = apply_timer_to_route(
            robot=next_rb,
            marker_full_text=next_marker,
            timer_thuc_te=timer_value['timer_thuc_te'],
            route_steps_by_robot=route_steps_by_robot
        )

        #log
        with open("log_route_steps_by_robot_step_5.txt", "w", encoding="utf-8") as f:
            for rb, steps in route_steps_by_robot.items():
                f.write(f"--- Robot {rb} ---\\n")
                for i, step in enumerate(steps):
                    f.write(f"{i+1:02d}: {step}\\n")
                f.write("\\n")

        # ✅ Ghi nhận marker đã xử lý sau khi hoàn tất step 5
        if next_marker not in processed_markers_by_robot[next_rb]:
            processed_markers_by_robot[next_rb].append(next_marker)

            # 📝 Ghi log mỗi lần cập nhật
            with open("log_processed_markers.txt", "a", encoding="utf-8") as f:
                f.write(f"→ Danh sách marker đã xử lý: {processed_markers_by_robot[next_rb]}\n\n")

        with open("log_step6_call.txt", "a", encoding="utf-8") as f:
            f.write(f"📌 Gọi step6: next_rb = {next_rb}, next_marker = {next_marker}\n")

        # ✅ Step 6 Kiểm tra nếu rb đã xử lý xong và gọi V4
        timeline = check_robot_done_and_generate_v4(
            robot=next_rb,
            processed_markers_by_robot=processed_markers_by_robot,
            markers_by_robot=markers_by_robot,
            route_steps_by_robot=route_steps_by_robot,
            base_timer_dict=base_timer_dict,
            start_time=start_time
        )
        if timeline is not None:
            timeline_full[next_rb] = timeline
            if next_rb in route_steps_by_robot:
                del route_steps_by_robot[next_rb]  # ✅ Loại khỏi vòng lặp

    timeline_by_robot = timeline_full

    # Ghi log kiểm tra timeline_by_robot
    with open("log_timeline_by_robot_step6.txt", "w", encoding="utf-8") as f:
        for rb, df in timeline_by_robot.items():
            f.write(f"--- Robot {rb} ---\\n")
            f.write(df.to_string(index=False))
            f.write("\\n\\n")


    return timeline_by_robot