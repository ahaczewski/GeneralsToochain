$zip = 'C:\Program Files\7-zip\7z.exe'

Set-Location build
& $zip a DirectX81SDK.7z -mx=7 -mmt=on -r DirectX81SDK
& $zip a VC6.7z -mx=7 -mmt=on -r VC6
