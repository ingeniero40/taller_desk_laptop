from typing import List, Optional
from ...domain.entities.device import Device
from ...domain.interfaces.device_repository import IDeviceRepository
import uuid

class DeviceManager:
    """
    Caso de uso para la gestión integral de dispositivos.
    """
    
    def __init__(self, repository: IDeviceRepository):
        self.repository = repository

    def register_device(self, brand: str, model: str, serial_number: str, customer_id: uuid.UUID) -> Device:
        """
        Registra un nuevo dispositivo en el sistema.
        """
        # Validar si el serial ya existe
        existing = self.repository.findBySerialNumber(serial_number)
        if existing:
            raise ValueError(f"El dispositivo con serie '{serial_number}' ya está registrado.")
            
        new_device = Device(
            brand=brand,
            model=model,
            serial_number=serial_number,
            customer_id=customer_id
        )
        return self.repository.create(new_device)

    def get_device_by_id(self, device_id: uuid.UUID) -> Optional[Device]:
        return self.repository.findById(device_id)

    def get_devices_by_customer(self, customer_id: uuid.UUID) -> List[Device]:
        return self.repository.findByCustomerId(customer_id)

    def get_all_devices(self) -> List[Device]:
        return self.repository.findAll()

    def update_device_info(self, device_id: uuid.UUID, brand: str = None, model: str = None) -> Device:
        device = self.repository.findById(device_id)
        if not device:
            raise ValueError("Dispositivo no encontrado.")
            
        if brand: device.brand = brand
        if model: device.model = model
        
        return self.repository.update(device)

    def remove_device(self, device_id: uuid.UUID) -> bool:
        return self.repository.delete(device_id)
