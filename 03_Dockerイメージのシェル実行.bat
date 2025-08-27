@echo off
setlocal ENABLEDELAYEDEXPANSION
set IMAGE=faq-batch

if not exist ".env" (
  echo [ERROR] .env not found.
  pause
  exit /b 1
)

set HOST=%cd%

docker run -it --rm --env-file .env ^
  -v "%HOST%\data:/app/data" ^
  -v "%HOST%\faiss_store:/app/faiss_store" ^
  --entrypoint cmd ^
  %IMAGE%

pause
