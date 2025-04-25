import pandas as pd

def generate_timeline_rb_v4_3(robot_name, route_steps, timer_positions, move_time=10, tdt_time=5, user_defined_timers=None, start_time=0):
    steps = []
    current_time = start_time  # dùng start_time truyền trực tiếp, không còn patch
    user_defined_timers = user_defined_timers or {}
    generated_timer_positions = set()  # theo dõi vị trí đã sinh timer

    i = 0
    while i < len(route_steps):
        step = route_steps[i].strip()
        if '→' not in step:
            i += 1
            continue

        source, rest = step.split('→')
        dest = rest.split('(')[0].strip()
        marker = rest[rest.find('('):].strip() if '(' in rest else ''
        source = source.strip()
        dest = dest.strip()

        has_timer_marker = "(vị trí" in marker.lower() and "timer" in marker.lower() and "timer time lưu" not in marker.lower()
        has_timeluu_marker = "timer time lưu" in marker.lower()

        # Thêm bước chính vào timeline
        steps.append({
            'robot': robot_name,
            'action': step,
            'source': source,
            'dest': dest,
            'start': current_time,
            'end': current_time + move_time
        })
        current_time += move_time

        # Nếu marker có timer và chưa từng sinh timer tại vị trí này
        if has_timer_marker and dest not in generated_timer_positions:
            timer_value = user_defined_timers.get(dest, 0)
            steps.append({
                'robot': robot_name,
                'action': f'{dest} (Vị trí {dest}: timer({timer_value}))',
                'source': dest,
                'dest': dest,
                'start': current_time,
                'end': current_time + timer_value
            })
            current_time += timer_value
            generated_timer_positions.add(dest)

        # Nếu là cặp hạ nâng liền nhau, thêm TDT
        next_step = route_steps[i + 1].strip() if i + 1 < len(route_steps) else ""
        if (source.endswith('T') and dest.endswith('D') and
            next_step.startswith(dest) and next_step.endswith('→ ' + source)):
            if not has_timer_marker and not has_timeluu_marker:
                steps.append({
                    'robot': robot_name,
                    'action': f'TDT tại {dest}',
                    'source': dest,
                    'dest': dest,
                    'start': current_time,
                    'end': current_time + tdt_time
                })
                current_time += tdt_time

        i += 1

    return pd.DataFrame(steps)