# DjangoProject
Django Backend Project - Daily Work Update

Today’s Completed Tasks

1. Development Workspace Setup

* Created a new Django project workspace.
* Created and activated Python virtual environment.
* Installed required dependencies:
    * Django
    * Django REST Framework
    * PostgreSQL driver (psycopg)
    * python-dotenv
* Created requirements.txt using installed dependencies.

2. Django Project Setup

* Created enterprise Django project structure.
* Understood the purpose of Django files:
    * manage.py - Command-line utility to manage Django projects.
    * settings.py - Contains project configurations, installed apps, database settings, and environment settings.
    * urls.py - Handles URL routing.
    * wsgi.py - Entry point for WSGI-compatible servers.
    * asgi.py - Entry point for ASGI-compatible servers.
* Ran the development server and verified the Django welcome page.

3. PostgreSQL Database Configuration

* Installed and configured PostgreSQL.
* Created database and database user.
* Configured Django to connect with PostgreSQL.
* Executed initial migrations.
* Verified database tables.

4. Django Application Architecture

* Created application structure:
    * core - Contains core project-level functionality.
    * accounts - Handles user/account-related features.
    * common - Contains reusable common utilities.
* Understood why large Django projects are divided into multiple apps.

5. Environment Configuration

* Created .env file.
* Moved sensitive configurations into environment variables:
    * Secret Key
    * Database Name
    * Username
    * Password
    * Host
    * Port
* Updated Django settings to read values from .env.

6. Django REST Framework Setup

* Installed and configured Django REST Framework.
* Added DRF to INSTALLED_APPS.
* Created first API endpoint.
* Implemented JSON response.
* Tested API using browser and Postman.
* Understood Request and Response objects.

7. Custom User Model Implementation

* Researched the importance of creating a custom user model before initial migrations.
* Implemented custom user model with:
    * UUID as primary key
    * Email-based authentication
    * Required user fields
* Configured Django to use the custom user model.
* Ran migrations and verified database tables.

Technologies Used

* Python
* Django
* Django REST Framework
* PostgreSQL
* Git
* Postman
* python-dotenv
