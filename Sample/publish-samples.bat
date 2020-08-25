@Echo off

IF "%1"=="" GOTO USAGE
SET "DESTINATION=%~1"
IF NOT EXIST "%DESTINATION%" GOTO USAGE

CD /d "%~dp0"
RoboCopy . "%DESTINATION%" /s /xf *.user publish-samples.bat /xd __pycache__ *env obj bin samples .vs

IF NOT EXIST "%DESTINATION%\PyWebApi.IIS\log" MKDIR "%DESTINATION%\PyWebApi.IIS\log"
Copy /y nul "%DESTINATION%\PyWebApi.IIS\log\wfastcgi.log" > nul

Goto:eof

:USAGE
Echo:
Echo Usage:
Echo:
Echo     publish-samples destination_directory
Echo:
Echo     The destination directory for publishing is required to exist.
