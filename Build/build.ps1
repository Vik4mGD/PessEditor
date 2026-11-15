$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name "PessEditor" `
    --icon ".\Resources\pess.ico" `
    --add-data ".\Resources\pess.ico;." `
    --add-binary ".\_internal\ffmpeg\ffmpeg.exe;ffmpeg" `
    --add-binary ".\_internal\ffmpeg\ffprobe.exe;ffmpeg" `
    ".\Source\main.py"

