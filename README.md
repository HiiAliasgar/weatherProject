# Weather Forecast Application

A Django-based web application for displaying weather information and presenting weather data through a simple browser interface.

## Features described by the application

- Search weather information by city.
- Display current weather conditions.
- Present weather data with charts or visual summaries.
- Responsive page layout for desktop and mobile screens.

## Technology

- Python
- Django
- HTML and CSS
- JavaScript

## Run locally

```bash
git clone https://github.com/HiiAliasgar/weatherProject.git
cd weatherProject

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install django
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

Install any additional dependencies required by the current application code before running it. If the project uses an external weather-data provider, configure its credentials according to the source code and keep them out of version control.

## Project layout

```text
weatherProject/
├── forecast/             # Main Django application
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   └── templates/
├── weatherProject/       # Django project configuration
├── manage.py
└── weather.csv           # Project data
```

## Scope

This repository is a learning project for Django-based web development and weather-data presentation. Check the current source and configuration before assuming a live deployment or a specific external data provider.

[Source code](https://github.com/HiiAliasgar/weatherProject)
