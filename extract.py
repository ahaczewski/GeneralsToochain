import os
import shutil
import subprocess
import sys
from pathlib import Path


def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def extract_with_7z(source_file, output_dir):
    """Extract files using 7-Zip"""
    print(f"Extracting {os.path.basename(source_file)} to {output_dir}...")
    ensure_directory_exists(output_dir)

    try:
        subprocess.run(["C:/Program Files/7-zip/7z.exe", "x", "-y", f"-o{output_dir}", source_file], check=True)
        print(f"Extraction of {os.path.basename(source_file)} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting {source_file}: {e}")
        return False
    except FileNotFoundError:
        print("Error: 7z.exe not found. Please ensure 7-Zip is installed and in your PATH.")
        return False


def extract_vs6_sp6(output_dir):
    """Extract the VS6 Service Pack 6 to the build directory"""
    print("Extracting VS6 Service Pack 6...")
    ensure_directory_exists(output_dir)

    # Get absolute path for the VS6SP6 directory
    abs_path = os.path.abspath(output_dir)

    try:
        subprocess.run(["downloads/en_vs6_sp6.exe", f"/T:{abs_path}", "/C"],
                       check=True)
        print("VS6 SP6 extraction completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting VS6 SP6: {e}")
        return False
    except FileNotFoundError:
        print("Error: VS6 SP6 installer not found in the downloads directory")
        return False


def main():
    """Main function to execute all extraction steps"""
    print("Extracting Visual Studio 6...")

    # If the `extract` directory exists, remove it first
    if os.path.isdir("extract"):
        print("Removing existing 'extract' directory...")
        shutil.rmtree("extract")
        print("'extract' directory removed.")

    # Check if downloads directory exists
    if not os.path.isdir("downloads"):
        print("Error: 'downloads' directory not found!")
        print("Please create a 'downloads' directory and place the required files there:")
        print("- en_vs6_ent_cd1.iso")
        print("- DX81b_SDK.exe")
        print("- en_vs6_sp6.exe")
        return 1

    # Check if all required files exist
    required_files = [
        "downloads/en_vs6_ent_cd1.iso",
        "downloads/DX81b_SDK.exe",
        "downloads/en_vs6_sp6.exe"
    ]

    missing_files = []
    for file in required_files:
        if not os.path.isfile(file):
            missing_files.append(file)

    if missing_files:
        print("Error: The following required files are missing:")
        for file in missing_files:
            print(f"- {file}")
        return 1

    # Step 1: Extract VS6 ISO using the refactored function
    if not extract_with_7z("downloads/en_vs6_ent_cd1.iso", "extract/VS6CD"):
        return 1

    # Step 2: Extract DirectX SDK using the same refactored function
    if not extract_with_7z("downloads/DX81b_SDK.exe", "extract"):
        return 1

    # Step 3: Extract VS6 SP6 (uses a different extraction method)
    if not extract_vs6_sp6("extract/VS6SP6"):
        return 1

    # # Step 4: Extract VS6 SP6 cabinet files
    # if not extract_with_7z(f"extract/VS6SP6/VS6sp61.cab", f"extract/VS6SP6Cab"):
    #     return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
