# MkDocs
Start-Process powershell -ArgumentList '-NoExit -Command python -m mkdocs serve -a 127.0.0.1:8888'

# Django
# activate myenv rom ROOT directory
.\myenv\Scripts\Activate.ps1;

# Django -> in new windor from folder project -> runserver
Start-Process powershell -ArgumentList '-NoExit -Command python manage.py runserver'  


