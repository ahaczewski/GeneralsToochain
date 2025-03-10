# C&C Generals Toolchain

This repository contains an automation for building VC6 toolchain necessary to work with C&C Generals.
The easiest way to consume this toolchain is to just download the built package from the [releases].

Other than that, take a look at the GitHub Actions workflow file to see how the toolchain is built.
The workflow is caching the downloaded files, so it should be fast to run (except for the first run).

## Contents

The following is the contents of the built packages in context of C&C Generals usage:

- VC6.7z:
  - C/C++ compiler
  - C and C++ standard libraries - headers and .lib files
  - MFC (Microsoft Foundation Classes) - headers and .lib files
  - ATL (Active Template Library) - headers
  - Linker and LIB (Library Manager)
  - MIDL Compiler
  - RC (Resources Compiler)
  - NMAKE
  - Few other tools
- DirectX 8.1 SDK.7z:
  - DirectX 8.1 SDK headers and .lib files
  - vsa.exe and psa.exe (shader compilers)

## Usage

The toolchain can be used for building C&C Generals (and Zero Hour) using CMake.
To point CMake to the toolchain, use the following `CMakeUserPresets.json` in the root directory of Generals:

```json
{
  "configurePresets": [
    {
      "name": "vc6-user",
      "inherits": "vc6",
      "environment": {
        "VC6_ROOT": "<POINT TO THE DIRECTORY YOU EXTRACTED VC6 TO>",
        "PATH": "$env{VC6_ROOT}/VC98/Bin;$penv{PATH}",
        "INCLUDE": "$env{VC6_ROOT}/VC98/ATL/Include;$env{VC6_ROOT}/VC98/Include;$env{VC6_ROOT}/VC98/MFC/Include;$penv{INCLUDE}",
        "LIB": "$env{VC6_ROOT}/VC98/Lib;$env{VS6_ROOT}/VC98/MFC/Lib;$penv{LIB}"
      }
    }
  ]
}
```

That should make CMake aware of the toolchain and allow you to configure the project for building.
CLion will also be able to pick up the toolchain automatically when using that preset, and build the code.

To build from the command line, run the `VCVARSALL.BAT` script from the `VC6_ROOT` directory.

## Downloads

The installation files are downloaded from the archive.org, links to all are in the `downloads.txt` file.

## Visual Studio 6

The `extract.py` script is used to unpack `.iso` and `.exe` files to the `extract` directory.
From there, the `build_vs6.py` script is used to "simulate" the installation of VC6,
reading the `.inf` files and copying required files to the `build/VC6` directory.
The build consists of the following steps:

- Copy vanilla VC6 files to the `build/VC6` directory
- Apply Service Pack 6 to the `build/VC6` directory
  - Remove files that the service pack `.inf` would remove otherwise
  - Copy files from the service pack to the `build/VC6` directory
- Copy MASM binaries from VS PreProcessor Package to the `build/VC6` directory
- Copy EULA files. To keep the hands clean.

## DirectX 8.1 SDK

The DirectX SDK is much simpler to create, as it is just a matter of copying files to the `build/DirectX` directory.
This is handled by the `build_dx.ps1` script.
Not the whole SDK is needed, only the `Include`, `Lib`, and `License` directories are copied.
Then `vsa.exe` and `psa.exe` are added to the `Bin` directory, as needed by the C&C Generals build system.
