from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "27d44dd82043e91b9552929568b877e1609793866988057456b57ed99165ad9a14eb0988fd0e3ce58353f0726c3331a1b52c8ea6bafa50d68b31604694a23d5aa95e5eb9b020275466ade906b793db9b356eca03f6873f9276723b74769e34de7913507b51e2cdff41b2dc6fbac462de94c948003109cdf7abc8189506d5fe641877445125a023f0344421250bb30887a58d9a7763e73f5d57746274fd6f6269a1f39ac6451c85326d152bb9c4ae3db6ab5313e267536736cb3fb81783d0cd9100fb7f801d9984d1daa813bbcab4ecf39a70afcb2c7e9c7afa667d3b518a51c6d13d2235a30da4f5552fa7157083e03d9fefd001a56b23e4c8fdf6db8119681a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
