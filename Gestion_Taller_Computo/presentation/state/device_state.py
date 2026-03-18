import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.device_manager import DeviceManager
from ...application.use_cases.user_manager import UserManager
from ...domain.entities.device import Device
from ...domain.entities.user import User

class DeviceState(rx.State):
    """
    Estado de Gestión de Dispositivos.
    Maneja el registro y consulta de equipos de clientes.
    """
    
    devices: List[Dict[str, Any]] = []
    customers: List[Dict[str, Any]] = []
    
    # Búsqueda y Filtros
    search_query: str = ""
    
    # Modales
    show_device_modal: bool = False
    
    # Formulario de Dispositivo
    device_form: Dict[str, Any] = {
        "brand": "",
        "model": "",
        "serial_number": "",
        "customer_id": ""
    }
    
    is_loading: bool = True

    def on_load(self):
        """Carga datos iniciales."""
        self.is_loading = True
        self.fetch_all_data()

    @rx.event
    def fetch_all_data(self):
        """Extrae dispositivos y clientes del backend."""
        try:
            device_repo = Psycopg2DeviceRepository()
            user_repo = Psycopg2UserRepository()
            
            dev_mgr = DeviceManager(device_repo)
            user_mgr = UserManager(user_repo)
            
            # 1. Obtener Dispositivos
            all_devs = dev_mgr.get_all_devices()
            
            # 2. Obtener Clientes (solo los de rol CUSTOMER)
            all_users = user_mgr.get_all_users()
            self.customers = [
                {"id": str(u.id), "name": u.full_name} 
                for u in all_users if u.role.value == "CUSTOMER"
            ]
            
            # Mapear dispositivos con nombre de cliente para la tabla
            # En un entorno real esto sería un JOIN en el repo, pero aquí lo haremos en memoria por ahora.
            customer_map = {str(u.id): u.full_name for u in all_users}
            
            self.devices = []
            for d in all_devs:
                self.devices.append({
                    "id": str(d.id),
                    "brand": d.brand,
                    "model": d.model,
                    "serial": d.serial_number,
                    "customer": customer_map.get(str(d.customer_id), "Desconocido"),
                    "date": d.created_at.strftime("%Y-%m-%d")
                })
                
        except Exception as e:
            print(f"Error fetching devices: {e}")
        finally:
            self.is_loading = False

    @rx.var
    def filtered_devices(self) -> List[Dict[str, Any]]:
        if not self.search_query:
            return self.devices
        q = self.search_query.lower()
        return [
            d for d in self.devices 
            if q in d["brand"].lower() or q in d["model"].lower() or q in d["serial"].lower() or q in d["customer"].lower()
        ]
    
    @rx.var
    def customer_ids(self) -> List[str]:
        return [c["id"] for c in self.customers]

    @rx.event
    def open_add_device_modal(self):
        self.device_form = {
            "brand": "",
            "model": "",
            "serial_number": "",
            "customer_id": self.customers[0]["id"] if self.customers else ""
        }
        self.show_device_modal = True

    @rx.event
    def save_device(self, form_data: Dict[str, Any]):
        """Registra un nuevo dispositivo."""
        try:
            device_repo = Psycopg2DeviceRepository()
            dev_mgr = DeviceManager(device_repo)
            
            brand = form_data.get("brand")
            model = form_data.get("model")
            serial = form_data.get("serial_number")
            customer_id = form_data.get("customer_id")
            
            if not brand or not model or not serial or not customer_id:
                return rx.window_alert("Todos los campos son obligatorios.")
                
            dev_mgr.register_device(
                brand=brand,
                model=model,
                serial_number=serial,
                customer_id=uuid.UUID(customer_id)
            )
            
            self.show_device_modal = False
            return self.fetch_all_data()
            
        except Exception as e:
            return rx.window_alert(f"Error al registrar dispositivo: {str(e)}")
