from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.database import get_session
from app.users.models import User
from app.config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='users/login')
ALGORITHM = 'HS256'

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        details='Could not validate credentials.',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    
    try:
        payload = jwt.decode(token, get_settings().JWT_SECRET_KEY, algorithm=ALGORITHM)
        user_id: str = payload.get('sub')
        if not user_id:
            raise credentials_exception
    # except jwt.PyJWTError:
    except JWTError:
        raise credentials_exception
    
    user = session.get(User, int(user_id))
    if not user:
        raise credentials_exception
    
    return user