@Echo off
CD /d "%~dp0"

IF "%~1"=="" (
	SET VENV=.venv
) ELSE (
	SET "VENV=%~1"
)

%VENV%\Scripts\wfastcgi-enable
