import ctypes
import mmap
import os
import platform
import subprocess

# Load and run executable files in memory
def load_and_run_executable_in_memory(file_path):
    os_type = platform.system()

    if os_type == 'Windows':
        load_and_run_executable_windows(file_path)
    elif os_type == 'Linux' or os_type == 'Darwin':  # Darwin is macOS
        load_and_run_executable_unix(file_path)
    else:
        raise NotImplementedError(f"Unsupported OS: {os_type}")

# Load and run exectuable files in windows
def load_and_run_executable_windows(file_path):
    # Load executable file in memory
    with open(file_path, 'rb') as f:
        executable_code = f.read()
    
    # Add execute permissions and create buffer
    buffer = mmap.mmap(-1, len(executable_code), access=mmap.ACCESS_WRITE)
    buffer.write(executable_code)

    ctypes.windll.kernel32.VirtualProtect(
        ctypes.c_void_p(ctypes.addressof(ctypes.c_char.from_buffer(buffer))),
        len(executable_code),
        0x40,  # PAGE_EXECUTE_READWRITE
        ctypes.byref(ctypes.c_ulong())
    )

    function = ctypes.cast(ctypes.addressof(ctypes.c_char.from_buffer(buffer)), ctypes.CFUNCTYPE(None))
    function()

# Load and run exectuable files in Unix
def load_and_run_executable_unix(file_path):
    # Load executable file in memory
    with open(file_path, 'rb') as f:
        executable_code = f.read()

    ## Create memory file
    memfd = os.memfd_create("exec_in_memory", 0)
    os.write(memfd, executable_code)

    # Add execute permissions
    mmap_obj = mmap.mmap(memfd, len(executable_code), prot=mmap.PROT_READ | mmap.PROT_EXEC)

    libc = ctypes.CDLL(None)
    entry_point = ctypes.cast(ctypes.addressof(ctypes.c_char.from_buffer(mmap_obj)), ctypes.CFUNCTYPE(None))

    # Execute the code
    entry_point()