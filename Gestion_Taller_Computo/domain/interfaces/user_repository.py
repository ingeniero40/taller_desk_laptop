from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User
import uuid

class IUserRepository(ABC):
    """
    Interfaz de repositorio de usuarios siguiendo Clean Architecture.
    Determina cómo se debe interactuar con los datos de usuario sin depender de una implementación concreta.
    """
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        pass
    
    @abstractmethod
    def findById(self, userId: uuid.UUID) -> Optional[User]:
        """Busca un usuario por su identificador."""
        pass
    
    @abstractmethod
    def findByUsername(self, username: str) -> Optional[User]:
        """Busca un usuario por su nombre de usuario."""
        pass
    
    @abstractmethod
    def findAll(self) -> List[User]:
        """Recupera todos los usuarios registrados."""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Actualiza los datos de un usuario existente."""
        pass
    
    @abstractmethod
    def delete(self, userId: uuid.UUID) -> bool:
        """Elimina un usuario por su identificador."""
        pass
