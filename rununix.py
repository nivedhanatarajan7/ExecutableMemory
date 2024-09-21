import mmap
import os

def load_and_run_executable_unix(file_path):
    with open(file_path, 'rb') as f:
        executable_code = f.read()

    # Create a memory file and write the executable code
    memfd = os.memfd_create("exec_in_memory", 0)
    os.write(memfd, executable_code)

    # Make the file executable and execute it
    os.fchmod(memfd, 0o755)  # Add execute permissions
    os.execve(f"/proc/self/fd/{memfd}", [], os.environ)  # Execute the memory file