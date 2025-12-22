@echo off
setlocal enabledelayedexpansion

set /a count=1

for /f "delims=" %%f in ('dir /b /on "1 (*.backup"') do (
    ren "%%f" "!count!.sql"
    set /a count+=1
)

echo Renaming complete. Files are now named 1.sql to %count%.sql (or up to 33.sql).
pause