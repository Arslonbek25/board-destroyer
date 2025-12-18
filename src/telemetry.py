import os
import time
import json

def now_ms() -> int:
    return int(time.time() * 1000)

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def log_jsonl(path: str, obj: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "a") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
