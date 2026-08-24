import hmac
import hashlib
import json
from urllib.parse import parse_qsl
from datetime import datetime, timedelta, timezone
import jwt
from src.core.config import SECRET_KEY, ALGORITHM

def verify_telegram_web_app_data(init_data: str, bot_token: str) -> dict | None:
    """
    Validates the `initData` from the Telegram Mini App.
    Returns a dictionary containing the user's data if validation is successful; otherwise, returns `None`.
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
        
        telegram_hash = parsed_data.pop('hash', None)
        if not telegram_hash:
            return None

        sorted_items = sorted(parsed_data.items(), key=lambda x: x[0])
        data_check_string = "\n".join([f"{k}={v}" for k, v in sorted_items])

        secret_key = hmac.new(
            key=b"WebAppData", 
            msg=bot_token.encode('utf-8'), 
            digestmod=hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            key=secret_key, 
            msg=data_check_string.encode('utf-8'), 
            digestmod=hashlib.sha256
        ).hexdigest()

        if calculated_hash != telegram_hash:
            return None
            
        auth_date = int(parsed_data.get('auth_date', 0))
        current_time = int(datetime.now(timezone.utc).timestamp())
        if current_time - auth_date > 86400:
            return None

        user_data = json.loads(parsed_data.get('user', '{}'))
        return user_data

    except Exception:
        return None

def verify_widget_hash(data: dict, bot_token: str) -> bool:
    received_hash = data.pop("hash")
    check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    return calculated_hash == received_hash

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Generate JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt