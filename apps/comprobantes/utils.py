# apps/comprobantes/utils.py
import re
from datetime import datetime

_DRIVE_PATTERNS = [
    r"https?://drive\.google\.com/file/d/([a-zA-Z0-9_-]+)",
    r"https?://drive\.google\.com/open\?id=([a-zA-Z0-9_-]+)",
    r"https?://drive\.google\.com/uc\?id=([a-zA-Z0-9_-]+)",
    r"https?://docs\.google\.com/uc\?id=([a-zA-Z0-9_-]+)",
]

def extract_drive_file_id(text: str) -> str | None:
    if not text:
        return None
    for pat in _DRIVE_PATTERNS:
        m = re.search(pat, text)
        if m:
            return m.group(1)
    if re.fullmatch(r"[a-zA-Z0-9_-]{10,}", text.strip()):
        return text.strip()
    return None

def normalize_cuil(raw: str) -> str:
    return "".join(ch for ch in (raw or "") if ch.isdigit())[:11]

def parse_timestamp_es(raw: str) -> datetime | None:
    raw = (raw or "").strip()
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None
