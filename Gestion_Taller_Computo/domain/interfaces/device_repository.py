from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.device import Device
import uuid


class IDeviceRepository(ABC):
    """
    Interfaz de repositorio de dispositivos siguiendo Clean Architecture.
    """

    @abstractmethod
    def create(self, device: Device) -> Device:
        """Registra un nuevo dispositivo."""
        pass

    @abstractmethod
    def findById(self, deviceId: uuid.UUID) -> Optional[Device]:
        """Busca un dispositivo por su ID."""
        pass

    @abstractmethod
    def findBySerialNumber(self, serial: str) -> Optional[Device]:
        """Busca un dispositivo por su número de serie."""
        pass

    @abstractmethod
    def findByCustomerId(self, customerId: uuid.UUID) -> List[Device]:
        """Recupera todos los dispositivos pertenecientes a un cliente."""
        pass

    @abstractmethod
    def findAll(self) -> List[Device]:
        """Recupera todos los dispositivos registrados."""
        pass

    @abstractmethod
    def update(self, device: Device) -> Device:
        """Actualiza los datos de un dispositivo."""
        pass

    @abstractmethod
    def delete(self, deviceId: uuid.UUID) -> bool:
        """Elimina un dispositivo del sistema."""
        pass
