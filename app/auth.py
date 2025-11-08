from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
from pathlib import Path

# Get absolute path of keys file from this script
script_path = Path(__file__).resolve()
keys_file = script_path.parent.parent / "user_keys.csv"

# Define keyheader type
api_key_header = APIKeyHeader(name="X-API-Key")


def get_user(api_key_header: str = Security(api_key_header)):
    try:
        user = get_user_from_api_key(api_key_header)
        return user
    except Exception as e:
        raise e


def check_api_key(api_key: str, key_file=keys_file):
    try:
        keys = pd.read_csv(key_file)
        return api_key in keys["api_key"].values
    except:
        raise FileNotFoundError(f"API Key file not found: {key_file}")


def get_user_from_api_key(api_key: str, key_file=keys_file):
    try:
        keys = pd.read_csv(key_file)
        if check_api_key(api_key):
            return keys[keys["api_key"] == api_key].iloc[0]["user"]
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid API key",
            )
    except HTTPException as e:
        raise e
    except:
        raise FileNotFoundError(f"API Key file not found: {key_file}")
