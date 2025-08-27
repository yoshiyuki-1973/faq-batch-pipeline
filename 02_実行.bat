@echo on

setlocal ENABLEDELAYEDEXPANSION
set IMAGE=faq-batch

if not exist ".env" (
  echo [ERROR] .env not found.
  pause
  exit /b 1
)

set HOST=%cd%

docker run --rm --env-file .env -v "%cd%\data:/app/data" -v "%cd%\faiss_store:/app/faiss_store" faq-batch

echo.
echo ===== é¿çsäÆóπ =====
pause
