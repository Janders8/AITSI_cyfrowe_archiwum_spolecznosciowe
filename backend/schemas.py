"""
Plik odpowiedzialny za walidację danych przychodzących oraz mapowanie danych wychodzących z API.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# schematy zdjęcia

# Informacje o zdjęciu. Szablon z którego korzystają inne schematy.
class MaterialBase(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    historical_period: Optional[str] = None

# Schemat do edycji zdjęcia.
class MaterialUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    historical_period: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

# Filtr sprawdzający dane z formularza "Dodaj Zdjęcie" wypełnianego przez Twórcę.
class MaterialCreate(MaterialBase):
    pass

# Krótki słownik na dane publiczne twórcy
class UserBasicInfo(BaseModel):
    id: int
    name: str
    email: str
    is_blocked: bool
    
    class Config:
        from_attributes = True

# To co serwer zwraca użytkownikowi przeglądającemu stronę.
# Dodaje serwerowe ID i datę i dane autora.
class Material(MaterialBase):
    id: int
    filename: str
    upload_date: datetime
    owner_id: int
    # Dane autora
    owner: UserBasicInfo 

    # Pozwala Pydanticowi pobierać dane bezpośrednio z rekordów bazy danych
    class Config:
        from_attributes = True 



# schematy użytkownika i autoryzacji

# Schemat oczekujący na token od Google po zalogowaiu się przez konto google
class GoogleToken(BaseModel):
    credential: str

# Zwracany przez API token wewnętrzny
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# Podstawowe informacje o człowieku. Szablon z którego korzystają inne klasy.
class UserBase(BaseModel):
    email: str
    name: str

# Filtr sprawdzający dane podczas pierwszej rejestracji przez powiązanie z kontem Google.
class UserCreate(UserBase):
    google_id: str

# Pełne dane o użytkowniku po pobraniu ich z Bazy Danych i odesłaniu stronom.
class User(UserBase):
    id: int
    role: str
    is_blocked: bool
    materials: List[Material] = []

    class Config:
        from_attributes = True
