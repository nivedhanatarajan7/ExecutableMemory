import mmap
import ctypes
import os

def run_exe_in_memory_unix(path):
    PROT_READ = 1
    PROT_WRITE = 2
    PROT_EXEC = 4

    with open(path, 'rb') as f:
        exe_data = f.read()

    mm = mmap.mmap(-1, len(exe_data), prot=PROT_READ | PROT_WRITE | PROT_EXEC)

    mm.write(exe_data)

    c_func_type = ctypes.CFUNCTYPE(None)
    c_func = c_func_type(ctypes.addressof(ctypes.c_void_p.from_buffer(mm)))

    c_func()
