@echo off
REM ============================================================================
REM CFS Task - Build Executable Script
REM ============================================================================
REM This script automates the process of building a Windows executable
REM from the CFS Task Python application using PyInstaller.
REM ============================================================================

echo ============================================================================
echo CFS Task - Build Executable
echo ============================================================================
echo.

REM Check if PyInstaller is installed
echo [1/6] Checking PyInstaller installation...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed.
    echo.
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller.
        echo Please install manually: pip install pyinstaller
        pause
        exit /b 1
    )
)
echo PyInstaller is installed. OK
echo.

REM Verify required files exist
echo [2/6] Verifying required files...
set MISSING_FILES=0

if not exist "display_file.py" (
    echo ERROR: display_file.py not found
    set MISSING_FILES=1
)
if not exist "base_module.py" (
    echo ERROR: base_module.py not found
    set MISSING_FILES=1
)
if not exist "config_file.py" (
    echo ERROR: config_file.py not found
    set MISSING_FILES=1
)
if not exist "mask_file.py" (
    echo ERROR: mask_file.py not found
    set MISSING_FILES=1
)
if not exist "stim_file.py" (
    echo ERROR: stim_file.py not found
    set MISSING_FILES=1
)
if not exist "packaging_helper.py" (
    echo ERROR: packaging_helper.py not found
    set MISSING_FILES=1
)
if not exist "grey.png" (
    echo ERROR: grey.png not found
    set MISSING_FILES=1
)
if not exist "temp_checkerboard.png" (
    echo ERROR: temp_checkerboard.png not found
    set MISSING_FILES=1
)
if not exist "config.json" (
    echo ERROR: config.json not found
    set MISSING_FILES=1
)
if not exist "flash_suppression_final.spec" (
    echo ERROR: flash_suppression_final.spec not found
    set MISSING_FILES=1
)

if %MISSING_FILES%==1 (
    echo.
    echo ERROR: Missing required files. Please ensure all files are present.
    pause
    exit /b 1
)
echo All required files found. OK
echo.

REM Clean previous builds
echo [3/6] Cleaning previous build artifacts...
if exist "build" (
    echo Removing build directory...
    rmdir /s /q build
)
if exist "dist" (
    echo Removing dist directory...
    rmdir /s /q dist
)
if exist "CFS_Task.exe" (
    echo Removing old executable...
    del /q CFS_Task.exe
)
echo Clean complete. OK
echo.

REM Build executable with PyInstaller
echo [4/6] Building executable with PyInstaller...
echo This may take several minutes...
echo.
pyinstaller flash_suppression_final.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed. Check the output above for errors.
    pause
    exit /b 1
)
echo.
echo Build complete. OK
echo.

REM Verify executable was created
echo [5/6] Verifying executable...
if not exist "dist\CFS_Task.exe" (
    echo ERROR: Executable was not created at dist\CFS_Task.exe
    pause
    exit /b 1
)
echo Executable created successfully. OK
echo.

REM Display file size
for %%F in ("dist\CFS_Task.exe") do (
    echo Executable size: %%~zF bytes
)
echo.

REM Create distribution package
echo [6/6] Preparing distribution package...
if not exist "distribution" mkdir distribution
echo Copying executable...
copy "dist\CFS_Task.exe" "distribution\" >nul
echo Copying README...
copy "README_DISTRIBUTION.txt" "distribution\" >nul
echo Copying sample directories...
if exist "mask_dir_sample" (
    xcopy "mask_dir_sample" "distribution\mask_dir_sample\" /E /I /Q >nul
)
if exist "stim_dir_sample" (
    xcopy "stim_dir_sample" "distribution\stim_dir_sample\" /E /I /Q >nul
)
echo Distribution package created in 'distribution' folder. OK
echo.

echo ============================================================================
echo BUILD SUCCESSFUL!
echo ============================================================================
echo.
echo Executable location: dist\CFS_Task.exe
echo Distribution package: distribution\
echo.
echo Distribution package contains:
echo   - CFS_Task.exe (main executable)
echo   - README_DISTRIBUTION.txt (user instructions)
echo   - mask_dir_sample\ (sample mask images)
echo   - stim_dir_sample\ (sample stimulus images)
echo.
echo You can now distribute the contents of the 'distribution' folder.
echo Users will need to provide their own complete image sets.
echo.
echo ============================================================================
pause
