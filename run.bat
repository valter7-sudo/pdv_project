@echo off
cd /d C:\pdv_project
call venv\Scripts\activate
set FLASK_APP=backend:create_app
set FLASK_DEBUG=1
flask run
pause
