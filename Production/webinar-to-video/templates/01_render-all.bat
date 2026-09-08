@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
set "PROJECT=%CD%"
set "RENDERS=%PROJECT%\renders"
set "QUALITY=draft"
set "WORKERS=12"
set "PRODUCER_BROWSER_GPU_MODE=hardware"
set "HF_DE_PARALLEL_ROUTER=false"
set "HYPERFRAMES_NO_PROMPT=1"
if not exist "%RENDERS%" mkdir "%RENDERS%"

echo ================================================
echo   RENDER - Scopus Bibliometric Analysis (12 ep)
echo   Quality: %QUALITY%   Workers: %WORKERS%   GPU: ON
echo ================================================

call :render ep01 ep01-fundamentos-bibliometria
call :render ep02 ep02-indicadores-tendencias
call :render ep03 ep03-questoes-estrategia
call :render ep04 ep04-sistematizacao-macro-micro
call :render ep05 ep05-produtividade-citacoes
call :render ep06 ep06-metricas-revistas
call :render ep07 ep07-altmetrics-contexto
call :render ep08 ep08-redes-vosviewer
call :render ep09 ep09-pesquisa-scopus
call :render ep10 ep10-analise-documentos
call :render ep11 ep11-autores-instituicoes
call :render ep12 ep12-comparacao-conclusao

echo.
echo Cleaning HyperFrames transactions...
for /d %%D in ("%RENDERS%\.hf-transaction-*") do rmdir /s /q "%%~fD" 2>nul
for /d %%D in ("%RENDERS%\.ep*-*") do rmdir /s /q "%%~fD" 2>nul
for /d %%D in ("%TEMP%\hyperframes*") do rmdir /s /q "%%~fD" 2>nul
for /d %%D in ("%TEMP%\hf-render-*") do rmdir /s /q "%%~fD" 2>nul
echo Done.
pause
exit /b 0

:render
set "EP=%~1"
set "NAME=%~2"
if exist "%RENDERS%\%NAME%.mp4" (
  echo [=] Already exists, skipping: %NAME%.mp4
  exit /b 0
)
echo.
echo Rendering %EP% - %NAME%
call npx --yes hyperframes render "%PROJECT%\%EP%" --quality %QUALITY% --workers %WORKERS% --gpu --video-frame-format jpg --frames-cache-dir off --output "%RENDERS%\%NAME%.mp4"
if errorlevel 1 (
  echo ERROR: %EP% failed
) else (
  echo OK: %RENDERS%\%NAME%.mp4
)
exit /b 0
