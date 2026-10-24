@echo off
title Push Savory AI Bistro to GitHub
echo ===================================================
echo   Pushing Savory AI Bistro to GitHub (Thota-Usha)
echo ===================================================
echo.
cd /d "%~dp0"
git push -u origin main
echo.
echo If it succeeded, go back to Vercel and refresh to see savory-ai-bistro!
pause
