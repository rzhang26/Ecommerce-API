from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.database import get_session, SessionDep
from app.users.models import User, UserCreate, UserResponse
from app.users.security import hash_password, verify_password, create_access_token
from app.users.dependencies import get_current_user

router = APIRouter(prefix='/users', tags=['Users/Authentication'])

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_acct(user_in: UserCreate, session: Session = Depends(get_session)): #SessionDep why not?
    hashed = hash_password(user_in.password)
    
    db_user = User(
        email=user_in.email,
        hashed_password=hashed
    )
    
    session.add(db_user)
    session.commit()  # <-- CRITICAL for test framework persistence!
    session.refresh(db_user)
    return db_user

@router.post('/login')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    
    access_token = create_access_token(data={'sub': str(user.id)})

    return {
        'access_token': access_token,
        'token_type': 'bearer'
        }

@router.get('/me', response_model=UserResponse)
def read_curr_user_profile(current_user: User = Depends(get_current_user)):

    return current_user