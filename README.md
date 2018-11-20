set FLASK_APP=application.py

flask run


*For some reason it works when I deploy on AWS console on website but not through command line*


eb init -p python-3.6 flask-tutorial --region us-east-2

eb create flask-env

eb open

eb terminate flask-env






flask db init

flask db migrate

flask db upgrade
