import sys
import json
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).resolve().parent / 'src'
sys.path.append(str(src_path))

from creiq.processor import RollNumberProcessor
from creiq.fetcher import URLFetcher
from creiq.parser import ARBParser
from creiq.db import DatabaseManager


def main():
    """
    Main entry point for the CREIQ application.
    
    Performs the complete workflow:
    1. Process roll numbers from CSV
    2. Generate URLs
    3. Fetch content
    4. Parse HTML content
    5. Initialize database
    6. Store parsed data in the database
    7. Display a summary of stored data
    """
    # Step 1: Initialize the processor and get URLs
    print("Step 1: Processing roll numbers and generating URLs...")
    processor = RollNumberProcessor('data/roll-number.csv')
    processor.load_roll_numbers()
    urls = processor.get_complete_urls()
    
    print(f"Generated {len(urls)} URLs from roll numbers.")
    
    # Step 2: Fetch content from the URLs
    print("\nStep 2: Fetching content from URLs...")
    results_file = 'results.json'
    parsed_results_file = 'parsed_results.json'
    
    # Check if results already exist
    if os.path.exists(results_file):
        fetch_again = input(f"\nResults file '{results_file}' already exists. Fetch again? (y/n): ").lower() == 'y'
    else:
        fetch_again = True
    
    if fetch_again:
        with URLFetcher() as fetcher:
            results = fetcher.fetch_multiple_urls(urls)
        
        # Count successes and failures
        success_count = sum(1 for result in results.values() if result[0])
        failure_count = len(results) - success_count
        
        print(f"Fetch completed: {success_count} successful, {failure_count} failed")
        
        # Convert results to a serializable format
        serializable_results = {}
        for url, (success, content_or_error) in results.items():
            if success:
                serializable_results[url] = {
                    'success': True,
                    'content': content_or_error
                }
            else:
                serializable_results[url] = {
                    'success': False,
                    'error': str(content_or_error)
                }
        
        # Save to file
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"Results saved to {results_file}")
    else:
        print(f"Using existing results from {results_file}")
        with open(results_file, 'r', encoding='utf-8') as f:
            serializable_results = json.load(f)
    
    # Step 3: Parse the HTML content
    print("\nStep 3: Parsing HTML content...")
    
    # Check if parsed results already exist
    if os.path.exists(parsed_results_file):
        parse_again = input(f"\nParsed results file '{parsed_results_file}' already exists. Parse again? (y/n): ").lower() == 'y'
    else:
        parse_again = True
    
    if parse_again:
        # Initialize parser
        parser = ARBParser()
        
        # Convert from serializable format back to the expected format for parsing
        raw_results = {}
        for url, data in serializable_results.items():
            if data.get('success', False):
                raw_results[url] = (True, data['content'])
            else:
                raw_results[url] = (False, data.get('error', 'Unknown error'))
        
        # Parse each successful result with detail fetching enabled
        parsed_results = {}
        for url, (success, content_or_error) in raw_results.items():
            if success:
                try:
                    # Use True to fetch appeal details
                    parsed_data = parser.parse_appeal_listing(content_or_error, True)
                    parsed_results[url] = parsed_data
                    print(f"Successfully parsed content from {url}")
                except Exception as e:
                    print(f"Error parsing content from {url}: {str(e)}")
            else:
                print(f"Skipping parsing for {url} due to fetch failure: {content_or_error}")
        
        # Save parsed results to file
        with open(parsed_results_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, indent=2)
        
        print(f"Parsed results saved to {parsed_results_file}")
    else:
        print(f"Using existing parsed results from {parsed_results_file}")
        with open(parsed_results_file, 'r', encoding='utf-8') as f:
            parsed_results = json.load(f)
    
    # Step 4: Initialize database and store data
    print("\nStep 4: Initializing database and storing data...")
    
    # Create database manager
    db_manager = DatabaseManager()
    
    # Create tables if they don't exist
    db_manager.create_tables()
    print("Database tables initialized.")
    
    # Store parsed data in the database
    db_manager.store_data(parsed_results)
    print("Data stored in the database.")
    
    # Step 5: Display a summary of stored data
    print("\nStep 5: Summary of database contents:")
    
    # Get a sample roll number from the first URL
    sample_url = list(parsed_results.keys())[0]
    sample_data = parsed_results[sample_url]
    sample_roll_number = sample_data.get('property_info', {}).get('roll_number')
    
    if sample_roll_number:
        property_info = db_manager.get_property_by_roll_number(sample_roll_number)
        appeals = db_manager.get_appeals_by_property(sample_roll_number)
        
        if property_info:
            print(f"\nSample Property: {property_info.roll_number}")
            print(f"Description: {property_info.property_description}")
            
            if appeals:
                print(f"\nFound {len(appeals)} appeals for this property.")
                
                # Display statuses
                statuses = {}
                for appeal in appeals:
                    status = appeal.status
                    statuses[status] = statuses.get(status, 0) + 1
                
                print("\nAppeal statuses:")
                for status, count in statuses.items():
                    print(f"  - {status}: {count}")
                
                # Display a few appeal numbers as examples
                print("\nSample appeal numbers:")
                for i, appeal in enumerate(appeals[:5], 1):
                    print(f"  {i}. {appeal.appeal_number} ({appeal.status})")
                
                if len(appeals) > 5:
                    print(f"  ...and {len(appeals) - 5} more")
    
    print("\nOperation completed successfully. All data is now stored in the database.")
    print("To query the database, use the CLI commands:")
    print("  python -m creiq.cli db query --roll-number <roll_number> --detailed")
    print("  python -m creiq.cli db query --appeal-number <appeal_number>")
    print("  python -m creiq.cli db query --status <status>")
    
    return parsed_results


if __name__ == "__main__":
    main()