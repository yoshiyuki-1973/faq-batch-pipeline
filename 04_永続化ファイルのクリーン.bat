@echo off
echo This will delete data\output and faiss_store contents. Press Ctrl+C to cancel.
pause

if exist "data\output" rd /s /q "data\output"
if exist "faiss_store" rd /s /q "faiss_store"
mkdir "data\output"
mkdir "faiss_store"
echo [OK] cleaned.
pause
