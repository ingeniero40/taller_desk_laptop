from typing import List, Optional
from ...domain.entities.user import User
from ...domain.interfaces.user_repository import IUserRepository
from ...domain.value_objects.user_role import UserRole
import uuid

class UserManager:
    """
    Caso de uso para la gestión integral de usuarios.
    Siguiendo Clean Architecture, esta clase no conoce los detalles de implementación de la base de datos.
    """
    
    def __init__(self, repository: IUserRepository):
        self.repository = repository

    def create_user(self, username: str, email: str, password_hash: str, full_name: str, 
                   role: UserRole = UserRole.CUSTOMER, phone: str = None) -> User:
        """
        Lógica de negocio para crear un nuevo usuario validando reglas básicas.
        """
        # Aquí se podrían añadir validaciones adicionales (ej. si el usuario ya existe)
        existing = self.repository.findByUsername(username)
        if existing:
            raise ValueError(f"El usuario '{username}' ya existe.")
            
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            phone=phone
        )
        return self.repository.create(new_user)

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        return self.repository.findById(user_id)

    def get_all_users(self) -> List[User]:
        return self.repository.findAll()

    def update_user_status(self, user_id: uuid.UUID, is_active: bool) -> User:
        user = self.repository.findById(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")
            
        user.is_active = is_active
        return self.repository.update(user)
