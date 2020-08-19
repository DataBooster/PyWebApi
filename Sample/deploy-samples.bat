@Echo off

IF "%1"=="" GOTO USAGE
SET "DESTINATION=%~1"
IF NOT EXIST "%DESTINATION%" GOTO USAGE

CD /d "%~dp0"
RoboCopy .\PyWebApi.IIS "%DESTINATION%" /s /xf *.user *.pyproj /xd __pycache__ *env obj bin user-script-root .vs
Copy /y nul "%DESTINATION%\log\wfastcgi.log" > nul

RoboCopy .\UserApps "%DESTINATION%\user-script-root\samples" /s /xf *.user *.pyproj deploy.bat /xd __pycache__ *env obj bin AdomdClient_From_NuGet .vs

For /f "delims=" %%a in ('dir /b /s "%DESTINATION%\user-script-root\samples\requirements.txt"') do type %%a >> "%DESTINATION%\requirements.txt"

Sort /C /UNIQUE "%DESTINATION%\requirements.txt" /O "%DESTINATION%\requirements.txt"

Copy /y setup-venv.bat "%DESTINATION%"

Goto:eof

:USAGE
Echo:
Echo Usage:
Echo:
Echo     deploy-samples destination_directory
Echo:
Echo     The destination directory for deploying is required to exist.
