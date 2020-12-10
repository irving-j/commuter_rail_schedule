# commuter_rail_schedule
This is a Django application with a ReactJS front end to display a commuter rail schedule for the current date and time.
It is recommended you use a virtual environment with Python3.7. In this example we'll pip and venv. 

Make sure to install Django and requests modules within your virtual environment.

`pip istall django django-cors-headers requests`

Once Django and requests module is installed, run the following:

cd into the root and run

`python manage.py runserver`

Verify the api is up and running

`localhost:8000`

Next cd into webapp and run 
`yarn start`

Verify the application is running.

Note: you might have to reload the Django app to apply cors or proxy.