@Echo off
CD /d "%~dp0"

IF "%~1"=="" GOTO USAGE

SET "VENV=%~1"

IF EXIST "%VENV%" (
	Echo The target directory "%VENV%" already exists!
	GOTO:EOF
)

python.exe -m venv %*

IF ERRORLEVEL 1 (
	Echo Please temporarily add your Python installation directory to the PATH environment variable and try again.
	GOTO:EOF
)

call "%VENV%\Scripts\activate.bat"

pip install -r requirements.txt

call wfastcgi-enable.bat "%VENV%"

Goto:eof

:USAGE
Echo:
Echo Usage:
Echo:
Echo     setup-venv ENV_DIR
Echo:
Echo     ENV_DIR: A directory to create the environment in.
Echo:
Echo:
Echo Example:
Echo:
Echo     setup-venv .venv
Echo:
