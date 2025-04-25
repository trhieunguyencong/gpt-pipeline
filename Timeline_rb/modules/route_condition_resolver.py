
import re

def resolve_static_route_conditions(route_steps_by_robot, base_timer_dict):
    """
    Lọc route_steps cho từng robot dựa trên điều kiện timer cố định.
    """

    def evaluate_condition(condition_line):
        match = re.match(r"#route_if timer (\d+)\s*([<>=!]+)\s*(\d+)", condition_line.strip())
        if not match:
            raise ValueError(f"Không đúng định dạng điều kiện: {condition_line}")
        timer_pos, operator, value = match.groups()
        timer_key = f"{timer_pos}D"
        timer_value = base_timer_dict.get(timer_key)

        if timer_value is None:
            raise ValueError(f"Không tìm thấy giá trị timer cho vị trí: {timer_key} (từ dòng: {condition_line})")

        value = float(value)
        if operator == "<":
            return timer_value < value
        elif operator == "<=":
            return timer_value <= value
        elif operator == ">":
            return timer_value > value
        elif operator == ">=":
            return timer_value >= value
        elif operator == "==":
            return timer_value == value
        elif operator == "!=":
            return timer_value != value
        else:
            raise ValueError(f"Toán tử không hợp lệ trong điều kiện: {condition_line}")

    def resolve_block(route_steps):
        new_steps = []
        i = 0
        while i < len(route_steps):
            line = route_steps[i].strip()

            if line.startswith("#route_if"):
                cond_result = evaluate_condition(line)

                # Tách nhánh IF
                i += 1
                if_block = []
                while i < len(route_steps) and not route_steps[i].strip().startswith("#route_else"):
                    if_block.append(route_steps[i])
                    i += 1

                if i >= len(route_steps):
                    raise ValueError("Thiếu #route_else trong khối điều kiện.")

                # Tách nhánh ELSE
                i += 1  # skip #route_else
                else_block = []
                while i < len(route_steps) and not route_steps[i].strip().startswith("#route_endif"):
                    else_block.append(route_steps[i])
                    i += 1

                if i >= len(route_steps):
                    raise ValueError("Thiếu #route_endif trong khối điều kiện.")

                i += 1  # skip #route_endif

                # Gộp nhánh đúng
                new_steps.extend(if_block if cond_result else else_block)

            elif line.startswith("#route_else") or line.startswith("#route_endif"):
                # Các marker này chỉ hợp lệ trong khối IF → nếu lẻ tẻ thì báo lỗi
                raise ValueError(f"Marker {line} không đúng vị trí hoặc dư thừa.")
            else:
                new_steps.append(route_steps[i])
                i += 1

        return new_steps

    cleaned_route_by_robot = {}
    for rb, steps in route_steps_by_robot.items():
        cleaned_route_by_robot[rb] = resolve_block(steps)

    return cleaned_route_by_robot
