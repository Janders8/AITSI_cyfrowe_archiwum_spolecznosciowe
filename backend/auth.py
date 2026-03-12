"""
Ten moduł obsługuje wszystko co związane z logowaniem przez Google.
Generuje i odczytuje tokeny JWT.
"""

import os
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# Sekretny klucz szyfrowania uzyskany z pliku .env
SECRET_KEY = os.getenv("SECRET_KEY")

# Wybrany algorytm kodowania
ALGORITHM = "HS256"

# Czas (w minutach) jaki jest ważny token
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Do szybkiego wyszukiwania tokenu w zapytaniach http
security = HTTPBearer()

def create_access_token(data: dict):
    """
    Funkcja przyjmuje słownik, dodaje do niego datę ważności
    i zabezpiecza kodem, zwracając token do użytku wewnątrz serwisu.
    """
    to_encode = data.copy()
    
    # Ustawienie czasu wygaśnięcia tokenu
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Haszowanie i zabezpieczanie z kluczem
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Funkcja weryfikuje token.
    """
    token = credentials.credentials
    try:
        # Deszyfracja tokenu
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Nieprawidłowy token uwierzytelniający.")
        return email
        
    # Gdy przekroczono czas połączenia
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sesja wygasła. Zaloguj się ponownie.")
        
    # Gdy token jest nieprawidłowy
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token uwierzytelniający jest nieprawidłowy.")
