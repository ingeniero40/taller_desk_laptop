import uuid
from datetime import datetime
from Gestion_Taller_Computo.domain.entities.user import User
from Gestion_Taller_Computo.domain.value_objects.user_roles import UserRole
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository

def seed_pos_customer():
    repo = Psycopg2UserRepository()
    existing = repo.findAll()
    if not any(u.full_name == "Público General" for u in existing):
        print("Creando cliente: Público General")
        user = User(
            full_name="Público General",
            email="pos@taller.local",
            phone="00000000",
            role=UserRole.CUSTOMER,
            is_active=True
        )
        repo.create(user)
        print(f"ID asignado: {user.id}")
    else:
        print("Público General ya existe.")

if __name__ == "__main__":
    seed_pos_customer()
