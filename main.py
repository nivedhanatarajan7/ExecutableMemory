import runwindows
import platform
import rununix

os_type = platform.system()
if os_type == 'Windows':
    runwindows.run_exe_in_memory_windows("./dist/helloworldpython.exe")
elif os_type == 'Linux' or os_type == 'Darwin':  # Darwin is macOS
    rununix.run_exe_in_memory_unix("./dist/helloworldpython.exe")
else:
    raise NotImplementedError(f"Unsupported OS: {os_type}")