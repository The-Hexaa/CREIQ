# Technical Context: CREIQ

## Technologies Used

### Core Technologies
- **Python 3.6+**: Main programming language
- **requests**: HTTP library for fetching web content
- **python-dotenv**: For environment variable management
- **argparse**: For command-line argument parsing
- **csv**: For processing CSV files
- **json**: For storing and processing JSON data

### Future Technologies
- **BeautifulSoup/lxml**: For HTML parsing and data extraction
- **SQLite/PostgreSQL**: For database storage
- **SQLAlchemy**: ORM for database operations

## Development Setup

### Environment Setup
1. Python 3.6+ installed
2. Virtual environment recommended
3. Dependencies installed via requirements.txt
4. .env file with URL configuration

### Installation Steps
```bash
# Clone the repository
git clone <repository-url>

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Configuration
A `.env` file is required with the following variables:
```
URL=https://arbesc.arb.gov.on.ca/arbecs/Default?r=
```

## Build and Execution

### Installation
The package can be installed in development mode:
```bash
pip install -e .
```

### Running the Application
There are multiple ways to run the application:

1. **Using main.py**:
   ```bash
   python main.py
   ```

2. **Using CLI after installation**:
   ```bash
   creiq --print
   creiq --fetch --output results.json
   ```

3. **Programmatically**:
   ```python
   from creiq.processor import RollNumberProcessor
   from creiq.fetcher import URLFetcher
   
   processor = RollNumberProcessor('data/roll-number.csv')
   urls = processor.get_complete_urls()
   
   with URLFetcher() as fetcher:
       results = fetcher.fetch_multiple_urls(urls)
   ```

## Testing

### Test Framework
- **unittest**: Python's built-in testing framework

### Running Tests
```bash
python -m unittest discover tests
```

## Dependencies

### Core Dependencies
- **python-dotenv==1.0.0**: For loading environment variables
- **requests==2.31.0**: For HTTP requests

### Development Dependencies
- No development dependencies specified yet

## Code Standards

### Formatting
- PEP 8 coding style
- Docstrings for all classes and methods

### Documentation
- README.md for project overview
- Docstrings using Google style format

## Deployment

### Packaging
The project is packaged following standard Python packaging conventions:
- setup.py with package metadata
- requirements.txt for dependencies

### Distribution
Currently set up for local development, not published to PyPI.

## Monitoring and Logging

### Logging
- Uses Python's built-in logging module
- Configurable log levels for different components
- Console logging for development