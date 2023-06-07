from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from src.api.token_schema import TokenPayload

ALGORITHM: str = "HS256"
SECRET_KEY: str = "0eb6cf90ff9953fcb9db7f355e012c2253c6b4c6ba8d991abb78744f8b21829e"
EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 24
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token):
    try:
        print("decoding token {} with secret key {} {}".format(token, SECRET_KEY, ALGORITHM))
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        print("token_data {}".format(token_data))
    except jwt.ExpiredSignatureError as e:
        print('Error : decode_token() ExpiredSignatureError {}'.format(e))
    except jwt.JWTError as e:
        # raise HTTPException(
        #     status_code=status.HTTP_403_FORBIDDEN,
        #     detail="Could not validate credentials",
        # )
        print('Error : decode_token() PyJWTError {}'.format(e))
    except Exception as e:
        print('Error : decode_token() - {}'.format(e))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
