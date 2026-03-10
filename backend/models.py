"""
Plik zawiera definicje tabel, które fizycznie powstaną w relacyjnej bazie danych SQLite.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    """Model użytkownika systemu
    reprezentuje zarówno Administratora jak i Twórcę.
    Każdy zalogowany użytkownik ma domyślnie rolę Twórcy. 
    Wykorzystano w tym projekcie podejście Role-Based Access Control"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True, nullable=True) # ID z Google OAuth
    email = Column(String, unique=True, index=True)
    name = Column(String)
    role = Column(String, default="Twórca") # Role: "Administrator", "Twórca"
    is_blocked = Column(Boolean, default=False) 

    # Relacja jeden-do-wielu twórca z jego materiałem
    materials = relationship("Material", back_populates="owner")


class Material(Base):
    """Model materiału archiwalnego
     reprezentuje wpis zdjęcia oraz jego metadane i hierarchię"""
    __tablename__ = "material"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    filename = Column(String) # Ścieżka do zapisanego zasobu na dysku
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Metadane i struktura hierarchiczna
    category = Column(String, index=True)

    # Indeksowanie dla przyśpieszenia wyszukiwania po lokalizacji
    location_lat = Column(Float, index=True, nullable=True) 
    location_lng = Column(Float, index=True, nullable=True)
    historical_period = Column(String, nullable=True)
    
    # Powiązanie z autorem (twórcą) wpisu
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", back_populates="materials")
