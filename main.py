import os
import sys
import json
import logging
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
dotenv_path = Path(__file__).parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded .env file from: {dotenv_path}")
else:
    print(f"Warning: .env file not found at {dotenv_path}")
    # Try to find .env file in parent directories
    dotenv_path = find_dotenv()
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Loaded .env file from: {dotenv_path}")
    else:
        print("Warning: No .env file found in any parent directory")

# Configure logging
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to capture all log levels
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Log to console
        logging.FileHandler('cron.log', mode='w')  # Overwrite log file each run
    ]
)
logger = logging.getLogger(__name__)
logger.info("Script started")

# Debug: Print all environment variables
logger.debug("Environment variables:")
for key, value in os.environ.items():
    if 'KEY' in key or 'TOKEN' in key or 'SECRET' in key or 'PASSWORD' in key:
        logger.debug(f"{key} = [REDACTED]")
    else:
        logger.debug(f"{key} = {value}")

def create_notion_page():
    # Load environment variables with detailed logging
    logger.info("Loading environment variables...")
    
    # Get and log all relevant environment variables
    env_vars = {
        'LANGLFOW_API_URL': os.getenv('LANGLFOW_API_URL'),
        'LANGFLOW_API_KEY': '[REDACTED]' if os.getenv('LANGFLOW_API_KEY') else None,
        'NOTION_DATABASE_ID': os.getenv('NOTION_DATABASE_ID')
    }
    
    logger.info(f"Environment variables: { {k: v if k != 'LANGFLOW_API_KEY' else '[REDACTED]' for k, v in env_vars.items()}}")
    
    # Check for missing required variables
    missing_vars = [var for var, value in env_vars.items() if not value and var != 'LANGFLOW_API_KEY']
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please ensure your .env file is in the correct location and contains these variables.")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Files in current directory: {os.listdir('.')}")
        return None
    
    url = env_vars['LANGLFOW_API_URL']
    database_id = env_vars['NOTION_DATABASE_ID']
    api_key = os.getenv('LANGFLOW_API_KEY')
    
    # Create a session with retry logic
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],  # status codes to retry on
        allowed_methods=["POST"]  # only retry on POST requests
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {"title": [{"text": {"content": "Harnessing Quiet Tech: Open-Source, Subtle AI, and Viral Reach"}}]},
            "Slug": {"rich_text": [{"text": {"content": "harnessing-quiet-tech-open-source-subtle-ai-and-viral-reach"}}]},
            "Short Description": {"rich_text": [{"text": {"content": "Explore how businesses can leverage open-source tools and understated AI startups."}}]},
            "Category": {"select": {"name": "Keyword Research"}},
            "Tags": {"multi_select": []},
            "Publication Date": {"date": {"start": "2025-06-07T20:00:00Z"}},
            "Status": {"select": {"name": "Draft"}},
            "Full Description": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": "<h1>Harnessing Quiet Tech</h1><p>Full post content here...</p>"}
                }]
            }
        },
        "cover": {"external": {"url": "https://yourcdn.com/path-to-image.jpg"}}
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    try:
        logger.info(f"Sending request to Notion API (timeout: 120s)...")
        logger.debug(f"URL: {url}")
        logger.debug(f"Headers: { {k: v if k != 'x-api-key' else '[REDACTED]' for k, v in headers.items()}}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        # First, try with a HEAD request to check if the endpoint is reachable
        try:
            logger.info("Checking if endpoint is reachable...")
            head_response = session.head(
                url,
                headers=headers,
                timeout=10
            )
            logger.info(f"Endpoint is reachable. Status code: {head_response.status_code}")
        except Exception as e:
            logger.warning(f"HEAD request failed: {e}. Continuing with POST request...")
        
        # Make the actual POST request with a longer timeout
        response = session.post(
            url,
            headers=headers,
            json=payload,
            timeout=120  # 120 seconds timeout
        )
        
        logger.info(f"Received response with status code: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            logger.debug(f"Response JSON: {json.dumps(response_data, indent=2)}")
        except ValueError:
            logger.debug(f"Response text (not JSON): {response.text[:500]}...")  # Log first 500 chars if not JSON
            
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        logger.info("Successfully created Notion page")
        return response_data if 'response_data' in locals() else response.text
        
    except requests.exceptions.Timeout:
        logger.error("Request timed out after 120 seconds. The server took too long to respond.")
        logger.info("This could be due to the server being under heavy load or network issues.")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response status: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
    return None

if __name__ == "__main__":
    logger.info("Starting Notion page creation job")
    result = create_notion_page()
    if result:
        logger.info("Job completed successfully")
    else:
        logger.error("Job failed")
        sys.exit(1)
