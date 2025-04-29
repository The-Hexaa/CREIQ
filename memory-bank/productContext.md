# Product Context: CREIQ

## Problem Statement
Real estate professionals, researchers, and analysts often need to gather property information from governmental assessment websites. This process is typically manual, time-consuming, and error-prone when dealing with large numbers of properties. CREIQ addresses this by automating the retrieval and organization of property data from the Assessment Review Board (ARB) in Ontario, Canada.

## User Needs
Users of this system need to:
- Process multiple property roll numbers efficiently
- Generate valid URLs for these properties
- Retrieve property assessment details automatically
- Extract meaningful data from complex HTML responses
- Store and analyze the extracted data
- Track property assessment appeals over time

## Solution Overview
CREIQ provides an end-to-end solution that:
1. Takes a CSV file containing property roll numbers as input
2. Generates URLs for each property by combining roll numbers with a base URL
3. Fetches content from these URLs using robust retry mechanisms
4. Parses the HTML responses to extract structured data
5. Stores this data in a database for analysis and tracking

## User Experience Goals
- **Simplicity**: Provide a straightforward command-line interface for basic operations
- **Flexibility**: Enable programmatic usage for integration into other systems
- **Reliability**: Implement robust error handling to manage network issues
- **Efficiency**: Minimize manual effort in property data collection
- **Visibility**: Offer clear feedback on process status and results

## Stakeholders
- Real estate professionals
- Property assessment analysts
- Government data researchers
- Property tax consultants
- Property owners with multiple properties

## Business Value
CREIQ delivers value by:
- Reducing manual data entry and lookup time
- Enabling bulk processing of property information
- Providing a structured database of property assessment data
- Allowing for tracking of assessment appeals over time
- Supporting data-driven decision making for property investments and appeals

## Constraints
- Must adhere to the terms of use of source websites
- Needs to handle rate limiting and session management
- Should respect the privacy of property data
- Must adapt to changes in source website structure