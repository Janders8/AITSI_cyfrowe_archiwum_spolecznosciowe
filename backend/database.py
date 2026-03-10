"""
Plik odpowiedzialny za definicję powiązania z bazą danych wg standardu SQLAlchemy.
Ustanawia silnik łączący Pythona z SQLite oraz przygotowuje fabrykę sesji zabezpieczającą pojedyncze zapytania.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Konfiguracja połączenia z lokalną bazą SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./archiwum.db"

# Przygotowanie silnika bazy danych
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Fabryka sesji dla zapytań do bazy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Główna klasa bazowa dla deklaratywnych modeli SQLAlchemy
Base = declarative_base()
