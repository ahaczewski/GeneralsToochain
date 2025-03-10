$Src = "extract/DX8.1b SDK/DXF/DXSDK"
$Directory = "build/DirectX81SDK"

if (Test-Path $Directory) {
    Remove-Item -Recurse -Force $Directory
}

mkdir -Force $Directory/Include
mkdir -Force $Directory/Lib
mkdir -Force $Directory/Bin

Copy-Item -Recurse -Force "$Src/include/*" $Directory/Include/
Copy-Item -Recurse -Force "$Src/lib/*" $Directory/Lib/
Copy-Item -Recurse -Force "$Src/license/*" $Directory/
Copy-Item -Force "$Src/bin/DXUtils/psa.exe" $Directory/Bin/
Copy-Item -Force "$Src/bin/DXUtils/vsa.exe" $Directory/Bin/

tree /F $Directory
