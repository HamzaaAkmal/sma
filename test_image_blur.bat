@echo off
echo ========================================
echo  Universal NSFW Filter - Image Blur Test
echo ========================================
echo.

echo [1/4] Starting Flask API Server...
start "Flask API" cmd /k "cd /d "%~dp0" && python flask_api.py"

echo [2/4] Waiting for server to start...
timeout /t 5 /nobreak > nul

echo [3/4] Opening test page in browser...
start "" "test_image_blur.html"

echo [4/4] Opening extension popup helper...
echo.
echo INSTRUCTIONS:
echo 1. Flask API is starting in a separate window
echo 2. Test page is opening in your default browser
echo 3. Right-click the Chrome extension icon and select "Inspect popup"
echo 4. In the extension popup:
echo    - Enable "Image NSFW Protection"
echo    - Choose which image types to blur
echo    - Adjust blur intensity and sensitivity
echo 5. Refresh the test page to see image blur in action
echo.
echo TESTING FEATURES:
echo - Thumbnail detection and blurring
echo - Profile picture detection and blurring  
echo - Advertisement image detection and blurring
echo - All images mode for maximum protection
echo - Real-time image processing with Flask API
echo - User-configurable blur settings
echo.
echo Press any key to open Chrome Extensions page...
pause > nul

start chrome://extensions/

echo.
echo Test environment ready! 
echo - Flask API: http://localhost:5000
echo - Test Page: test_image_blur.html
echo - Chrome Extensions: chrome://extensions/
echo.
echo Make sure to enable the Universal NSFW Filter extension!
echo.
pause
