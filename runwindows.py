import ctypes
import os

def run_exe_in_memory(exe_path):
    with open(exe_path, "rb") as f:
        exe_data = f.read()

    size = len(exe_data)

    addr = ctypes.windll.kernel32.VirtualAlloc(
        None,
        size,
        0x1000 | 0x2000,
        0x40
    )
    if not addr:
        raise Exception("VirtualAlloc failed")

    try:
        buffer = ctypes.create_string_buffer(exe_data)
        ctypes.memmove(addr, buffer, size)
    except Exception as e:
        print(f"Error writing to memory: {e}")

    entry_point = ctypes.cast(addr, ctypes.CFUNCTYPE(ctypes.c_int))

    try:
        result = entry_point()
        return result
    except Exception as e:
        print(f"Error executing entry point: {e}")

exe_path = "./dist/helloworldpython.exe"
exit_code = run_exe_in_memory(exe_path)
print(f"Process exited with code: {exit_code}")
