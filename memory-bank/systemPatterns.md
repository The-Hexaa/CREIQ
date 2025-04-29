# System Patterns: CREIQ

## Architecture Overview

CREIQ follows a layered architecture with clear separation of concerns:

```
┌─────────────────┐
│  Main / CLI     │  Entry points and user interfaces
├─────────────────┤
│  Processor      │  Business logic for roll number processing
├─────────────────┤
│  Fetcher        │  URL fetching and content retrieval
├─────────────────┤
│  Parser         │  Content parsing and data extraction
├─────────────────┤
│  Database       │  Database storage and retrieval
└─────────────────┘
```

## Design Patterns

### 1. Singleton Pattern
- Used in the environment variable loading mechanism to ensure configuration is loaded only once
- Applied in the database connection to maintain a single connection pool

### 2. Factory Method Pattern
- Implemented in the URL generation to create URLs from roll numbers
- Used in the database manager to create sessions

### 3. Strategy Pattern
- Used in the fetcher module to allow different fetching strategies (retry logic, timeout handling)
- Applied in the parser module to handle different types of HTML content

### 4. Adapter Pattern
- Implemented in the database integration to abstract database operations across different backends
- Enables future migration from SQLite to PostgreSQL

### 5. Command Pattern
- Implemented in the CLI module to encapsulate operations as commands
- Used for database commands (init, store, query, export)

### 6. Composite Pattern
- Used in the data structure organization to represent hierarchical appeal data
- Applied in the ORM model relationships

### 7. Repository Pattern
- Implemented in the DatabaseManager class to abstract data access
- Provides methods for storing and retrieving objects without exposing implementation details

## Component Relationships

### RollNumberProcessor
- **Responsibility**: Process roll numbers from CSV files and generate URLs
- **Dependencies**: 
  - Python's CSV module
  - dotenv for environment variables
- **Interface**:
  - `load_roll_numbers()`: Loads roll numbers from CSV
  - `get_complete_urls()`: Generates complete URLs
  - `print_urls()`: Utility to print URLs

### URLFetcher
- **Responsibility**: Fetch content from URLs with robust error handling
- **Dependencies**:
  - requests library for HTTP requests
  - logging for operation tracking
- **Interface**:
  - `fetch_url(url)`: Fetch content from a single URL
  - `fetch_multiple_urls(urls)`: Fetch content from multiple URLs
  - Context manager interface (\_\_enter\_\_, \_\_exit\_\_)

### ARBParser
- **Responsibility**: Parse HTML content and extract structured data
- **Dependencies**:
  - BeautifulSoup for HTML parsing
  - URLFetcher for fetching appeal details
  - logging for operation tracking
- **Interface**:
  - `parse_appeal_listing(html_content, fetch_appeal_details)`: Parse appeal listing page
  - `parse_appeal_detail(html_content)`: Parse appeal detail page
  - Various private extraction methods for specific data elements

### DatabaseManager
- **Responsibility**: Handle database operations for storing and retrieving data
- **Dependencies**:
  - SQLAlchemy for ORM functionality
  - Database models (Property, Appeal, AppealDetail, etc.)
  - dateutil for date parsing
- **Interface**:
  - `create_tables()`: Create database tables
  - `store_data(parsed_data)`: Store parsed data in the database
  - `get_property_by_roll_number(roll_number)`: Get property by roll number
  - `get_appeal_by_number(appeal_number)`: Get appeal by appeal number
  - `get_appeals_by_property(roll_number)`: Get appeals for a property
  - `get_appeals_by_status(status)`: Get appeals by status

### CLI (Command Line Interface)
- **Responsibility**: Provide command-line access to functionality
- **Dependencies**:
  - argparse for command-line argument parsing
  - RollNumberProcessor, URLFetcher, ARBParser, and DatabaseManager
- **Interface**:
  - Command-line arguments for different operations
  - Database subcommands (init, store, query, export)
  - `main()`: Entry point for CLI

## Critical Implementation Paths

1. **Roll Number Processing Path**:
   ```
   CSV File → RollNumberProcessor → Clean Roll Numbers → Generate URLs
   ```

2. **Content Fetching Path**:
   ```
   URLs → URLFetcher → HTTP Requests → Response Handling → Content Storage
   ```

3. **Data Extraction Path**:
   ```
   HTML Content → ARBParser → Property & Appeal Extraction → Appeal Detail Fetching → Structured Data
   ```

4. **Database Storage Path**:
   ```
   Structured Data → DatabaseManager → ORM Models → Database Operations → SQLite Database
   ```

5. **Data Query Path**:
   ```
   Query Parameters → DatabaseManager → ORM Queries → SQLAlchemy Session → Result Objects
   ```

## Code Organization

The codebase is organized as a Python package with the following structure:

```
CREIQ/
│
├── src/                  # Source code
│   └── creiq/
│       ├── __init__.py   # Package initialization
│       ├── processor.py  # Roll number processing
│       ├── fetcher.py    # URL fetching
│       ├── parser.py     # HTML parsing
│       ├── cli.py        # Command-line interface
│       └── db/           # Database module
│           ├── __init__.py
│           ├── config.py # Database configuration
│           ├── models.py # ORM models
│           └── manager.py # Database operations
│
├── data/                 # Data files
│   ├── roll-number.csv   # Input CSV file
│   └── appeal-detail.html # Sample HTML for testing
│
├── tests/                # Test files
│   └── test_processor.py # Tests for processor
│
├── examples/             # Example scripts
│   ├── usage_example.py  # Basic usage example
│   └── db_integration_example.py # Database integration example
│
├── docs/                 # Documentation
│
├── main.py               # Main script entry point
├── setup.py              # Package setup
└── requirements.txt      # Dependencies
```

## Key Technical Decisions

1. **Python as the Primary Language**:
   - Chosen for its strong text processing and web capabilities
   - Rich ecosystem for HTTP requests and HTML parsing

2. **Modular Package Structure**:
   - Organized as a package for reusability
   - Clear separation of concerns

3. **Environment Variables for Configuration**:
   - Uses .env file for configuration to keep sensitive data out of code
   - Makes the application configurable without code changes

4. **HTTP Retry Mechanism**:
   - Implements retry logic for transient network failures
   - Configurable timeout and retry counts

5. **Context Managers for Resource Handling**:
   - Uses context managers for cleaning up resources automatically
   - Ensures proper session management

6. **HTML Parsing Strategy**:
   - Uses BeautifulSoup for parsing HTML content
   - Implementation separates extraction logic for different components
   - Structures data in a hierarchical format with clear categorization
   - Handles variations in HTML structure through robust selector strategies

7. **Data Organization**:
   - Organizes parsed data into logical sections (property_information, appellant_information)
   - Uses nested dictionaries to represent hierarchical relationships
   - Maintains explicit typing with type hints

8. **Database Design**:
   - Uses SQLAlchemy ORM for database abstraction
   - Implements a normalized database schema with proper relationships
   - Uses SQLite for simplicity but designed for easy migration to PostgreSQL
   - Implements eager loading for relationship queries to prevent DetachedInstanceError

9. **Session Management**:
   - Uses context managers for proper session handling and resource cleanup
   - Implements joinedload for eager loading of related objects
   - Handles session lifecycle to prevent database connection leaks