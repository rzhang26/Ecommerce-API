from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.users.models import User, UserBase, UserCreate, UserResponse
from app.users.security import hash_password, verify_password, create_access_token
from app.users.dependencies import get_current_user
from app.database import get_session, SessionDep

router = APIRouter(prefix='/users', tags=['Users/Authentication'])

@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_account(user_in: UserCreate, session: Session = Depends(get_session)):
    plain_password = user_in.password
    hashed_password = hash_password(plain_password)

    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password
    )

    try:
        session.add(db_user)
        session.commit()
    except IntegrityError:
        session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
         
    session.refresh(db_user)
    return db_user

# @router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_user_account(user_in: UserCreate, session: Session = SessionDep):
#     user = session.exec(select(User.email == user_in.email)).first()
#     if user:
#         raise HTTPException(
#             status_code=status.HTTP_302_FOUND,
#             detail=f'A user with email {user_in.email} already exists.'
#         )

#     plain_password = user_in.password
#     hashed_password = hash_password(plain_password)

#     db_user = User(
#         email=user_in.email,
#         hashed_password=hashed_password
#     )
#     session.add(db_user)
#     session.commit()
#     session.refresh(db_user)

#     return db_user

@router.post('/login')
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)) -> str:
    current_user = session.exec(select(User).where(User.email == form_data.username))
    if not current_user or not verify_password(form_data.password, current_user.hashed_password): # form_data password auto-hashed
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'Incorrect email or password.'
            )

    access_token = create_access_token(data={'sub': str(current_user.id)})

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }

@router.get('/me', response_model=UserResponse)
def read_current_user_profile(user: User = Depends(get_current_user)):

    return user