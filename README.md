# RoomiePlatform

A comprehensive Django-based platform designed to help university students find compatible roommates and affordable shared accommodations.

## Project Overview

RoomiePlatform addresses the common challenge faced by university students in finding suitable living arrangements. The platform serves as a centralized marketplace where students can:

- **Find Roommates**: Browse profiles of potential roommates based on lifestyle preferences, budget, and location
- **List & Discover Rooms**: Room providers can list available spaces while seekers can search with detailed filtering options
- **Secure Bookings**: Request room bookings with a structured approval workflow
- **Communicate Safely**: Exchange messages within the platform to discuss arrangements
- **Get Support**: Access a dedicated support ticketing system for assistance

The application implements a user-friendly interface with responsive design, robust search functionality, and secure user authentication to create an end-to-end solution for student housing needs.

## RoomiePlatform Directory Structure

```
RoomiePlatform/
├── core/                   # Core application containing primary data models
│   ├── models.py           # Database models (User, Room, Message, Booking, etc.)
│   ├── admin.py            # Admin interface configurations
│   └── migrations/         # Database migration files
│
├── roomie/                 # Main application handling views and business logic
│   ├── forms.py            # Form definitions using factory pattern
│   ├── views.py            # View functions for all major features
│   ├── urls.py             # URL routing configurations
│   └── templates/          # HTML templates organized by feature
│       ├── home.html       # Landing page template
│       ├── dashboard.html  # User dashboard
│       ├── find_roommate.html # Roommate search interface
│       ├── filter_rooms.html # Room search and filtering
│       ├── room_detail.html # Individual room view
│       ├── user_profile.html # User profile display
│       ├── messages.html   # Messaging interface
│       ├── support_*.html  # Support system templates
│       └── auth/           # Authentication templates
│           ├── login.html  # User login page
│           └── register.html # User registration
│
├── static/                 # Static assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Image assets
│
├── media/                  # User-uploaded content
│   ├── profile_photos/     # User profile pictures
│   └── room_images/        # Room listing photos
│
├── templates/              # Project-wide templates
│   └── base.html           # Base template with common layout elements
│
├── manage.py               # Django management script
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## Current Status

The project has evolved from basic structure to a functional platform with these implemented features:

- **User Authentication**: Complete registration and login system with account type selection (seeker or provider)
- **Profile Management**: Users can create, view, and edit detailed profiles
- **Room Listings**: Providers can create, edit and manage room listings with multiple images
- **Advanced Search & Filtering**:
  - Room filtering by location, price range, room type, and availability
  - Roommate filtering by location, preferences, and availability status
- **Booking System**: Full booking workflow with request, approval/rejection, and status tracking
- **Messaging System**: In-platform messaging between users with read status tracking
- **Support Ticketing**: Help desk functionality with ticket submission and response system
- **Responsive UI**: Bootstrap-based interface that works across devices
- **Form Validation**: Server-side and client-side validation for all forms

The codebase follows several design patterns:

- Factory pattern for form creation
- Container class pattern for form organization
- Template inheritance for consistent UI

## Technology Stack

- **Backend**: Django 4.2+, Python 3.10+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: PostgreSQL (production), SQLite (development)
- **File Storage**: Django's FileField with local storage (AWS S3 ready)
- **Authentication**: Django's built-in authentication system
- **Form Handling**: Django Forms with custom validation

## Issues to Fix

While the platform is functional, these areas need improvement:

1. **User Profile Enhancement**

   - Add lifestyle preferences field to user profiles
   - Implement budget preferences for better matching
   - Fix template syntax errors in user_profile.html
   - Fix critical layout issues in user_profile page - profile information is poorly organized
   - Add missing profile completion percentage indicator

2. **Dashboard & Navigation Improvements**

   - Fix dashboard layout - cards are misaligned on medium screens
   - Improve dashboard statistics visualization
   - Add quick action buttons for common tasks
   - Fix navigation menu collapse issues on mobile devices
   - Implement proper breadcrumb navigation

3. **Room Listing Layout Issues**

   - Fix Featured Rooms detail page layout - images are disproportionate
   - Improve room amenities display in detail view
   - Fix spacing and alignment in room cards
   - Add proper image carousel for room photos
   - Implement proper grid layout for room listings on all screen sizes

4. **Search & Filter Optimization**

   - Improve search algorithm for better roommate matching
   - Add pagination for all listing pages
   - Ensure filter parameters persist across page navigation
   - Add saved search functionality

5. **Responsive Design Issues**

   - Fix mobile layout for room detail pages
   - Improve message thread display on small screens
   - Ensure consistent spacing and alignment
   - Fix form field rendering on small screens
   - Address overlapping elements in mobile view

6. **Performance Optimization**

   - Optimize database queries for room listings
   - Add caching for frequently accessed data
   - Implement lazy loading for images
   - Reduce page load time for image-heavy pages

7. **Security Enhancements**

   - Strengthen password policy
   - Add rate limiting for authentication attempts
   - Implement proper CSRF protection for all forms
   - Add session timeout for inactive users

8. **User Experience Improvements**

   - Add loading indicators for asynchronous operations
   - Implement proper error messages with clear solutions
   - Add tooltips for complex features
   - Improve form validation feedback
   - Add success messages for completed actions

9. **Accessibility Issues**

   - Improve color contrast for better readability
   - Add proper ARIA labels for interactive elements
   - Ensure keyboard navigation works throughout the site
   - Make forms accessible to screen readers
   - Add alt text to all images

10. **Content Management**
    - Implement moderation for user-generated content
    - Add reporting functionality for inappropriate listings
    - Create admin dashboard for content oversight
    - Add automatic content filtering for prohibited terms

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)
- virtualenv (recommended)

### Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/RoomiePlatform.git
   cd RoomiePlatform
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Visit http://127.0.0.1:8000 in your browser
   - Admin interface: http://127.0.0.1:8000/admin

## Future Enhancements

1. **AI Roommate Matching**

   - Implement machine learning algorithm for compatibility scoring
   - Add personality questionnaire for better matching

2. **Virtual Tours**

   - Add support for 360° room photos
   - Implement video tour scheduling

3. **Payment Integration**

   - Add secure deposit payment processing
   - Implement recurring rent payments

4. **Mobile Application**

   - Develop native mobile apps for iOS and Android
   - Implement push notifications

5. **Advanced Analytics**
   - Add dashboard with market insights for providers
   - Provide statistics on popular areas and price ranges

## Contributing

This project is currently a university project but may be open for contributions in the future. Documentation for contribution guidelines will be provided at that time.

## License

This project is developed for educational purposes. All rights reserved.
