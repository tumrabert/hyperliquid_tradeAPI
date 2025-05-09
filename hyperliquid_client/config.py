import os
import json
from dotenv import load_dotenv

def load_config():
    """
    Load configuration from .env file
    """
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    
    # Check if .env exists
    if not os.path.exists(env_path):
        print(".env file not found, please create one with the required configuration.")
        return {
            "secret_key": "",
            "account_address": "0x0000000000000000000000000000000000000000",
            "multi_sig": {
                "authorized_users": []
            }
        }
    
    # Load the .env file
    load_dotenv(env_path)
    
    # Extract multi-sig users from JSON format
    multi_sig_users = []
    try:
        if os.getenv("HL_MULTI_SIG_USERS"):
            multi_sig_data = json.loads(os.getenv("HL_MULTI_SIG_USERS", "[]"))
            if isinstance(multi_sig_data, list):
                multi_sig_users = multi_sig_data
            else:
                multi_sig_users = [multi_sig_data]
    except json.JSONDecodeError:
        print("Warning: Could not parse HL_MULTI_SIG_USERS as JSON.")
    
    # Create config dictionary from environment variables with HL_ prefix
    config = {
        "secret_key": os.getenv("HL_SECRET_KEY", ""),
        "account_address": os.getenv("HL_ACCOUNT_ADDRESS", "0x0000000000000000000000000000000000000000"),
        "multi_sig": {
            "authorized_users": multi_sig_users
        }
    }
    
    return config
