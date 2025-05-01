"""
Module for browser automation to interact with the ARB website using Playwright.
"""

import os
import time
import re
import json
import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext


class PlaywrightAutomation:
    """
    A base class for automating interactions with the ARB website using Playwright.
    """
    
    def __init__(self, headless: bool = False):
        """
        Initialize the Playwright automation with browser settings.
        
        Args:
            headless (bool): Whether to run the browser in headless mode (default: False)
        """
        # Load environment variables
        load_dotenv()
        
        # Get the URL from environment variables
        self.base_url = os.getenv('URL')
        if not self.base_url:
            raise ValueError("URL not found in environment variables. Make sure .env file exists with URL key.")
        
        # Initialize playwright objects as None
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Browser configuration
        self.headless = headless
    
    def start_browser(self) -> None:
        """
        Start the browser session.
        """
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(viewport={"width": 1600, "height": 900})
        self.page = self.context.new_page()
    
    def navigate_to_site(self) -> None:
        """
        Navigate to the base URL from environment variables.
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        self.page.goto(self.base_url)
        # Wait for the page to load
        self.page.wait_for_load_state("networkidle")
        
        # Check if the page loaded correctly
        title = self.page.title()
        if "E-Status" not in title and "ARB" not in title and "Appeals" not in title:
            print(f"Warning: Page title '{title}' does not contain expected text. The page may not have loaded correctly.")
    
    def enter_roll_number(self, roll_number: str) -> None:
        """
        Enter a roll number into the website's multiple input fields.
        The roll number format is expected to be like: 12-34-456-789-12345-0000
        
        Args:
            roll_number (str): The roll number to enter, with or without dashes
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        # Remove any non-digit characters from the roll number
        digits_only = re.sub(r'\D', '', roll_number)
        
        # Check if we have the expected number of digits (19)
        if len(digits_only) != 19:
            print(f"Warning: Roll number '{roll_number}' does not have the expected 19 digits. Got {len(digits_only)} digits.")
            if len(digits_only) > 19:
                digits_only = digits_only[:19]  # Truncate if too long
            elif len(digits_only) < 19:
                # Pad with zeros if too short
                digits_only = digits_only.ljust(19, '0')
        
        try:
            # Wait for the first roll number field to be visible
            self.page.wait_for_selector('#MainContent_txtRollNo1', state='visible', timeout=10000)
            
            # Split the roll number into segments
            roll_no1 = digits_only[0:2]
            roll_no2 = digits_only[2:4]
            roll_no3 = digits_only[4:7]
            roll_no4 = digits_only[7:10]
            roll_no5 = digits_only[10:15]
            roll_no6 = digits_only[15:19]
            
            # Fill each field with its corresponding segment
            self.page.fill('#MainContent_txtRollNo1', roll_no1)
            self.page.fill('#MainContent_txtRollNo2', roll_no2)
            self.page.fill('#MainContent_txtRollNo3', roll_no3)
            self.page.fill('#MainContent_txtRollNo4', roll_no4)
            self.page.fill('#MainContent_txtRollNo5', roll_no5)
            self.page.fill('#MainContent_txtRollNo6', roll_no6)
            
            print(f"Successfully entered roll number: {roll_number}")
        except Exception as e:
            print(f"Error entering roll number: {e}")
    
    def submit_search(self) -> bool:
        """
        Submit the roll number search form.
        
        Returns:
            bool: True if the search was successful, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        try:
            # Wait for the submit button and click it
            self.page.wait_for_selector('#MainContent_btnSubmit', state='visible', timeout=10000)
            self.page.click('#MainContent_btnSubmit')
            print("Successfully submitted search")
            
            # Wait for results to load
            self.page.wait_for_load_state("networkidle")
            
            # Check if there's an error message (e.g., invalid roll number format)
            error_dialog = self.page.locator('div.alert-danger, .alert-warning')
            if error_dialog.count() > 0:
                error_text = error_dialog.first.text_content()
                print(f"Warning: Received error message: {error_text}")
                return False
            
            return True
        except Exception as e:
            print(f"Error submitting search: {e}")
            return False
    
    def save_html_content(self, file_path: str) -> None:
        """
        Save the current page's HTML content to a file.
        
        Args:
            file_path (str): The path where to save the HTML content
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        try:
            # Get the HTML content of the page
            html_content = self.page.content()
            
            # Save the HTML content to the specified file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"HTML content saved to {file_path}")
        except Exception as e:
            print(f"Error saving HTML content: {e}")
    
    def extract_data_to_json(self, roll_number: str) -> Dict[str, Any]:
        """
        Extract data from the current page and return it as a dictionary.
        This method extracts relevant information from the ARB website's response page.
        
        Args:
            roll_number (str): The roll number that was searched
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted data
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        data = {
            "roll_number": roll_number,
            "extracted_timestamp": datetime.datetime.now().isoformat(),
            "page_title": self.page.title(),
            "property_info": {},
            "appeal_info": [],
            "raw_tables": []
        }
        
        try:
            # Check if we're on the E-Services - Appeals page
            title = self.page.title()
            is_appeals_page = "Appeals" in title
            
            # Extract roll number from the page (to confirm it matches input)
            roll_number_displayed = self.page.locator('div.col-md-3:has-text("Roll Number:") + div.col-md-3').first
            if roll_number_displayed and roll_number_displayed.count() > 0:
                data["roll_number_displayed"] = roll_number_displayed.text_content().strip()
            
            # Extract property information from the Appeals page
            if is_appeals_page:
                # Try to get the Location & Property Description
                property_desc = self.page.locator('div.col-md-3:has-text("Location & Property Description:") + div.col-md-3').first
                if property_desc and property_desc.count() > 0:
                    data["property_info"]["description"] = property_desc.text_content().strip()
            else:
                # For non-Appeals pages, try the original selectors
                property_address = self.page.locator('td:has-text("Property Address:") + td').first
                property_municipality = self.page.locator('td:has-text("Municipality:") + td').first
                
                if property_address and property_address.count() > 0:
                    data["property_info"]["address"] = property_address.text_content().strip()
                
                if property_municipality and property_municipality.count() > 0:
                    data["property_info"]["municipality"] = property_municipality.text_content().strip()
            
            # Extract table data
            tables = self.page.locator('table.table').all()
            for i, table in enumerate(tables):
                table_data = []
                rows = table.locator('tr').all()
                
                for row in rows:
                    cells = row.locator('td, th').all()
                    row_data = [cell.text_content().strip() for cell in cells]
                    if row_data:  # Only add non-empty rows
                        table_data.append(row_data)
                
                if table_data:  # Only add non-empty tables
                    data["raw_tables"].append(table_data)
                    
                    # For Appeals page, the table structure is different
                    if is_appeals_page and i == 0 and len(table_data) > 1:
                        # Check for the appeals table with columns like AppealNo, Appellant, etc.
                        headers = table_data[0]
                        if "AppealNo" in headers[0] or "Appeal" in headers[0]:
                            for row_idx in range(1, len(table_data)):
                                appeal = {}
                                for col_idx, header in enumerate(headers):
                                    if col_idx < len(table_data[row_idx]):
                                        # Clean up header names for consistent keys
                                        clean_header = header.replace("No", "Number").replace(" ", "_").lower()
                                        appeal[clean_header] = table_data[row_idx][col_idx]
                                data["appeal_info"].append(appeal)
                    # For non-Appeals pages, use the original logic
                    elif not is_appeals_page and i == 0 and len(table_data) > 1 and "Appeal Number" in table_data[0]:
                        headers = table_data[0]
                        for row_idx in range(1, len(table_data)):
                            appeal = {}
                            for col_idx, header in enumerate(headers):
                                if col_idx < len(table_data[row_idx]):
                                    appeal[header] = table_data[row_idx][col_idx]
                            data["appeal_info"].append(appeal)
            
            return data
        
        except Exception as e:
            print(f"Error extracting data to JSON: {e}")
            # Return basic data even if extraction failed
            return data
    
    def save_json_data(self, data: Dict[str, Any], file_path: str) -> None:
        """
        Save the extracted data to a JSON file.
        
        Args:
            data (Dict[str, Any]): The data to save
            file_path (str): The path where to save the JSON data
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"JSON data saved to {file_path}")
        except Exception as e:
            print(f"Error saving JSON data: {e}")
    
    def process_roll_numbers(self, roll_numbers: List[str], output_dir: str, save_screenshots: bool = False, save_html: bool = False) -> None:
        """
        Process a list of roll numbers one by one, saving HTML and JSON data for each.
        All roll numbers are processed automatically without requiring confirmation.
        For each roll number, captures all appeals and their details before moving to the next.
        
        Args:
            roll_numbers (List[str]): A list of roll numbers to process
            output_dir (str): The directory where to save the output files
            save_screenshots (bool, optional): Whether to save screenshots. Defaults to False.
            save_html (bool, optional): Whether to save HTML content. Defaults to False.
        """
        total_roll_numbers = len(roll_numbers)
        
        for index, roll_number in enumerate(roll_numbers, 1):
            print(f"\nProcessing roll number {index}/{total_roll_numbers}: {roll_number}")
            
            try:
                # Navigate back to the main page before processing each roll number
                if index > 1:  # Don't need to do this for the first roll number
                    self.navigate_to_site()
                    time.sleep(2)  # Give time for the page to fully load
                
                self.enter_roll_number(roll_number)
                success = self.submit_search()
                
                if success:
                    # Create a directory for this roll number if it doesn't exist
                    roll_dir = os.path.join(output_dir, roll_number.replace('-', '_'))
                    os.makedirs(roll_dir, exist_ok=True)
                    
                    # Check if we're on an Appeals page
                    is_appeals_page = "Appeals" in self.page.title()
                    
                    # Take a screenshot if enabled
                    if save_screenshots:
                        screenshot_path = os.path.join(roll_dir, "screenshot.png")
                        self.take_screenshot(screenshot_path)
                    
                    # Save HTML content if enabled
                    if save_html:
                        html_filename = "appeals.html" if is_appeals_page else "page.html"
                        html_path = os.path.join(roll_dir, html_filename)
                        self.save_html_content(html_path)
                    
                    # Extract and save JSON data (always save this)
                    json_data = self.extract_data_to_json(roll_number)
                    json_filename = "appeals_data.json" if is_appeals_page else "data.json"
                    json_path = os.path.join(roll_dir, json_filename)
                    self.save_json_data(json_data, json_path)
                    
                    print(f"Data for roll number {roll_number} saved to {roll_dir}/")
                    
                    # Additional processing for the Appeals page - capture ALL appeals
                    if is_appeals_page:
                        # Check if there are appeal links to follow
                        appeal_links = self.page.locator('table.table a[href^="ComplaintDetail.aspx"]').all()
                        
                        if appeal_links:
                            appeals_detail_dir = os.path.join(roll_dir, "appeal_details")
                            os.makedirs(appeals_detail_dir, exist_ok=True)
                            
                            # Process ALL appeals instead of limiting to the first few
                            total_appeals = len(appeal_links)
                            print(f"Found {total_appeals} appeal links, processing all of them")
                            
                            # Create a list to store appeal data
                            appeal_details = []
                            
                            for i in range(total_appeals):
                                try:
                                    # Get the appeal number from the link text
                                    appeal_number = appeal_links[i].text_content().strip()
                                    print(f"Processing appeal {appeal_number} ({i+1}/{total_appeals})")
                                    
                                    # Click the link (will navigate away from the main appeals page)
                                    appeal_links[i].click()
                                    
                                    # Wait for the page to load
                                    self.page.wait_for_load_state("networkidle")
                                    
                                    # Save the detail page screenshot if enabled
                                    if save_screenshots:
                                        detail_screenshot_path = os.path.join(appeals_detail_dir, f"appeal_{appeal_number}.png")
                                        self.take_screenshot(detail_screenshot_path)
                                    
                                    # Save the detail page HTML if enabled
                                    if save_html:
                                        detail_html_path = os.path.join(appeals_detail_dir, f"appeal_{appeal_number}.html")
                                        self.save_html_content(detail_html_path)
                                    
                                    # Extract appeal detail data
                                    appeal_data = self.extract_appeal_detail_data(appeal_number)
                                    appeal_details.append(appeal_data)
                                    
                                    # Save individual appeal JSON data (always save this)
                                    detail_json_path = os.path.join(appeals_detail_dir, f"appeal_{appeal_number}.json")
                                    self.save_json_data(appeal_data, detail_json_path)
                                    
                                    # Navigate back to the main appeals page
                                    self.page.go_back()
                                    self.page.wait_for_load_state("networkidle")
                                    
                                    # Need to refresh the appeal links after navigating back
                                    appeal_links = self.page.locator('table.table a[href^="ComplaintDetail.aspx"]').all()
                                except Exception as e:
                                    print(f"Error processing appeal detail: {e}")
                                    # Try to navigate back to the main appeals page if there was an error
                                    try:
                                        self.page.go_back()
                                        self.page.wait_for_load_state("networkidle")
                                        # Refresh appeal links
                                        appeal_links = self.page.locator('table.table a[href^="ComplaintDetail.aspx"]').all()
                                    except Exception as nav_error:
                                        print(f"Error navigating back: {nav_error}")
                                        # If we can't go back, try to navigate to the site again
                                        try:
                                            self.navigate_to_site()
                                            # We need to re-enter the roll number to get back to where we were
                                            self.enter_roll_number(roll_number)
                                            self.submit_search()
                                            # Refresh appeal links
                                            appeal_links = self.page.locator('table.table a[href^="ComplaintDetail.aspx"]').all()
                                        except Exception as site_error:
                                            print(f"Error returning to site: {site_error}")
                                            # If all navigation fails, break out of the loop and move to the next roll number
                                            break
                            
                            # Save all appeal details in a combined JSON file (always save this)
                            all_appeals_json_path = os.path.join(roll_dir, "all_appeal_details.json")
                            self.save_json_data({"roll_number": roll_number, "appeals": appeal_details}, all_appeals_json_path)
                else:
                    print(f"Failed to process roll number: {roll_number}")
            
            except Exception as e:
                print(f"Error processing roll number {roll_number}: {e}")
                print("Continuing with next roll number...")
                
            # Add a small delay between roll numbers to avoid overwhelming the server
            time.sleep(2)
    
    def take_screenshot(self, file_path: str) -> None:
        """
        Take a screenshot of the current page state.
        
        Args:
            file_path (str): The path where to save the screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        try:
            self.page.screenshot(path=file_path)
            print(f"Screenshot saved to {file_path}")
        except Exception as e:
            print(f"Error taking screenshot: {e}")
    
    def close(self) -> None:
        """
        Close the browser and end the Playwright session.
        """
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
            
        # Reset attributes
        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

    def extract_appeal_detail_data(self, appeal_number: str) -> Dict[str, Any]:
        """
        Extract detailed information from an appeal detail page.
        
        Args:
            appeal_number (str): The appeal number being processed
            
        Returns:
            Dict[str, Any]: A dictionary containing the extracted appeal detail data
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")
        
        data = {
            "appeal_number": appeal_number,
            "extracted_timestamp": datetime.datetime.now().isoformat(),
            "property_info": {},
            "appellant_info": {},
            "status_info": {},
            "decision_info": {}
        }
        
        try:
            # Extract property information
            property_roll = self.page.locator('div.col-md-4:has-text("Property Roll Number:") + div.col-md-4').first
            if property_roll and property_roll.count() > 0:
                data["property_info"]["roll_number"] = property_roll.text_content().strip()
            
            location = self.page.locator('div.col-md-4:has-text("Location & Property Description:") + div.col-md-4').first
            if location and location.count() > 0:
                data["property_info"]["description"] = location.text_content().strip()
            
            municipality = self.page.locator('div.col-md-4:has-text("Municipality:") + div.col-md-4').first
            if municipality and municipality.count() > 0:
                data["property_info"]["municipality"] = municipality.text_content().strip()
            
            classification = self.page.locator('div.col-md-4:has-text("Property Classification:") + div.col-md-4').first
            if classification and classification.count() > 0:
                data["property_info"]["classification"] = classification.text_content().strip()
            
            nbhd = self.page.locator('div.col-md-4:has-text("NBHD:") + div.col-md-4').first
            if nbhd and nbhd.count() > 0:
                data["property_info"]["nbhd"] = nbhd.text_content().strip()
            
            # Extract appellant information
            name1 = self.page.locator('div.col-md-4:has-text("Name1:") + div.col-md-4').first
            if name1 and name1.count() > 0:
                data["appellant_info"]["name1"] = name1.text_content().strip()
            
            name2 = self.page.locator('div.col-md-4:has-text("Name2:") + div.col-md-4').first
            if name2 and name2.count() > 0:
                data["appellant_info"]["name2"] = name2.text_content().strip()
            
            representative = self.page.locator('div.col-md-4:has-text("Name of Representative:") + div.col-md-4').first
            if representative and representative.count() > 0:
                data["appellant_info"]["representative"] = representative.text_content().strip()
            
            filing_date = self.page.locator('div.col-md-4:has-text("Filing Date:") + div.col-md-4').first
            if filing_date and filing_date.count() > 0:
                data["appellant_info"]["filing_date"] = filing_date.text_content().strip()
            
            tax_date = self.page.locator('div.col-md-4:has-text("Tax Date:") + div.col-md-4').first
            if tax_date and tax_date.count() > 0:
                data["appellant_info"]["tax_date"] = tax_date.text_content().strip()
            
            section = self.page.locator('div.col-md-4:has-text("Section:") + div.col-md-4').first
            if section and section.count() > 0:
                data["appellant_info"]["section"] = section.text_content().strip()
            
            reason = self.page.locator('div.col-md-4:has-text("Reason for Appeal:") + div.col-md-4').first
            if reason and reason.count() > 0:
                data["appellant_info"]["reason_for_appeal"] = reason.text_content().strip()
            
            # Extract status information
            status = self.page.locator('div.col-md-4:has-text("Status:") + div.col-md-4').first
            if status and status.count() > 0:
                data["status_info"]["status"] = status.text_content().strip()
            
            # Extract decision information if available
            decision_number = self.page.locator('div.col-md-4:has-text("Decision Number:") + div.col-md-4').first
            if decision_number and decision_number.count() > 0:
                data["decision_info"]["decision_number"] = decision_number.text_content().strip()
            
            mailing_date = self.page.locator('div.col-md-4:has-text("Decision Mailing Date:") + div.col-md-4').first
            if mailing_date and mailing_date.count() > 0:
                data["decision_info"]["mailing_date"] = mailing_date.text_content().strip()
            
            decisions = self.page.locator('div.col-md-4:has-text("Decision(s):") + div.col-md-4').first
            if decisions and decisions.count() > 0:
                data["decision_info"]["decisions"] = decisions.text_content().strip()
            
            return data
        
        except Exception as e:
            print(f"Error extracting appeal detail data: {e}")
            # Return basic data even if extraction failed
            return data