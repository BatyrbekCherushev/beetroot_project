
# ACTIVATE ENVIRONMENT myenv rom ROOT directory
.\venv\Scripts\Activate.ps1;

# MkDocs SERVER
python -m mkdocs serve -a 127.0.0.1:8888

# СТВОРЕННЯ файлу requirements.txt
pip freeze > requirements.txt

# DJANGO SERVER IN NEW WINDOW
Start-Process powershell -ArgumentList '-NoExit -Command python manage.py runserver'  


