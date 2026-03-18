@echo off
chcp 65001
echo Installing dependency packages required for AI analysis...
echo.

echo Installing PyTorch...
.\.venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Installing other AI dependencies...
.\.venv\Scripts\python.exe -m pip install opencv-python pillow numpy

echo.
echo Installation complete!
pause