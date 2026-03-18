import uuid
from typing import List, Optional
from ...domain.entities.user import User
from ...domain.interfaces.user_repository import IUserRepository
from ...domain.value_objects.user_role import UserRole
from psycopg2.extras import RealDictCursor
from ..database.psycopg_db import Psycopg2Database

from datetime import datetime

class Psycopg2UserRepository(IUserRepository):
    """
    Implementación del repositorio de usuarios utilizando Psycopg2.
    """
    
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, user: User) -> User:
        query = """
            INSERT INTO users (id, username, email, password_hash, full_name, role, phone, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, created_at, updated_at;
        """
        params = (
            str(user.id),
            user.username,
            user.email,
            user.password_hash,
            user.full_name,
            user.role.value,
            user.phone,
            user.is_active,
            user.created_at,
            user.updated_at
        )
        
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            # Sincronizamos los campos generados por la BD si existieran, aunque aquí los pasamos nosotros
            return user
        return None

    def findById(self, userId: uuid.UUID) -> Optional[User]:
        query = "SELECT * FROM users WHERE id = %s"
        params = (str(userId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None



    def findByUsername(self, username: str) -> Optional[User]:
        query = "SELECT * FROM users WHERE username = %s"
        params = (username,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findAll(self) -> List[User]:
        query = "SELECT * FROM users"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def update(self, user: User) -> User:
        user.updated_at = datetime.utcnow()
        query = """
            UPDATE users 
            SET username = %s, email = %s, password_hash = %s, full_name = %s, role = %s, phone = %s, is_active = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            user.username,
            user.email,
            user.password_hash,
            user.full_name,
            user.role.value,
            user.phone,
            user.is_active,
            user.updated_at,
            str(user.id)
        )
        self.db.executeRawQuery(query, params)
        return user

    def delete(self, userId: uuid.UUID) -> bool:
        query = "DELETE FROM users WHERE id = %s"
        params = (str(userId),)
        try:
            self.db.executeRawQuery(query, params)
            return True
        except:
            return False

    def _map_row_to_entity(self, row) -> User:
        """
        Mapea una fila de Psycopg2 a la entidad User.
        Orden basado en la tabla real: id, created_at, updated_at, username, email, password_hash, full_name, role, phone, is_active
        """
        return User(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            username=row[3],
            email=row[4],
            password_hash=row[5],
            full_name=row[6],
            role=UserRole(row[7]),
            phone=row[8],
            is_active=row[9]
        )

