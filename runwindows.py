import ctypes
import numpy as np
import pefile

def run_exe_in_memory_windows(pe_path):
    pe = pefile.PE(pe_path)

    size = pe.OPTIONAL_HEADER.SizeOfImage
    print(f"Size of executable data: {size} bytes")

    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_void_p
    addr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),
                                                ctypes.c_int(size),
                                                ctypes.c_int(0x3000),
                                                ctypes.c_int(0x40))

    if not addr:
        raise Exception("VirtualAlloc failed")
    
    print(f"Memory allocated at address: {hex(addr)}")

    memory_data = bytearray(size)

    for section in pe.sections:
        section_size = section.SizeOfRawData
        section_addr = addr + section.VirtualAddress
        
        print(f"Copying section {section.Name.decode().strip()} at {hex(section_addr)}")
        
        section_data = section.get_data()
        section_data_np = np.frombuffer(section_data, dtype=np.uint8)

        buffer_ptr = section_data_np.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        
        print(f"Attempting to copy {section_size} bytes to address {hex(section_addr)}...")
        ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_void_p(section_addr),
                                              buffer_ptr,
                                              ctypes.c_int(section_size))

        print(f"Section {section.Name.decode().strip()} copied successfully.")

        memory_data[section.VirtualAddress:section.VirtualAddress + section_size] = section_data

    image_base = pe.OPTIONAL_HEADER.ImageBase
    entry_point_offset = pe.OPTIONAL_HEADER.AddressOfEntryPoint

    entry_point_address = addr + entry_point_offset 
    print(f"Image Base: {hex(image_base)}")
    print(f"Entry Point Offset: {hex(entry_point_offset)}")
    print(f"Calculated Entry Point Address: {hex(entry_point_address)}")

    if entry_point_address < addr or entry_point_address >= addr + size:
        raise Exception("Entry point address is out of allocated memory bounds.")

    for section in pe.sections:
        section_size = section.SizeOfRawData
        section_data = section.get_data()
        memory_section = memory_data[section.VirtualAddress:section.VirtualAddress + section_size]

        if memory_section != section_data:
            print(f"Memory section {section.Name.decode().strip()} does NOT match original.")
        else:
            print(f"Memory section {section.Name.decode().strip()} matches original.")

    entry_point_type = ctypes.CFUNCTYPE(ctypes.c_int)

    try:
        entry_point = ctypes.cast(entry_point_address, entry_point_type)
        print(f"Successfully cast entry point to function type.")
    except Exception as e:
        raise Exception(f"Failed to cast entry point: {e}")

    try:
        print(f"Calling entry point at {hex(entry_point_address)}...")
        entry_point()
        print(f"Process exited with code: {result}")
    except Exception as e:
        print(f"Error executing entry point: {e}")
        result = None

    return result