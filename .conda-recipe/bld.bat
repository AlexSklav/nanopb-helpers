@echo off

REM Copy `nanopb-helpers` C source and headers to Arduino
copy lib\nanopb\src\*.h "%PREFIX%"\Library\include\Arduino\nanopb\src

"%PYTHON%" setup.py install --single-version-externally-managed --record record.txt
if errorlevel 1 exit 1
