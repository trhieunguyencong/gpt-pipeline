import re

def parse_source_dest(step: str) -> tuple[str, str]:
    """
    Trích xuất source và dest từ một dòng route. Ví dụ:
    "Từ 5T → 5D" → ("5T", "5D")
    """
    pattern = r"(\d{1,2}[TD])\s*→\s*(\d{1,2}[TD])"
    match = re.search(pattern, step)
    if not match:
        raise ValueError(f"Không tách được source/dest từ dòng: {step}")
    return match.group(1), match.group(2)


def apply_timer_to_route(
    robot: str,
    marker_full_text: str,
    timer_thuc_te: int,
    route_steps_by_robot: dict
):
    route = route_steps_by_robot.get(robot)
    if not route:
        raise ValueError(f"Không tìm thấy route của robot {robot}")

    marker_clean = marker_full_text["position"].strip().upper()
    updated_route = []
    found = False

    for step in route:
        if not isinstance(step, str):
            updated_route.append(step)
            continue

        step_upper = step.upper()
        source, dest = None, None
        step_lower = step.lower()

        try:
            source, dest = parse_source_dest(step)
        except:
            updated_route.append(step)
            continue

        # ✅ Nếu dòng chứa đúng vị trí marker và là dòng có nội dung marker
        if marker_clean in {source, dest} and any(
            kw in step_lower for kw in ["timer time lưu", "chờ đồng bộ"]
        ):
            if "(" in step:
                new_step = re.sub(r"\(.*?\)", f"(Vị trí {marker_clean}: timer({timer_thuc_te}))", step)
            else:
                new_step = step + f" (Vị trí {marker_clean}: timer({timer_thuc_te}))"
            updated_route.append(new_step)
            found = True
        else:
            updated_route.append(step)

    if not found:
        raise ValueError(f"❌ Không tìm thấy dòng chứa marker '{marker_clean}' trong route của robot {robot}")

    # ✅ Ghi log updated_route
    with open("log_updated_route_{robot}.txt", "w", encoding="utf-8") as f:
        f.write(f"--- Route mới sau khi gắn timer cho robot {robot} ---\\n")
        for i, step in enumerate(updated_route):
            f.write(f"{i+1:02d}: {step}\\n")

    # Ghi đè lại route sau khi cập nhật
    route_steps_by_robot[robot] = updated_route
    return route_steps_by_robot