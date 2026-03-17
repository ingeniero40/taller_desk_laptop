import os
from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/taller_db")

engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    # Aquí importaríamos todas las entidades para que SQLModel las reconozca
    from ...domain.entities.user import User
    from ...domain.entities.device import Device
    from ...domain.entities.work_order import WorkOrder
    
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
