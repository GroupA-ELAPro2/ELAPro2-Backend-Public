from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
import pandas as pd
from pathlib import Path

#Get absolute path of keys file from this script
script_path = Path(__file__).resolve()
keys_file = script_path.parent.parent/"user_keys.csv"

#Define keyheader type
api_key_header = APIKeyHeader(name="X-API-Key")

#Callable function to validate api key from keyheader
def get_user(api_key_header: str = Security(api_key_header)):
    if check_api_key(api_key_header):
        user = get_user_from_api_key(api_key_header)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key"
        )

#Function to validate if api_key exists
def check_api_key(api_key: str):
    keys = pd.read_csv(keys_file)
    return api_key in keys['api_key'].values

#Function to get user details from api_key file
def get_user_from_api_key(api_key: str):
    keys = pd.read_csv(keys_file)
    return keys[keys['api_key']==api_key].iloc[0]['user']
