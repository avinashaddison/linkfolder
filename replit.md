# Link Extractor

## Overview

Link Extractor is a Flask-based web application that extracts and categorizes all links from any given webpage URL. The application provides both a web interface and API endpoints for link extraction, featuring real-time categorization of links (internal, external, images, documents, etc.) and a responsive Bootstrap-based UI with dark theme support.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask for server-side rendering
- **UI Framework**: Bootstrap 5 with dark theme support and Font Awesome icons
- **JavaScript**: Vanilla JavaScript for client-side interactions, form handling, and copy functionality
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Web Framework**: Flask with modular structure separating concerns
- **Main Application**: `app.py` handles routing, request processing, and template rendering
- **Core Logic**: `link_extractor.py` contains the LinkExtractor class for web scraping and link categorization
- **Entry Point**: `main.py` serves as the application launcher

### Link Extraction Engine
- **Web Scraping**: BeautifulSoup for HTML parsing with requests library for HTTP handling
- **URL Processing**: urllib.parse for URL normalization and validation
- **Categorization**: Custom logic to classify links by type (internal, external, images, documents)
- **Error Handling**: Comprehensive exception handling with user-friendly error messages

### API Design
- **Web Interface**: Form-based POST requests to `/extract` endpoint
- **REST API**: JSON API endpoint at `/api/extract` for programmatic access
- **Response Format**: Structured JSON responses with links, categories, and metadata

### Session Management
- **Flask Sessions**: Secret key-based session handling for flash messages
- **Environment Configuration**: Configurable session secret via environment variables

## External Dependencies

### Core Libraries
- **Flask**: Web framework for routing and templating
- **BeautifulSoup4**: HTML parsing and DOM manipulation
- **Requests**: HTTP client library with session management and custom headers

### Frontend Dependencies
- **Bootstrap 5**: CSS framework with dark theme from cdn.replit.com
- **Font Awesome 6.4.0**: Icon library via CDN
- **JavaScript**: Native browser APIs for clipboard operations and DOM manipulation

### Development Tools
- **Python Logging**: Built-in logging module for debugging and error tracking
- **Environment Variables**: OS environment for configuration management

### Browser Compatibility
- **User Agent**: Configured to mimic modern Chrome browser for better website compatibility
- **Timeout Handling**: 10-second request timeout for responsive user experience