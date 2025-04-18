"""DOC.

docs.
"""

import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import psycopg2
# from typing import Optional

frontend_host = os.getenv("FRONTEND_HOST")
frontend_port = os.getenv("FRONTEND_PORT")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://frontend:5000",
                   "http://frontend:5000/auth/login"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

test_hash = "$2b$12$pyeuCHMyobtbym6epMs2WeWiOi3ULbt0Yz6EjoE/4AfVA6jC8EyqC"
print(pwd_context.verify("password123", test_hash))

print(os.getenv("AUTHDB_USER"))
print(os.getenv("AUTHDB_PASSWORD"))


# Secret key (use env vars in real app)
SECRET_KEY = os.getenv("JWT_SECRET_KEY","captboxslammer")
ALGORITHM = os.getenv("JWT_ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES","60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: EmailStr
    password_hash: str
    fullname: str
    email: EmailStr


class RegisterUser(BaseModel):
    username: EmailStr
    fullname: str
    password: str
    email: EmailStr


def get_authdb_conn():
    return psycopg2.connect(
        host=os.getenv("AUTHDB_HOST", "authdb"),
        database=os.getenv("AUTHDB_DB", "authdb"),
        user=os.getenv("AUTHDB_USER", "authuser"),
        password=os.getenv("AUTHDB_PASSWORD", "authpass")
    )


def get_user(username: str):
    conn = get_authdb_conn()
    cur = conn.cursor()
    cur.execute("SELECT username, password_hash, fullname, email " +
                "FROM users WHERE username = %s", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User(username=row[0],
                    password_hash=row[1],
                    fullname=row[2],
                    email=row[3])
    return None



def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


def authenticate_user(username, password):
    user = get_user(username)
    print(f"LOOKUP USER {user}")
    if not user:
        print("No user found")
    else:
        print("Verifying password ...")
        print(f"Stored hash: {user.password_hash}")
        print(f"Input password: {password}")
    if user and verify_password(password, user.password_hash):
        print("✅ Password matched!")
        return user
    print("❌ Password did not match.")
    return None


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def log_auth_attempt(user_id, action, success, details=""):
    conn = psycopg2.connect(
        host="db",
        database="authdb",
        user="your_user",
        password="your_password"
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO auth_logs (user_id, action, success, timestamp, details)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, action, success, datetime.now(), details))
    conn.commit()
    conn.close()


# Login route
@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# Dependency to protect routes
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token payload")
        user = get_user(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token")


# Protected route
@app.get("/auth/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Welcome, {current_user.fullname}"}


@app.post("/auth/register")
def register_user(user: RegisterUser):
    conn = get_authdb_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = %s", (user.username,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)

    cur.execute(
        "INSERT INTO users (username, fullname, password_hash, email) VALUES (%s, %s, %s, %s)",
        (user.username, user.fullname, hashed_password, user.email)
    )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "User registered successfully"}
