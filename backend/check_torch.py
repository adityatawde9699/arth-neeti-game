import time
print("Start import...", flush=True)
start = time.time()
try:
    import torch
    print(f"Imported torch in {time.time() - start:.2f}s", flush=True)
    print(f"Torch version: {torch.__version__}", flush=True)
except ImportError as e:
    print(f"Failed to import torch: {e}", flush=True)
except Exception as e:
    print(f"Error importing torch: {e}", flush=True)
