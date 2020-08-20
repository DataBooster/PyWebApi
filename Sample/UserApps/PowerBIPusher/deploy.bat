@Echo off
CD /d "%~dp0"
SETLOCAL EnableDelayedExpansion EnableExtensions

IF "%~1"=="" (
	For %%l in (.) Do SET FOLDER=%%~nxl
	SET "DESTINATION=..\..\PyWebApi.IIS\user-script-root\samples\!FOLDER!"
) ELSE (
	SET "DESTINATION=%~1"
)

RoboCopy . "!DESTINATION!" /s /purge /xf *.pyproj *.bak deploy.bat /xd __pycache__

FOR /f "delims=" %%i in ('dir pywintypes??.dll /s /b') DO (
	SET SOURCE=%%i
	IF "!SOURCE:~-4!"==".dll" (
		Copy "!SOURCE!" "!DESTINATION!" /y
	)
)

ENDLOCAL
