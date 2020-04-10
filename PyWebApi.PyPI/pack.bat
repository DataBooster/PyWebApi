@Echo off
CD /d "%~dp0"
env\Scripts\python.exe setup.py bdist_wheel --universal
