# peppol-python-demo

A Django-based demo server that shows how to use the peppol-python library

# Command line (recommended: use a virtual environment)

**git clone https://github.com/pondersource/peppol-python-demo**

**cd peppol-python-demo**

**pip install -r requirements.txt**

export DATABASE_URL=postgres://...

**python manage.py makemigrations** 

**python manage.py migrate**

**python manage.py runserver**

# Superuser 

To create a superuser first run:

**python3 manage.py createsuperuser**

