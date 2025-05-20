# Gym Management System - Project Documentation

## Overview
This Django Rest Framework (DRF) project implements a Gym Management System designed to work with a Flutter app. The system allows for member registration, authentication, and tracking of gym sessions.

## Features
1. Member registration and authentication using JWT
2. Phone number and password-based login
3. Automatic tracking of gym sessions when members enter and exit
4. Automatic reset of all members' status at midnight
5. API documentation with Swagger/OpenAPI

## Project Structure
- `gym/` - Main application directory
  - `models.py` - Contains Member and GymSession models
  - `views.py` - API endpoints implementation
  - `serializers.py` - Data serialization for API
  - `urls.py` - URL routing for API endpoints
  - `admin.py` - Admin panel configuration
  - `management/commands/` - Custom management commands
    - `reset_gym_status.py` - Command to reset members' status at midnight

## API Endpoints
- `/api/register/` - Register new members
- `/api/login/` - Authenticate members with phone number and password
- `/api/token/refresh/` - Refresh JWT token
- `/api/members/` - List all members (admin only)
- `/api/members/<id>/` - View and update member details
- `/api/members/<id>/enter/` - Record member entry to gym
- `/api/members/<id>/exit/` - Record member exit from gym and create session
- `/api/sessions/` - List gym sessions

## Authentication
The system uses JWT (JSON Web Token) authentication. When a user logs in or registers, they receive an access token and a refresh token. The access token should be included in the Authorization header for subsequent requests.

## Scheduled Tasks
To reset all members' `is_in_gym` status at midnight, set up a cron job to run:
```
python manage.py reset_gym_status
```

## Documentation
API documentation is available at:
- `/swagger/` - Swagger UI
- `/redoc/` - ReDoc UI

## Getting Started
1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run the server: `python manage.py runserver`
