import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor
from functools import partial

_cpu_count = os.cpu_count() or 1
_io_default_workers = min(100, _cpu_count * 5)

_env_workers = os.getenv("FASTER_REQUESTS_WORKERS")
try:
    max_workers = max(1, int(_env_workers)) if _env_workers else _io_default_workers
except ValueError:
    max_workers = _io_default_workers

_env_timeout = os.getenv("FASTER_REQUESTS_TIMEOUT")
try:
    REQUEST_TIMEOUT = float(_env_timeout) if _env_timeout else 5.0
except ValueError:
    REQUEST_TIMEOUT = 5.0

def send_request(url):
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        request_call = partial(requests.get, url, timeout=REQUEST_TIMEOUT)
        futures = [executor.submit(request_call) for _ in range(10)]

        for idx, future in enumerate(futures, 1):
            try:
                response = future.result()
                print(f"\rRequest {idx}: {response.status_code}", end="", flush=True)
            except requests.exceptions.Timeout as e:
                print(f"\rRequest {idx}: timeout {e}", end="", flush=True)
            except requests.exceptions.RequestException as e:
                print(f"\rRequest {idx}: error {e}", end="", flush=True)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal time for 10 requests: {total_time:.4f} seconds")