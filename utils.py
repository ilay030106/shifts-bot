from datetime import datetime
import zoneinfo
import json
import os
import tempfile
from typing import Any

def to_iso8601(year,month,day,hour,minute,second,tz_name):
    tz=zoneinfo.ZoneInfo(tz_name)
    dt=datetime(year,month,day,hour,minute,second,tzinfo=tz)
    return dt.isoformat()


def atomic_write_json(path: str, data: Any) -> None:
    """Write JSON to a file atomically (write to temp then rename)."""
    dirpath = os.path.dirname(path) or '.'
    fd, tmp_path = tempfile.mkstemp(dir=dirpath)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        raise


def atomic_read_json(path: str, default: Any = None) -> Any:
    """Read JSON file returning default on error."""
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default