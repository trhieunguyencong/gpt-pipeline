import sys

import re
from docx import Document
import pandas as pd

def extract_marker_notes_from_docx(docx_path: str) -> dict:
    """
    Trích toàn bộ các ghi chú từ dấu ngoặc có dạng (Vị trí X: ghi chú)
    """
    doc = Document(docx_path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    marker_notes = {}

    for line in paragraphs:
        match = re.search(r"\(Vị trí\s+([A-Z0-9]+)\s*[:：\-–]\s*([^)]+)\)", line, re.IGNORECASE)
        if match:
            pos = match.group(1).strip().upper()
            note = match.group(2).strip()
            marker_notes[pos] = note

    return marker_notes

def apply_marker_notes_if_cc1(timeline_df: pd.DataFrame, cc_number: int, marker_notes: dict) -> pd.DataFrame:
    """
    Gắn ghi chú 'nạp hàng' tại bước nâng (XD → XT),
    và 'tháo hàng' tại bước hạ (XT → XD), nhưng chỉ áp dụng khi cc_number == 1
    """
    if cc_number != 1:
        return timeline_df  # Chỉ áp dụng cho CC1

    if "Ghi chú" not in timeline_df.columns:
        timeline_df["Ghi chú"] = ""

    for pos, note in marker_notes.items():
        full_note = f"Vị trí {pos}: {note}"
        xt = pos.replace("D", "T")

        # Nạp hàng → bước nâng XD → XT
        if "nạp hàng" in note.lower():
            mask = (timeline_df["source"] == pos) & (timeline_df["dest"] == xt)
            timeline_df.loc[mask, "Ghi chú"] = full_note

        # Tháo hàng → bước hạ XT → XD
        elif "tháo hàng" in note.lower():
            mask = (timeline_df["source"] == xt) & (timeline_df["dest"] == pos)
            timeline_df.loc[mask, "Ghi chú"] = full_note

    return timeline_df
