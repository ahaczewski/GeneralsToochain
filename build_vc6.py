import os
import shutil
import sys
from configparser import ConfigParser
from fnmatch import fnmatch
from pathlib import Path

from extract import ensure_directory_exists

# List of fnmatch patterns for files to copy over from the installation directory to the destination.
SPEC = [
    ("vc98/atl/include/*", None),
    ("vc98/bin/*", None),
    ("vc98/lib/*", None),
    ("vc98/include/*", None),
    ("vc98/mfc/include/*", None),
    ("vc98/mfc/lib/*", None),
    ("common/msdev98/bin/rc.exe", 'vc98/bin'),
    ("common/msdev98/bin/rcdll.dll", 'vc98/bin'),
    ("common/msdev98/bin/mspdb60.dll", 'vc98/bin'),
    ("common/msdev98/bin/msdis110.dll", 'vc98/bin'),
    ("common/msdev98/bin/msobj10.dll", 'vc98/bin'),
]

DIR_CASE = {
    "vc98": "VC98",
    "common": "Common",
    "msdev98": "MSDev98",
    "mfc": "MFC",
    "atl": "ATL",
    "lib": "Lib",
    "include": "Include",
    "bin": "Bin",
    "objmodel": "ObjModel",
    "gl": "GL",
    "sys": "SYS",
    "res": "Res",
}

VCVARS = r"""
@echo off
rem
rem Root of Visual C++ installed files.
rem
set MSVCDir=%~dp0VC98

rem
echo Setting environment for using Microsoft Visual C++ tools.
rem

set PATH="%MSVCDir%\BIN";"%PATH%"
set INCLUDE=%MSVCDir%\ATL\INCLUDE;%MSVCDir%\INCLUDE;%MSVCDir%\MFC\INCLUDE;%INCLUDE%
set LIB=%MSVCDir%\LIB;%MSVCDir%\MFC\LIB;%LIB%
"""


def apply_case(path: Path):
    """Apply the directory case to the path."""
    parts = path.parts
    new_parts = []
    for part in parts:
        if part.lower() in DIR_CASE:
            new_parts.append(DIR_CASE[part.lower()])
        else:
            new_parts.append(part)
    return Path(*new_parts)


def copy_file(src: Path, dest: Path):
    """Copy file from src to dest, creating the destination directory if it doesn't exist and preserving the file timestamp."""
    ensure_directory_exists(dest.parent)
    try:
        # Copy the file and preserve the timestamp
        os.makedirs(dest.parent, exist_ok=True)
        os.remove(dest) if dest.exists() else None
        shutil.copy2(src, dest)
    except Exception as e:
        print(f"Error copying {src} to {dest}: {e}")


def main():
    vs98ent = read_inf_file('extract/VS6CD/SETUP/VS98ENT.INF')
    sp698ent = read_inf_file('extract/VS6SP6/SETUP/sp698ent.inf')

    # stf_entries = read_stf_file("extract/VS6CD/SETUP/VS98ENT.STF")

    output_dir = "build/VC6"

    # If the `extract` directory exists, remove it first
    if os.path.isdir(output_dir):
        print(f"Removing existing '{output_dir}' directory...")
        shutil.rmtree(output_dir)

    ensure_directory_exists(output_dir)

    # Copy base VS6 files
    copy_files_from_inf(vs98ent, 'extract/VS6CD', output_dir)

    # Copy VCPP5 files
    vcpp5_path = Path('extract/VCPP5')
    bin_dir_path = Path(output_dir) / 'VC98/Bin'
    copy_file(vcpp5_path / 'c2.dll', bin_dir_path / 'C2.DLL')
    copy_file(vcpp5_path / 'ml.exe', bin_dir_path / 'ML.EXE')
    copy_file(vcpp5_path / 'ml.err', bin_dir_path / 'ML.ERR')
    copy_file(vcpp5_path / 'h2inc.exe', bin_dir_path / 'H2INC.EXE')
    copy_file(vcpp5_path / 'h2inc.err', bin_dir_path / 'H2INC.EXE')

    # Apply SP6
    remove_files_from_inf(sp698ent, 'VC PP Remove Hdr', os.path.join(output_dir, 'VC98/Include'))
    copy_files_from_inf(sp698ent, 'extract/VS6SP6', output_dir)

    # Copy EULAs
    copy_file(Path('extract/VS6CD/EULA.TXT'), Path(output_dir) / 'EULA.txt')
    copy_file(Path('extract/VS6SP6/SETUP/eula.txt'), Path(output_dir) / 'EULA-SP6.txt')

    # Remove stub VCVARS32.BAT
    os.remove(Path(output_dir) / 'VC98/Bin/VCVARS32.BAT')

    # Write VCVARSALL.BAT
    vc_vars_all_bat_path = Path(output_dir) / 'VCVARSALL.BAT'
    with open(vc_vars_all_bat_path, 'wt') as f:
        f.write(VCVARS)

    return 0


def read_inf_file(file_path):
    invalid_lines = []
    valid_lines = []
    with open(file_path, 'r') as file:
        lines = file.readlines()

        for line in lines:
            if '=' in line or '[' in line:
                valid_lines.append(line)
            else:
                invalid_lines.append(line)

    # lines.pop(9)  # Remove the 10th line (index 9) as it breaks ConfigParser, and we don't need it anyway.
    modified_content = ''.join(valid_lines)
    config = ConfigParser(strict=False)
    config.read_string(modified_content, source=file_path)
    return config


def copy_files_from_inf(config, input_dir, output_dir):
    print(f"=====================================================  Copying files from {input_dir} to {output_dir}...")
    for section in config.sections():
        for key, value in config.items(section):
            columns = value.split(",")
            if len(columns) != 21:
                continue

            dest_file_name, install_file_path = get_inf_file_paths(columns[1])

            for spec in SPEC:
                src_pattern = spec[0]
                override_dir = spec[1]
                if fnmatch(install_file_path, src_pattern):
                    src_file_path = Path(input_dir) / install_file_path
                    dest_dir = Path(install_file_path).parent if override_dir is None else Path(override_dir)
                    dest_file_path = output_dir / apply_case(dest_dir) / dest_file_name
                    print(f"Copying {src_file_path} to {dest_file_path}...")
                    copy_file(src_file_path, dest_file_path)


def remove_files_from_inf(config, section_name, dir_path):
    print(
        f"=====================================================  Removing files of section {section_name} from {dir_path}...")
    for key, value in config.items(section_name):
        columns = value.split(",")
        if len(columns) != 21:
            continue

        dest_file_name, install_file_path = get_inf_file_paths(columns[1])
        dest_dir = Path(install_file_path).parent
        dest_file_path = Path(dir_path) / apply_case(dest_dir) / dest_file_name
        if dest_file_path.exists():
            print(f"Removing {dest_file_path}...")
            os.remove(dest_file_path)


def get_inf_file_paths(file_column):
    install_file_path_column = file_column.replace("\\", "/")
    # Find the file name, e.g. <EVENTCPTS_I.C>
    install_file_path_parts = install_file_path_column.split("<")
    install_file_path = install_file_path_parts[0].strip()
    dest_file_name = os.path.basename(install_file_path).upper() if len(install_file_path_parts) < 2 else \
        install_file_path_parts[1].strip()[:-1]
    return dest_file_name, install_file_path


if __name__ == "__main__":
    sys.exit(main())
