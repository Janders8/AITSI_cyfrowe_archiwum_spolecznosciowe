"""
Plik odpowiedzialny za walidację danych przychodzących oraz mapowanie danych wychodzących z API.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# schematy zdjęcia

class MaterialBase(BaseModel):
    """Zbiór podstawowych informacji o zdjęciu. Szablon z którego korzystają inne schematy."""
    title: str
    category: str
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    historical_period: Optional[str] = None

class MaterialUpdate(BaseModel):
    """Schemat do edycji zdjęcia."""
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    historical_period: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None

class MaterialCreate(MaterialBase):
    """Filtr sprawdzający dane z formularza "Dodaj Zdjęcie" wypełnianego przez Twórcę."""
    pass

class UserBasicInfo(BaseModel):
    """Krótki słownik na dane publiczne twórcy"""
    id: int
    name: str
    email: str
    is_blocked: bool
    
    class Config:
        from_attributes = True

class Material(MaterialBase):
    """To co serwer zwraca użytkownikowi przeglądającemu stronę.
    Dodaje serwerowe ID i datę i dane autora."""
    id: int
    filename: str
    upload_date: datetime
    owner_id: int
    # Dane autora
    owner: UserBasicInfo 

    # To pozwala czytać z obiektów bazy, a nie tylko ze słowników
    class Config:
        from_attributes = True 



# schematy użytkownika i autoryzacji

class GoogleToken(BaseModel):
    """Schemat oczekujący na token od Google po zalogowaiu się przez konto google"""
    credential: str

class TokenResponse(BaseModel):
    """Zwracany przez API token wewnętrzny"""
    access_token: str
    token_type: str


class UserBase(BaseModel):
    """Podstawowe informacje o człowieku. Szablon z którego korzystają inne klasy."""
    email: str
    name: str

class UserCreate(UserBase):
    """Filtr sprawdzający dane podczas pierwszej rejestracji przez powiązanie z kontem Google."""
    google_id: str

class User(UserBase):
    """Pełne dane o użytkowniku po pobraniu ich z Bazy Danych i odesłaniu stronom."""
    id: int
    role: str
    is_blocked: bool
    materials: List[Material] = []

    class Config:
        from_attributes = True
