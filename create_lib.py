import sys
import os
import subprocess
import re
import tempfile


def generate_def_file(dll_path):
    """
    Generate a .def file from a .dll file by extracting exports using DUMPBIN
    """
    # Run DUMPBIN /EXPORTS on the dll file
    try:
        result = subprocess.run(['DUMPBIN.EXE', '/EXPORTS', dll_path],
                                capture_output=True, text=True, check=True)
        dumpbin_output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running DUMPBIN: {e}")
        return None
    except FileNotFoundError:
        print("DUMPBIN.EXE not found. Make sure it's in your PATH or use the full path.")
        return None

    # Parse the output to extract function names
    # Find the section containing exports
    exports_section = re.search(r'ordinal\s+hint\s+RVA\s+name\s+([\s\S]+?)(?=\n\n|\Z)', dumpbin_output)

    if not exports_section:
        print("No exports found in the DLL")
        return None

    # Extract function names
    function_lines = exports_section.group(1).strip().split('\n')
    function_names = []

    for line in function_lines:
        # Match function name from format like "         1    0 0001C760 @stream_background@0"
        match = re.search(r'\s*(\d+)\s+[0-9A-F]+\s+[0-9A-F]+\s+(.+)$', line)
        if match:
            ordinal = int(match.group(1))
            fn_name = match.group(2)
            is_stdcall = re.search(r'@\d+$', fn_name) and fn_name.startswith('_')
            if is_stdcall:
                fn_name = fn_name[1:]
            function_names.append((ordinal, fn_name))

    # Sort by ordinal
    function_names.sort(key=lambda x: x[0])

    # Create base name for output files
    base_name = os.path.splitext(os.path.basename(dll_path))[0]
    def_path = f"{base_name}.def"
    dump_path = f"{base_name}.txt"

    # Write the .def file
    with open(def_path, 'w') as def_file:
        def_file.write("EXPORTS\n")
        for name in function_names:
            def_file.write(f"    {name[1]}\n")

    # Write the .dump file
    with open(dump_path, 'w') as def_file:
        def_file.write(dumpbin_output)

    return def_path


def generate_lib_file(def_path, linker_options):
    """
    Generate a .lib file from a .def file using LIB.EXE
    """
    base_name = os.path.splitext(def_path)[0]
    lib_path = f"{base_name}.lib"

    try:
        subprocess.run(['LIB.EXE', f'/DEF:{def_path}', f'/OUT:{lib_path}'] + linker_options,
                       check=True)
        return lib_path
    except subprocess.CalledProcessError as e:
        print(f"Error running LIB.EXE: {e}")
        return None
    except FileNotFoundError:
        print("LIB.EXE not found. Make sure it's in your PATH or use the full path.")
        return None


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <dll_file> [additional_linker_options]")
        return 1

    dll_path = sys.argv[1]

    if not os.path.exists(dll_path):
        print(f"Error: File '{dll_path}' not found")
        return 1

    print(f"Processing '{dll_path}'...")
    def_path = generate_def_file(dll_path)

    if not def_path:
        return 1

    print(f"Created .def file: {def_path}")

    lib_path = generate_lib_file(def_path, sys.argv[2:] if len(sys.argv) > 2 else ['/MACHINE:x86'])

    if not lib_path:
        return 1

    print(f"Created .lib file: {lib_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
