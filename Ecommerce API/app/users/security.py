from datetime import datetime, timedelta
from typing import Any, Optional
from jose import jwt
import bcrypt
from zoneinfo import ZoneInfo

from app.config import get_settings

EASTERN_TZ = ZoneInfo('America/New_York')
ALGORITHM = 'HS256'

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_bytes, hashed_bytes) #interesting how not direct comparison

#figure out how to consume this function's output
def create_access_token(data: dict[str, Any], expire_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expire_delta:
        expire = datetime.now(EASTERN_TZ) + expire_delta
    else: 
        expire = datetime.now(EASTERN_TZ) + timedelta(minutes=get_settings().ACCESS_TOKEN_EXPIRE_MIN)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().JWT_SECRET_KEY, algorithms=[ALGORITHM])

    return encoded_jwt