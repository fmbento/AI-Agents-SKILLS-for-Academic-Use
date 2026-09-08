@echo off
setlocal enabledelayedexpansion

REM 🔧 CUSTOMIZE: Project path
set RENDERS=C:\IA\ghrepos\OpenMontage\videos\PROJECT_NAME\renders
set OUTDIR=%RENDERS%\youtube
set CRF=18
set PRESET=slow

if not exist "%OUTDIR%" mkdir "%OUTDIR%"

echo ================================================
echo   OPTIMIZE YOUTUBE - PROJECT TITLE
echo   CRF: %CRF%   Preset: %PRESET%
echo ================================================
echo.

REM 🔧 CUSTOMIZE: Episode list — one block per episode
REM Copy this pattern for each episode:

if exist "%RENDERS%\ep01-name.mp4" (
  echo [OPTIMIZE] ep01-name.mp4
  ffmpeg -i "%RENDERS%\ep01-name.mp4" ^
    -c:v libx264 -preset %PRESET% -crf %CRF% ^
    -profile:v high -level 4.0 -bf 2 -g 30 ^
    -c:a aac -b:a 192k -ar 48000 ^
    -movflags +faststart ^
    "%OUTDIR%\ep01-name-yt.mp4" -y -loglevel error
  if exist "%OUTDIR%\ep01-name-yt.mp4" (
    echo  [+] ep01-name-yt.mp4 created
    echo  [CLEANUP] Removing draft: ep01-name.mp4
    del "%RENDERS%\ep01-name.mp4"
  ) else (
    echo  [!] FAILED: ep01-name
  )
) else (
  echo  [-] ep01-name.mp4 not found, skipping
)

echo.
echo ================================================
echo   CLEANUP - a libertar espaco...
echo ================================================
rmdir /s /q "%RENDERS%\.hf-transaction-*" 2>nul
echo  [+] Cleanup concluido

echo.
echo CONCLUIDO
echo Ficheiros YouTube em: %OUTDIR%
dir "%OUTDIR%" 2>nul
pause
