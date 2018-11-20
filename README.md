set FLASK_APP=application.py
flask run

eb init -p python-3.6 flask-tutorial --region us-east-2
eb create flask-env
eb open
eb terminate flask-env



flask db init
flask db migrate
flask db upgrade