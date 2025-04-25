import sys

from input_preprocessor import extract_inputs
from v5_loop_controller_v1_2 import run_pipeline_v5
from marker_nap_thao_v2 import extract_marker_notes_from_docx, apply_marker_notes_if_cc1
from timeline_exporter import export_timeline

def run_full_timeline_pipeline(
    input_dir: str,
    output_path: str,
    cc_label: str,
    verbose: bool = False,
    start_time: int = 0
):
    # Tầng 1–2: Tiền xử lý
    route_steps_by_robot, base_timer_dict, time_luu_dict, marker_docx_path, selected_robots = extract_inputs(input_dir)

    with open("log_route_steps.txt", "w", encoding="utf-8") as f:
        for robot, steps in route_steps_by_robot.items():
            f.write(f"--- Robot: {robot} ({len(steps)} bước) ---\n")
            for i, step in enumerate(steps, 1):
                f.write(f"{i:02d}. {step}\n")
            f.write("\n")


    # Tầng 3: Thực thi pipeline
    timeline_by_robot = run_pipeline_v5(route_steps_by_robot, time_luu_dict, base_timer_dict, verbose=verbose, start_time=start_time, cc_label=cc_label)

    # Tầng 4: Gắn marker đặc biệt
    if cc_label == "1":
        marker_notes = extract_marker_notes_from_docx(marker_docx_path)
        for rb_name in timeline_by_robot:
            timeline_by_robot[rb_name] = apply_marker_notes_if_cc1(
                timeline_by_robot[rb_name],
                cc_number=1,
                marker_notes=marker_notes
            )

    # Tầng 5: Xuất kết quả
    export_timeline(
        timeline_by_robot=timeline_by_robot,
        output_path=output_path,
        cc_label=cc_label,
        selected_robots=selected_robots
    )
    return timeline_by_robot
