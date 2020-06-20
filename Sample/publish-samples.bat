@Echo off

IF "%1"=="" GOTO USAGE
SET "DESTINATION=%~1"
IF NOT EXIST "%DESTINATION%" GOTO USAGE

CD /d "%~dp0"
RoboCopy . "%DESTINATION%" /s /xf *.user publish.bat /xd __pycache__ env obj bin utilities .vs
copy /y nul "%DESTINATION%\PyWebApi.IIS\log\wfastcgi.log" > nul
Goto:Eof

:USAGE
Echo Usage:
Echo     publish-samples destination_directory
Echo:
Echo     The destination directory for publishing is required to exist.
