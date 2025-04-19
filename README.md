# RoomiePlatform

A Django-based platform for university students to find roommates and shared accommodations.

RoomiePlatform/
├── core/ # Core app with models
├── message/ # Messaging functionality
├── roomie/ # Main application
│ ├── forms.py # Form definitions
│ ├── views.py # View functions
│ ├── urls.py # URL patterns
│ └── templates/ # HTML templates
└── templates/ # Project-wide templates
└── base.html # Base template

## Project Overview

RoomiePlatform helps students find compatible roommates and affordable housing. The system manages user accounts, room listings, roommate profiles, bookings, and communication between users.

## Current Status

The project has a basic structure with:

- Models for rooms, roommate profiles, bookings, contracts
- Form classes organized in a container class (RoomieForms)
- Form factory pattern for form creation
- Basic views for user authentication
- Login template with client-side validation

## Issues to Fix

1. **Form Integration**: Login form is currently using client-side JavaScript for validation instead of Django's authentication system.

2. **View-Form Connection**: The `user_login` view needs proper integration with the RoomieFormFactory.

3. **Template-Form Binding**: Templates need to correctly render Django form fields with proper error handling.

4. **Missing Models Implementation**: Some model metadata and relationships may be incomplete.

5. **Authentication Flow**: The registration and login process needs to be fully connected.

## Tasks to Complete

### Essential Tasks

1. **Fix Authentication System**

   - Update login.html to use Django form instead of fake login function
   - Ensure user_login view correctly uses the form factory
   - Add proper error handling and validation

2. **Complete Room Management**

   - Create a template for listing rooms
   - Add a view for creating and editing room listings
   - Implement room search functionality

3. **Implement Roommate Profile System**

   - Create profile creation/editing template
   - Connect profile view to form factory
   - Add ability to view other users' profiles

4. **Add Booking Functionality**

   - Create booking form template
   - Implement booking request and approval flow
   - Add booking history for users

5. **Create Basic Messaging System**
   - Add message listing page
   - Create conversation view
   - Implement message sending between users

### Additional Tasks

6. **Create Error Pages**

   - Add 404 error page
   - Add 500 error page
   - Add permission denied page

7. **Add Data Validation**

   - Implement form validation for all forms
   - Add model validation constraints
   - Create meaningful error messages

8. **Enhance User Interface**

   - Add consistent styling across templates
   - Improve form layout and user experience
   - Add responsive design elements

9. **Add Sample Data**

   - Create fixtures for testing
   - Add demo users and room listings

10. **Implement Basic Testing**
    - Add model tests
    - Add form validation tests
    - Add view function tests

## Submission Requirements

For this university project, ensure you have completed:

1. **Documentation**

   - Update this README with final implementation details
   - Document key design decisions
   - Include setup instructions

2. **Core Functionality**

   - User authentication (login/register)
   - Room listing management
   - Roommate profile management
   - Basic messaging between users

3. **Data Integrity**

   - Proper model relationships
   - Form validation
   - Data storage security

4. **User Experience**
   - Intuitive navigation
   - Error feedback
   - Responsive design basics

## Project Structure

The project follows a standard Django structure with these main components:

- **core/**: Essential models and functionality
- **message/**: Messaging system
- **roomie/**: Main application with forms, views, and templates

Complete these tasks systematically to create a functional roommate matching platform that meets university project requirements.
