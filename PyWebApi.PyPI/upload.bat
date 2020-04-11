@Echo off
CD /d "%~dp0"
env\Scripts\twine.exe upload dist/*
