# 104 Webcrawler Job Finder

## Project Overview
This project is a web crawler designed to extract job posting information from the 104 job search platform. It integrates intelligent job categorization and search suggestions to provide job recommendations tailored to the user's preferences.

## Key Features
- Filters and matches job postings based on user-specified search criteria.
- Extracts essential job information such as job title, company name, job link, salary, and work location.
- Uses predefined category and prompt data for intelligent matching and recommendations.

## Project Structure
- `src/prompts/`: Contains search prompts and various option dictionaries (e.g., area, education, job experience).
- `src/json/`: Holds necessary JSON data, including proxy server details and job category mappings.
- `src/`: Contains core modules such as the JobFinder module, which handles the search and matching logic.
- `main.py`: The main entry point of the project that processes user queries and outputs search results.

## Usage Instructions
1. Install dependencies via `pip install -r requirements.txt`
2. Update the `api_key` in `main.py` with a valid key.
3. Modify the `user_prompt` to match your job search preferences..
4. Execute `main.py` to retrieve the job postings that meet your criteria.

## Dependencies
- Python 3.x  
- openai api
## Configuration Details
- The files in `src/prompts/` define options for regions, education levels, work experience, etc.
- The JSON files in `src/json/` provide proxy server details and job category mappings to ensure proper network requests and accurate data matching.


