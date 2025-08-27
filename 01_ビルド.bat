@echo on
docker build -t faq-batch .

rem docker create --name tmp faq-batch
rem docker cp tmp:/app/pip_freeze.txt ./pip_freeze.txt
rem docker rm tmp

echo.
echo ===== é¿çsäÆóπ =====
pause
