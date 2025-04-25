
import re
from typing import Optional, Dict

def parse_marker_wait_sync(marker_text: str) -> Optional[Dict[str, str]]:
    """
    Phân tích marker dạng "Chờ đồng bộ – rX: A hành động B"
    Trả về trigger_dict = {robot, source, dest, trigger_time}
    """
    marker_text = marker_text.strip()

    # Tách phần sau "Chờ đồng bộ – "
    match_main = re.search(r"Chờ đồng bộ\s*–\s*(r\d+)\s*:\s*(.+)", marker_text)
    if not match_main:
        return None

    robot, action_text = match_main.groups()
    robot = robot.strip()
    action_text = action_text.strip()

    # Danh sách từ khóa hỗ trợ
    keyword_map = {
        "bắt đầu lên":     ("start", lambda src: (src, src.replace("D", "T"))),
        "kết thúc lên":    ("end",   lambda src: (src, src.replace("D", "T"))),
        "bắt đầu xuống":   ("start", lambda src: (src, src.replace("T", "D"))),
        "kết thúc xuống":  ("end",   lambda src: (src, src.replace("T", "D"))),
        "bắt đầu di chuyển tới": ("start", lambda src, dst: (src, dst)),
        "kết thúc di chuyển tới": ("end", lambda src, dst: (src, dst)),
        "bắt đầu đi sang": ("start", lambda src, dst: (src, dst)),
        "kết thúc đi sang": ("end", lambda src, dst: (src, dst)),
    }

    for keyword, (trigger_time, position_fn) in keyword_map.items():
        if keyword in action_text:
            parts = action_text.split(keyword)
            if len(parts) != 2:
                return None

            part1 = parts[0].strip()
            part2 = parts[1].strip()

            if "→" in part1 or "→" in part2:
                return None  # Không hỗ trợ dạng có mũi tên

            if callable(position_fn):
                if "sang" in keyword or "tới" in keyword:
                    source = part1
                    dest = part2
                    if not (re.match(r"\d+[TD]", source) and re.match(r"\d+[TD]", dest)):
                        return None
                    source, dest = position_fn(source, dest)
                else:
                    source = part1
                    if not re.match(r"\d+[TD]", source):
                        return None
                    source, dest = position_fn(source)

                return {
                    "robot": robot,
                    "source": source,
                    "dest": dest,
                    "trigger_time": trigger_time
                }

    return None  # Không khớp bất kỳ từ khóa nào
