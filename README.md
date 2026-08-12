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

* # Enterprise Django Backend

## Project Overview
This project is a Django REST Framework backend implementing JWT-based user authentication.

## Features Implemented

### Task 1 - Authentication Flow
- Studied the authentication flow.
- Understood Registration, Login, Authentication, Authorization, JWT, and Refresh Tokens.

### Task 2 - Registration API
- Created user registration API.
- Added serializer and input validation.
- Implemented password validation.
- Tested:
  - Valid registration
  - Invalid request
  - Duplicate email
  - Missing required fields

### Task 3 - Login API
- Implemented login using email.
- Generated JWT Access Token and Refresh Token.
- Returned authenticated user details along with tokens.
- Tested login success and failure scenarios.

### Task 4 - JWT Authentication
- Configured JWT authentication.
- Protected API endpoints using authentication classes.
- Verified unauthorized requests return appropriate error responses.
- Implemented Profile API for authenticated users.

### Task 5 - Change Password API
- Created Change Password API.
- Validated current password.
- Added new password validation.
- Updated password securely using Django's password hashing.
- Tested successfully using Postman.

## Technologies Used
- Python
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- Postman

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/users/register/ | Register a new user |
| POST | /api/users/login/ | Login and generate JWT tokens |
| GET | /api/users/profile/ | Get authenticated user profile |
| POST | /api/users/change-password/ | Change user password |

## Authentication
Protected APIs require a valid JWT Access Token.

Authorization Header:

```
Authorization: Bearer <access_token>
```

## Testing
All APIs were tested successfully using Postman.

Django User Management API

Project Overview

This project is a Django REST Framework application developed to manage user authentication and user profiles securely. It uses JWT authentication and PostgreSQL for data storage. The project also includes API validation, image upload functionality, search, filtering, ordering, pagination, and Swagger documentation for easy API testing.

Features

* User Registration
* User Login with JWT Authentication
* User Profile Management (Create, View, Update, Delete)
* Change Password
* Logout with Token Blacklisting
* Profile Image Upload
* Search, Filtering, Ordering, and Pagination
* Input Validations (Email, Phone Number, Required Fields, Image Type and Size, Duplicate Records)
* Swagger API Documentation

Technologies Used

* Python
* Django
* Django REST Framework (DRF)
* PostgreSQL
* Simple JWT
* drf-yasg (Swagger)
* django-filter

API Documentation

The project includes Swagger UI for interactive API documentation, allowing all endpoints to be viewed and tested through the browser.

Conclusion

This project demonstrates a secure and well-structured REST API for user management with authentication, profile management, validation, and comprehensive API documentation.
# Django Backend Project

## Today's Work Update

### Task 1 – RBAC (Role-Based Access Control)
- Studied RBAC concepts.
- Learned the difference between Roles, Permissions, and Authorization.
- Prepared notes on how RBAC secures APIs.

### Task 2&3 – Roles & Permissions
- Implemented role-based access control.
- Created Admin and User roles.
- Assigned permissions based on roles.
- Protected APIs using custom permission classes.
- Verified that:
  - Anonymous users cannot access protected APIs.
  - Unauthorized users cannot access restricted resources.

### Task 4 – Soft Delete
- Added `is_deleted` field to the UserProfile model.
- Implemented soft delete functionality.
- Added profile restore functionality.
- Filtered only active (non-deleted) records.
- Tested all APIs successfully.

### Task 5 – Audit Fields
- Added audit fields:
  - `created_at`
  - `updated_at`
  - `created_by`
  - `updated_by`
- Configured automatic timestamp updates.
- Stored the authenticated user for create and update operations.
- Verified the audit fields using Postman.

### Task 6 – Logging & Exception Handling
- Configured centralized logging using Django logging.
- Generated application logs in `logs/django.log`.
- Added custom exception handling.
- Improved API error responses.
- Verified log generation for API requests.

### Task 7 – ORM Performance Optimization
- Learned and implemented `select_related()`.
- Studied `prefetch_related()`.
- Optimized database queries.
- Compared query count before and after optimization.

### Task 8 – Final Testing & Documentation
- Performed end-to-end API testing.
- Verified Login, Profile, Update, Soft Delete, and Restore APIs.
- Reviewed the project structure.
- Fixed identified issues.
- Committed completed work to Git.
- Prepared a demo explaining all implemented features.

- ## Task Completion Report — (10-Aug-2026)

### Task 1 — Select a Business Domain
**Learned:**
- Understood how to select a realistic business domain for a mobile application.
- Studied the Ride Booking domain as the reference example.
**Completed:**
- Selected Ride Booking as the business domain for the project.
### Task 2 — Design the Database
**Learned:**
- Learned how to convert business requirements into database entities and relationships.
- Understood Primary Keys and Foreign Keys.
- Learned One-to-One, One-to-Many, and Many-to-Many relationships.
**Completed:**
- Designed the Ride Booking database structure.
- Identified User, Driver Profile, Vehicle, Ride, and Pickup/Drop Location entities.
- Created the ER diagram and identified the required relationships.
- User
                          │
                       1 : 1
                          │
                          ▼
                   Driver Profile
                          │
                       1 : Many
                          │
                          ▼
                       Vehicle
                          │
                       1 : Many
                          │
                          ▼
                         Ride
                        /    \
                       /      \
                  Pickup      Drop
                 Location    Location

User ─────────── 1 : Many ─────────── Ride
Driver Profile ─ 1 : Many ─────────── Ride
Vehicle ───────── 1 : Many ────────── Ride

### Task 3 — Create Django Models
**Learned:**
- Learned how to create Django models for a real-world business module.
- Understood UUIDs, Foreign Keys, Choices, Constraints, Indexes, and Timestamps.
**Completed:**
- Created `DriverProfile`, `Vehicle`, `VehicleType`, `Ride`, and `RideStatus` models.
- Implemented UUIDs, relationships, choices, constraints, indexes, and timestamps.
### Task 4 — Understand Relationships
**Learned:**
- Practiced `ForeignKey`, `OneToOneField`, and `ManyToManyField`.
- Understood how related objects are accessed and queried in Django.
**Completed:**
- Created sample data using Django Shell.
- Tested One-to-One and One-to-Many relationships.
- Queried related objects successfully.
### Task 5 — Database Constraints
**Learned:**
- Learned how database constraints maintain data integrity.
- Understood Unique constraints, NOT NULL requirements, Choices, Indexes, and Composite constraints.
**Completed:**
- Implemented unique constraints for important fields.
- Applied required field/NOT NULL rules.
- Added valid choices for Ride Status.
- Added database indexes for frequently queried fields.
- Reviewed composite constraints based on business requirements.
### Task 6 — Django Admin
**Learned:**
- Learned how to manage business models through Django Admin.
- Understood list display, search, filters, and ordering.
**Completed:**
- Registered Ride Booking business models in Django Admin.
- Configured list display, search fields, filters, and ordering.
- Created and used a Django superuser to verify the Admin configuration.
### Task 7 — Migration Testing
**Learned:**
- Learned how Django migrations convert model changes into database changes.
- Understood `makemigrations`, `migrate`, migration status, rollback, and migration correction.
**Completed:**
- Created and applied Django migrations.
- Verified the generated PostgreSQL tables using pgAdmin4.
- Verified the Ride Booking tables:
  - `rides_driverprofile`
  - `rides_vehicle`
  - `rides_vehicletype`
  - `rides_ride`
- Reviewed and tested migration rollback and correction concepts.
### Task 8 — Documentation
**Learned:**
- Learned how to document database architecture and business rules clearly.
- Understood how to document ER diagrams, models, relationships, constraints, and business rules.
**Completed:**
- Documented the ER diagram.
- Documented Django models and relationships.
- Documented business rules and database constraints.
- Added the complete project documentation to the README.
### Final Status
**Tasks 1–8: Completed Successfully ✅**
The complete Ride Booking database architecture, Django implementation, PostgreSQL migration, Django Admin configuration, testing, and documentation have been completed and pushed to GitHub.

Driver & Vehicle Management API (11th august 2026)

Implemented a Driver and Vehicle Management backend using Django REST Framework and PostgreSQL, with authentication, authorization, validation, filtering, nested responses, and API error handling.
Implemented Features
1. Driver Management
* Created DriverProfile model with UUID-based identification and user relationship.
* Implemented Driver APIs for creating, retrieving, listing, and updating driver profiles.
* Added serializer-based validation for driver-related data.
* Added role-based access control for driver management.

2. Vehicle Management
* Created Vehicle and VehicleType models with relationships to drivers.
* Implemented Vehicle APIs for:
    * Create
    * List
    * Retrieve
    * Update
    * Delete
* Added validation for vehicle registration numbers, vehicle types, and driver references.
* Prevented duplicate vehicle registration numbers.

3. API Validation
Implemented serializer-level validations to ensure:
* Required fields are provided.
* Vehicle registration numbers are valid and normalized.
* Driver IDs are valid.
* Vehicle type IDs are valid.
* Duplicate vehicle registrations are rejected.
* Invalid data returns appropriate validation errors.

4. Role-Based Permissions
Implemented permission rules for different user roles:

* Admin can manage all drivers and vehicles.
* Drivers can manage their own vehicles.
* Normal users cannot modify driver information.
* Protected APIs against unauthorized and forbidden access.

5. Nested API Responses
Implemented nested responses to provide driver and vehicle information together.
6. Search, Filtering & Pagination
Implemented API query features including:
* Driver search by license number and user email.
* Vehicle search and vehicle-type filtering.
* Active/inactive driver filtering.
* Page-number pagination.
* Ordering by rating and timestamps.
* Combination of search, filters, pagination, and ordering.
7. API Error Handling
Implemented proper HTTP error responses for common API scenarios:

* 400 Bad Request for invalid data and duplicate registrations.
* 401 Unauthorized for unauthenticated requests.
* 403 Forbidden for unauthorized operations.
* 404 Not Found for non-existing drivers and vehicles.
8. API Testing

Performed end-to-end testing using Postman covering:
* Positive and negative scenarios.
* Authentication and authorization.
* Role-based permissions.
* Serializer validations.
* Search and filtering.
* Pagination and ordering.
* Error handling and edge cases.
Successfully developed a secure and validated Driver & Vehicle Management API with role-based authorization, relational data handling, nested responses, search/filtering capabilities, pagination, and comprehensive API testing.

Ride Management Module (aug 12th 2026)
Implemented the complete Ride Management module with end-to-end APIs and tested all major scenarios using Postman.
Features Implemented

* Ride Lifecycle: REQUESTED → ACCEPTED → DRIVER_ARRIVING → STARTED → COMPLETED
* Create Ride API: Create a ride with pickup, drop location, ride type, and passenger.
* Ride Validations: Authentication, location validation, ride type validation, and active ride conflict checks.
* Ride Details API: View passenger, driver, vehicle, locations, status, fare, and timestamps.
* Ride Status API: Controlled status transitions with invalid transitions rejected.
* Driver Accept Ride: Validates driver authentication, active status, conflicting rides, and ride availability.
* Cancel Ride: Handles valid cancellation rules and prevents invalid cancellations.
* End-to-End Testing: Tested complete ride lifecycle and invalid scenarios successfully in Postman.
Testing
All Ride Management APIs were tested successfully using Postman, including both valid and invalid scenarios.
Git
All Ride Management changes have been committed and pushed to GitHub.



