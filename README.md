# CGPA Calculator (Django)

## Run it
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Open http://127.0.0.1:8000

Optional: `python manage.py createsuperuser` (admin at /admin/)
Run tests: `python manage.py test`

Note: the UI loads Tailwind from a CDN, so an internet connection is needed for styling.
