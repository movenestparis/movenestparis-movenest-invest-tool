# Real Estate Investment Calculator

## Overview

This is a bilingual (French/Arabic) real estate investment calculator web application built with Flask. The application allows users to analyze the financial viability of real estate investments by calculating various metrics including NPV, IRR, cash flow, and yield ratios. It features comprehensive loan analysis capabilities and provides professional-grade financial insights for real estate investment decisions.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Styling**: Custom CSS with MoveNest brand colors and Font Awesome icons
- **JavaScript**: Vanilla JavaScript for form validation and dynamic field toggling
- **Internationalization**: Session-based language switching between French and Arabic with RTL support

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Session Management**: Flask sessions for maintaining user state and form data
- **Calculation Engine**: Object-oriented calculator class with comprehensive financial modeling
- **Translation System**: Dictionary-based translation management for multilingual support

### Key Design Patterns
- **MVC Pattern**: Clear separation between models (calculator), views (templates), and controllers (Flask routes)
- **Factory Pattern**: Translation system that returns language-specific dictionaries
- **Session State Management**: Form data persistence across language switches

## Key Components

### Core Application Files
- **`app.py`**: Main Flask application with routing logic and session management
- **`calculator.py`**: RealEstateCalculator class containing all financial calculation methods
- **`translations.py`**: Internationalization system supporting French and Arabic languages
- **`main.py`**: Application entry point for development and production deployment

### Frontend Components
- **`templates/index.html`**: Main application template with form inputs and results display
- **`static/css/style.css`**: Custom styling with MoveNest brand guidelines
- **`static/js/script.js`**: Client-side form validation and UI interactions

### Financial Calculation Features
- Property acquisition costs (price, notary fees, renovation)
- Rental income projections with vacancy considerations
- Operating expenses (charges, taxes, CAPEX)
- Loan analysis with payment calculations
- NPV calculations for 3, 5, and 10-year periods
- IRR computation for investment returns
- Monthly cash flow analysis

## Data Flow

1. **User Input**: Form data collected through Bootstrap-styled interface
2. **Session Storage**: Form data persisted in Flask sessions for language switching
3. **Calculation Processing**: RealEstateCalculator processes input parameters
4. **Financial Modeling**: NumPy-powered calculations for NPV, IRR, and cash flows
5. **Results Display**: Formatted results rendered in user's selected language
6. **State Persistence**: Session maintains both language preference and form data

### Calculation Pipeline
```
Input Validation → Calculator Instantiation → Financial Metrics → Results Formatting → Template Rendering
```

## External Dependencies

### Python Dependencies
- **Flask 3.1.1**: Web framework and routing
- **NumPy 2.3.1**: Financial calculations and array operations
- **Gunicorn 23.0.0**: WSGI HTTP server for production deployment
- **email-validator 2.2.0**: Input validation utilities
- **psycopg2-binary 2.9.10**: PostgreSQL adapter (future database integration)
- **Flask-SQLAlchemy 3.1.1**: ORM for future database features

### Frontend Dependencies
- **Bootstrap 5.3.0**: CSS framework for responsive design
- **Font Awesome 6.4.0**: Icon library for enhanced UI

### Infrastructure Dependencies
- **PostgreSQL**: Database system (configured but not yet implemented)
- **OpenSSL**: Security and encryption support

## Deployment Strategy

### Development Environment
- **Python 3.11**: Runtime environment
- **Flask development server**: Hot reload capability
- **Debug mode**: Enhanced error reporting and logging

### Production Deployment
- **Gunicorn WSGI server**: Production-grade application server
- **Autoscale deployment target**: Horizontal scaling capability
- **Port 5000**: Standard Flask application port
- **Environment variables**: Secure session key management

### Configuration Management
- **Nix packages**: Reproducible dependency management
- **pyproject.toml**: Modern Python packaging and dependency specification
- **uv.lock**: Deterministic dependency resolution

## Changelog

```
Changelog:
- June 22, 2025. Initial setup with Flask real estate calculator
- June 22, 2025. Updated to authentic MoveNest brand colors (Stromboli Green #2e5e4e, Ivory White #f7f5ef)
- June 22, 2025. Enhanced with advanced financial tools (DSCR, break-even rent, scenario analysis)
- June 22, 2025. Added NPV chart, tooltips, PDF export, and corrected loan payoff calculation
- June 22, 2025. Implemented annual rent and charges escalation for realistic projections
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```