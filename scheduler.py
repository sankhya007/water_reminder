from datetime import datetime, time

def is_sleep_time(sleep_start: str, sleep_end: str) -> bool:
    now = datetime.now().time()
    start = time.fromisoformat(sleep_start)
    end = time.fromisoformat(sleep_end)

    if start < end:
        return start <= now <= end
    return now >= start or now <= end
