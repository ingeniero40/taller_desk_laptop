import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.device import Device
from ...domain.interfaces.device_repository import IDeviceRepository
from ..database.psycopg_db import Psycopg2Database

class Psycopg2DeviceRepository(IDeviceRepository):
    """
    Implementación del repositorio de dispositivos utilizando Psycopg2.
    """
    
    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, device: Device) -> Device:
        query = """
            INSERT INTO devices (
                id, created_at, updated_at, brand, model, serial_number, customer_id,
                physical_condition, accessories, photo_url, device_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(device.id), device.created_at, device.updated_at,
            device.brand, device.model, device.serial_number, str(device.customer_id),
            device.physical_condition, device.accessories, device.photo_url, device.device_type
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return device

    def findById(self, deviceId: uuid.UUID) -> Optional[Device]:
        query = "SELECT * FROM devices WHERE id = %s"
        params = (str(deviceId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findBySerialNumber(self, serial: str) -> Optional[Device]:
        query = "SELECT * FROM devices WHERE serial_number = %s"
        params = (serial,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByCustomerId(self, customerId: uuid.UUID) -> List[Device]:
        query = "SELECT * FROM devices WHERE customer_id = %s"
        params = (str(customerId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def findAll(self) -> List[Device]:
        query = "SELECT * FROM devices"
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def update(self, device: Device) -> Device:
        device.updated_at = datetime.utcnow()
        query = """
            UPDATE devices 
            SET brand = %s, model = %s, serial_number = %s, customer_id = %s,
                physical_condition = %s, accessories = %s, photo_url = %s,
                device_type = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            device.brand, device.model, device.serial_number, str(device.customer_id),
            device.physical_condition, device.accessories, device.photo_url,
            device.device_type, device.updated_at, str(device.id)
        )
        self.db.executeRawQuery(query, params)
        return device

    def delete(self, deviceId: uuid.UUID) -> bool:
        query = "DELETE FROM devices WHERE id = %s"
        params = (str(deviceId),)
        try:
            self.db.executeRawQuery(query, params)
            return True
        except:
            return False

    def _map_row_to_entity(self, row) -> Device:
        """
        Mapea una fila de Psycopg2 a la entidad Device.
        Soporta tanto el esquema antiguo (7 cols) como el nuevo (11 cols con admisión).
        """
        return Device(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            brand=row[3],
            model=row[4],
            serial_number=row[5],
            customer_id=uuid.UUID(str(row[6])),
            physical_condition=row[7] if len(row) > 7 else None,
            accessories=row[8] if len(row) > 8 else None,
            photo_url=row[9] if len(row) > 9 else None,
            device_type=row[10] if len(row) > 10 else "Laptop/PC",
        )
