import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...application.use_cases.user_manager import UserManager
from ...domain.entities.user import User
from ...domain.value_objects.user_role import UserRole

class SettingsState(rx.State):
    """
    Estado de Configuración Global.
    Maneja la información del taller, preferencias de usuario y administración de cuentas.
    """
    
    # 1. Información del Taller (Placeholder - Podría venir de una tabla 'config')
    workshop_info: Dict[str, str] = {
        "name": "Taller Desk & Laptop",
        "address": "Av. Reforma #456, Monterrey, NL",
        "phone": "+52 81 2345 6789",
        "email": "soporte@deskandlaptop.com",
        "currency": "MXN",
        "tax_rate": "16.0"
    }
    
    # 2. Gestión de Usuarios
    users: List[Dict[str, Any]] = []
    show_user_modal: bool = False
    
    # Formulario de Nuevo Usuario
    user_form: Dict[str, str] = {
        "username": "",
        "full_name": "",
        "email": "",
        "password": "",
        "role": "TECHNICIAN"
    }
    
    # 3. Preferencias del Sistema
    dark_mode: bool = False
    language: str = "Español"
    
    is_loading: bool = True

    def on_load(self):
        """Pre-carga la lista de usuarios al entrar a configuracion."""
        self.is_loading = True
        self.fetch_users()

    @rx.event
    def fetch_users(self):
        """Obtiene todos los usuarios del sistema."""
        try:
            repo = Psycopg2UserRepository()
            mgr = UserManager(repo)
            all_users = mgr.get_all_users()
            
            self.users = []
            for u in all_users:
                self.users.append({
                    "id": str(u.id),
                    "username": u.username,
                    "name": u.full_name,
                    "email": u.email,
                    "role": u.role.value,
                    "is_active": u.is_active,
                    "role_color": "cyan" if u.role == UserRole.ADMIN else "indigo" if u.role == UserRole.TECHNICIAN else "gray"
                })
        except Exception as e:
            print(f"Error fetching users: {e}")
        finally:
            self.is_loading = False

    @rx.event
    def set_workshop_info(self, key: str, value: str):
        self.workshop_info[key] = value

    @rx.event
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    # -- Acciones de Usuarios --
    
    @rx.event
    def open_add_user_modal(self):
        self.user_form = {
            "username": "",
            "full_name": "",
            "email": "",
            "password": "",
            "role": "TECHNICIAN"
        }
        self.show_user_modal = True

    @rx.event
    def save_new_user(self, form_data: Dict[str, str]):
        """Crea un nuevo usuario (Staff/Admin/Client)."""
        try:
            repo = Psycopg2UserRepository()
            mgr = UserManager(repo)
            
            username = form_data.get("username")
            full_name = form_data.get("full_name")
            email = form_data.get("email")
            password = form_data.get("password")
            role_str = form_data.get("role")
            
            if not username or not password or not full_name:
                return rx.window_alert("Usuario, Nombre y Contraseña son requeridos.")
            
            # Nota: En produccion el password_hash se genera aqui
            mgr.create_user(
                username=username,
                email=email,
                password_hash=password, # El manager lo recibe como hash pero aqui simplificamos el flujo
                full_name=full_name,
                role=UserRole(role_str)
            )
            
            self.show_user_modal = False
            return self.fetch_users()
            
        except Exception as e:
            return rx.window_alert(f"Error al crear usuario: {str(e)}")

    @rx.event
    def toggle_user_active(self, user_id: str, current_status: bool):
        """Activa/Desactiva cuenta de usuario."""
        try:
            repo = Psycopg2UserRepository()
            mgr = UserManager(repo)
            mgr.update_user_status(uuid.UUID(user_id), not current_status)
            return self.fetch_users()
        except Exception as e:
             return rx.window_alert(f"Error al cambiar estado: {str(e)}")
