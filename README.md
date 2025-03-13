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

## Extras

### Creating .lib files for .dll files

The repository contains a Python script `create_lib.py` that can be used to create `.lib` files for `.dll` files.

C&C Generals uses Miles Sound System and Bink proprietary libraries, that were not open sourced.
To use them for linking, you need to create `.lib` files for them.

The script takes a `.dll` file and creates a `.lib` file for it, using the `dumpbin.exe` tool from the Visual Studio 6 toolchain.
The script is used as follows:

```cmd
<PATH_TO_VC6>\VC98\Bin\VCVARS32.BAT
python create_lib.py <PATH_TO_DLL>
```

### Installing Visual Studio 6 on Windows 11

To install Visual Studio 6 on Windows 11, you will need to perform a few steps to bypass the installer check for JavaVM from nineties,
and strip down the installed packages to the ones that will actually install.

The steps are as follows:

1. Apply patch to the `VS98ENT.STF` and `SETUPWIZ.INI` files in the `extract/VS6CD/SETUP` directory.
2. Set compatibility mode for `SETUP.EXE` to Windows XP SP3.
3. Run the installer.
4. Apply 

#### Applying the patch

The [`vs6-setup.patch`](vs6-setup.patch) file is a patch for `VS98ENT.STF` and `SETUPWIZ.INI` files in the VS6 SETUP directory,
that makes it possible to install it on a modern Windows 11 system.
Apply the patch with the usual `patch` command:

```cmd
patch -p0 < vs6-setup.patch
```

#### Running the installer

**Before running `SETUP.EXE`, set its compatibility mode to Windows XP SP3.**

Once compatibility mode is set, you can run the installer.
Do not select any additional components when asked, as the installer will fail.

The installer will restart Windows after installing Visual Studio 6.0 and will give you an option to install MSDN.
I choose not to, but it should work fine.

### (Optional) Installing Processor Pack

The Processor Pack is a package that adds support for the SSE instructions to the compiler,
and requires Service Pack 5 to be installed.

Because Service Pack 6 will remove the support anyway, it might seem useless to install the Processor Pack...
If not for the fact, that SP6 removes the header files, but leaves MASM and H2INC binaries in place.
So installing the Processor Pack is a way of getting the ML.EXE and H2INC.EXE binaries, if you wish to play with the old assembler.

As mentioned, the VCPP5 package requires SP5 to be installed, but we can trick the installer into thinking that SP5 is installed.
To do so, import the [`SP5_Add.reg`](SP5_Add.reg) file to your registry, once you have installed the Visual Studio 6.0.

Install the VCPP5 package, and then import the [`SP5_Remove.reg`](SP5_Remove.reg) file to remove the SP5 information from your registry.

> **Note:** The VCPP5 package is removed by SP6 installer because by that time there was already Visual Studio .NET 2002 available which Microsoft directed VCPP5 users to,
> and which included extended support for SSE instructions.

### Installing Service Pack 6

To install Service Pack 6, run the `en_vs6_sp6.exe`, it is self-extracting archive, and extract the contents to some directory.

The usual installer of SP6 (`setupsp6.exe`) fails on Windows 11, but it is pretty easy to bypass.
To do so, you need to run `acmsetup.exe` instead.

First, make sure to set the compatibility mode for `acmsetup.exe` to Windows XP SP3.
Then run the `acmsetup.exe` with the following command line:

```cmd
cd <PATH TO THE EXTRACTED SP6>
acmsetup.exe /S <ABSOLUTE PATH TO THE EXTRACTED SP6> /T sp698ent.stf
```

That will skip all the failing checks and install the Service Pack 6.
