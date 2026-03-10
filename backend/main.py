"""
Główny plik uruchomieniowy backendu.
Uruchomienie FastAPI, tworzenie tabel w bazie danych
oraz definiowanie endpointów.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import pozostałch modułów
import os
import shutil
import uuid
import models
import schemas
import auth
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Query, File, UploadFile, Form
from typing import List, Optional

# Biblioteki odpowiedzialne za logowanie przez Google
from google.oauth2 import id_token
from google.auth.transport import requests

# Obsługa statycznych plików na serwerze (do wyświetlania zdjęć)
from fastapi.staticfiles import StaticFiles

# Funkcja do otwierania i automatycznego zamykania połączenia z bazą
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(email: str = Depends(auth.verify_token), db: Session = Depends(get_db)):
    """
    Funkcja zwracająca pełen profill użytkownika, m.in. z jego rolą.
    """
    # Wyszukanie użytkownika w bazie danych
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Użytkownik nie istnieje w bazie.")
    
    # Sprawdzenie czy użytkownik nie jest zablokowany
    if user.is_blocked:
        raise HTTPException(status_code=403, detail="Twoje konto uległo blokadzie.")
    
    return user

# Tworzenie Tabel
# SQLAlchemy wczytuje plik models.py i generuje na jego podstawie tabele w archiwum.db o ile jeszcze nie istnieją
models.Base.metadata.create_all(bind=engine)

# Utworzenie aplikacji 
app = FastAPI(
    title="Cyfrowe Archiwum Społecznościowe",
    description="API dla projektu archiwum społecznościowego.",
    version="1.0.0"
)

# Konfiguracja CORS
# pozwalam zdefiniowanym stronom na łączenie się z serwerem serwisu.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montowanie katalogu uploads, by móc je wyświetlać na stronie
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Próbny endpoint dla testów.
@app.get("/")
def test_status_serwera():
    return {"message": "Serwer i Baza działają! :)"}



# Logowanie przez Google
from dotenv import load_dotenv
import os

# Wskazanie ścieżki do pliku .env na frontendzie (tamten zawiera klucz google)
load_dotenv(dotenv_path="../frontend/.env")

# Klucz ladowany z .env
GOOGLE_CLIENT_ID = os.getenv("VITE_GOOGLE_CLIENT_ID")

@app.post("/auth/google", response_model=schemas.TokenResponse)
def auth_google(token_data: schemas.GoogleToken, db: Session = Depends(get_db)):
    """
Funkcja do weryfikacji tokenu Google, tworzenia nowego konta (jeśłi potrzeba) oraz generowania tokenu JWT.

    """
    try:
        # sprawdzenie autentyczności tokenu
        idinfo = id_token.verify_oauth2_token(
            token_data.credential, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )

        # Zgranie zmiennych
        email = idinfo['email']
        name = idinfo.get('name', 'Brak Imienia')
        google_id = idinfo['sub']

        # Wyszukanie użytkownika
        user = db.query(models.User).filter(models.User.email == email).first()

        # Jeśli nie ma go w bazie to tworzy się nowy użytkownik z rolą Twórca
        if not user:

            user = models.User(
                email=email,
                name=name,
                google_id=google_id,
                role="Twórca"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Sprawdzenie czy Administrator nie zablokował użytkownika!
            if user.is_blocked:
                raise HTTPException(status_code=403, detail="Konto zostało zablokowane przez Administratora.")

        # Wygenerowanie tokenu dla podanego maila i roli
        access_token = auth.create_access_token(
            data={"sub": user.email, "role": user.role}
        )

        return {"access_token": access_token, "token_type": "bearer"}

    # obsługa nieprawidłowego tokenu Google
    except ValueError:
        raise HTTPException(status_code=401, detail="Nieprawidłowy token uwierzytelniający z Google.")



# Prywatne API (Dla twórców i administratorów)

@app.post("/materials/", response_model=schemas.Material)
def create_material(
        title: str = Form(...),
        description: Optional[str] = Form(None),
        category: str = Form("Ogólne"),
        historical_period: Optional[str] = Form(None),
        location_lat: Optional[float] = Form(None),
        location_lng: Optional[float] = Form(None),
        file: UploadFile = File(...),                    
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Funkcja Do tworzenia nowego zdjęcia w archiwum. 
    """

    # Sprawdzenie ról
    if current_user.role not in ["Twórca", "Administrator"]:
        raise HTTPException(status_code=403, detail="Tylko Twórcy i Administratorzy mogą dodawać nowe zdjęcia do archiwum.")

    # Zachowanie rozszerzenia zdjęcia
    file_extension = file.filename.split(".")[-1]
    
    # Generowanie losowej nazwy pliku (by na dysku nie nadpisać zdjęcia)
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Pełna ścieżka do zapisania zdjęcia
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Kopiowanie zdjęcia do folderu
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


    # Zapis metadanych i ścieżki do bazy danych
    new_material = models.Material(
        title=title,
        description=description,
        filename=unique_filename,
        category=category,
        historical_period=historical_period,
        location_lat=location_lat,
        location_lng=location_lng,
        owner_id=current_user.id
    )
    
    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


@app.get("/materials/my", response_model=List[schemas.Material])
def get_my_materials(
        db: Session = Depends(get_db),
        current_user: models.User = Depends(get_current_user)
):
    """
    Funkcja pozwalająca zalogowanemu Twórcy pobrać wyłącznie jego materiały
    """
    
    # Filtracja tylko tych materiałów, gdzie ID właściciela jest równe ID aktualnie zalogowanego użytkownika
    my_materials = db.query(models.Material).filter(models.Material.owner_id == current_user.id).all()
    
    return my_materials


@app.put("/materials/{material_id}", response_model=schemas.Material)
def update_material(
        material_id: int, 
        material_data: schemas.MaterialUpdate, 
        db: Session = Depends(get_db), 
        current_user: models.User = Depends(get_current_user)
):
    """
    Funkcja edycji materiału przez użytkownika.
    """

    # Znalezienie materiału w bazie
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    
    # W wypadku nieznalezienia zdjęcia
    if not material:
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego zdjęcia w archiwum.")

    # Sprawdzenie uprawnień użytkownika
    if material.owner_id != current_user.id and current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Możesz edytować wyłącznie własne zdjęcia.")

    # Aktualizacja wysłanych danych
    update_data = material_data.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(material, key, value) 

    # Zapis zaktualizowanego obiektu
    db.commit()
    db.refresh(material)

    return material

@app.delete("/materials/{material_id}")
def delete_material(
        material_id: int, 
        db: Session = Depends(get_db), 
        current_user: models.User = Depends(get_current_user)
):
    """
    Funkcja do kasowania zdjęć. 
    """
    # Wyszukanie zdjęcia
    material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego zdjęcia w archiwum.")

    # Sprawdzenie uprawnień
    if material.owner_id != current_user.id and current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Brak uprawnień. Tylko właściciel lub Administrator może skasować to zdjęcie.")

    # Usunięcie pliku zdjęcia
    file_path = os.path.join(UPLOAD_DIR, material.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Usunięcie wpisu w bazie danych
    db.delete(material)
    db.commit()

    return {"message": "Zdjęcie i dane wykasowane z serwera."}

@app.patch("/users/{user_id}/block")
def block_user(
        user_id: int, 
        db: Session = Depends(get_db), 
        current_user: models.User = Depends(get_current_user)
):
    """
    Funkcja do blokowania użtkownika przez Administratora 
    Uniemożliwia to użytkownikowi zalogowanie do serwisu.

    """
    # Sprawdzenie czy to administratory
    if current_user.role != "Administrator":
        raise HTTPException(status_code=403, detail="Tylko Administrator może korzystać z panelu blokowania kont.")

    # Znalezienie blokowanego użytkownika
    user_to_block = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_block:
        raise HTTPException(status_code=404, detail="Taki użytkownik nie istnieje.")

    # Blokowanie użytkownika
    user_to_block.is_blocked = True
    db.commit()
    

    return {"message": f"Użytkownik {user_to_block.email} został zablokowany."}


# Publiczne api (nie wymagające uprawnień)


@app.get("/materials/", response_model=List[schemas.Material])
def get_materials(
    skip: int = 0,
    limit: int = 100, 
    search: Optional[str] = None,
    category: Optional[str] = None, 
    historical_period: Optional[str] = None,
    min_lat: Optional[float] = Query(None, description="Minimalna szerokość geograficzna (dół mapy)"),
    max_lat: Optional[float] = Query(None, description="Maksymalna szerokość geograficzna (góra mapy)"),
    min_lng: Optional[float] = Query(None, description="Minimalna długość geograficzna (lewo mapy)"),
    max_lng: Optional[float] = Query(None, description="Maksymalna długość geograficzna (prawo mapy)"),
    db: Session = Depends(get_db) # Wykorzystanie funkcji get_db do otwierania i zamykania połączenia z bazą
):
    """
    Pobiera i filtruje listę materiałów. 
    Wspiera proste szukanie obszarowe Bounding Box (po lat i lng). 
    """
    
    # Budowa zapytania
    query = db.query(models.Material)

    # Filtry użytkownika
    if category:
        # Wyszukiwanie po kategorii
        query = query.filter(models.Material.category.startswith(category))
        
    if search:
        # Wyszukuje bez względu na wielkość liter w tytule zdjęcia
        query = query.filter(models.Material.title.ilike(f"%{search}%"))
        
    if historical_period:
        # Zwykłe dopasowanie do podanego okresu
        query = query.filter(models.Material.historical_period == historical_period)

    # Logika wyszukiwania po widocznej lokalizacji
    if min_lat is not None and max_lat is not None and min_lng is not None and max_lng is not None:
        
        # Filtracja bazy po widocznym kwadracie mapy
        query = query.filter(
            models.Material.location_lat >= min_lat,
            models.Material.location_lat <= max_lat,
            models.Material.location_lng >= min_lng,
            models.Material.location_lng <= max_lng
        )

    # Wysłanie zbudowanego zapytania do bazy 
    materials = query.offset(skip).limit(limit).all()
    
    # Obsługa błędów, jeśli nic nie ma
    if not materials and (search or category or historical_period or min_lat is not None):
        params_info = []
        if search: params_info.append(f"tekstem: '{search}'")
        if category: params_info.append(f"kategorią: '{category}'")
        if historical_period: params_info.append(f"okresem: '{historical_period}'")
        if min_lat is not None: params_info.append("zadaną lokalizacją")
        raise HTTPException(status_code=404, detail=f"Brak materiałów z {' oraz '.join(params_info)}")
    
    return materials


@app.get("/materials/{material_id}", response_model=schemas.Material)
def get_material(material_id: int, db: Session = Depends(get_db)):
    """Pobiera jeden konkretny materiał po jego ID."""
    
    # Zwrócenie jednego wyniku
    db_material = db.query(models.Material).filter(models.Material.id == material_id).first()
    
    # Obsługa na wypadek braku zdjęcia
    if db_material is None:
        raise HTTPException(status_code=404, detail="Zdjęcie o takim ID nie istnieje.")
        
    return db_material

