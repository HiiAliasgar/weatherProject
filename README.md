<h1 align="center">Weather Forecast Project</h1>

<p align="center">
  <b>A Django web application for weather forecasting and data visualization</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
</p>

---

## Overview

A Django-based weather application that provides forecast data display with a user-friendly interface. Built as a full-stack web application using Django's MVC architecture.

### Features

| Feature | Description |
|---------|-------------|
| 🌤️ Weather Display | Current weather conditions |
| 📊 Data Visualization | Weather data charts and graphs |
| 🔍 City Search | Search weather by location |
| 📱 Responsive Design | Works on desktop and mobile |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/HiiAliasgar/weatherProject.git
cd weatherProject
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install django
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the server

```bash
python manage.py runserver
```

Open http://localhost:8000 in your browser.

---

## Project Structure

```
weatherProject/
├── forecast/           # Main app directory
│   ├── views.py       # View logic
│   ├── urls.py        # URL routing
│   ├── models.py      # Data models
│   └── templates/     # HTML templates
├── weatherProject/    # Project settings
│   ├── settings.py    # Django settings
│   └── urls.py        # Root URL config
├── manage.py          # Django CLI
├── weather.csv        # Weather data
└── .gitignore         # Git ignore rules
```

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core language |
| Django | Web framework |
| HTML/CSS | Frontend templates |
| JavaScript | Interactive features |

---

## Author

**Aliasgar Lohawala** - [@HiiAliasgar](https://github.com/HiiAliasgar)

---

<p align="center">
  Made with ❤️ and Django
</p>
