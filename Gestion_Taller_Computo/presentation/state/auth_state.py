import reflex as rx
from typing import Optional, Dict, Any
from ..state.settings_state import SettingsState
from ...domain.value_objects.user_role import UserRole

class AuthState(rx.State):
    """
    Estado de Autenticación y Autorización (RBAC).
    Maneja el usuario actual y sus permisos dentro del sistema.
    """
    
    # Usuario actual (Mock inicial para desarrollo)
    # En producción esto vendría de una sesión JWT/Base de datos
    user_info: Dict[str, Any] = {
        "username": "admin_gravity",
        "full_name": "Héctor Cruz",
        "role": UserRole.ADMIN.value,
        "is_authenticated": True
    }

    @rx.var
    def current_role(self) -> str:
        return self.user_info.get("role", UserRole.CUSTOMER.value)

    @rx.var
    def is_admin(self) -> bool:
        return self.current_role == UserRole.ADMIN.value

    @rx.var
    def is_technician(self) -> bool:
        return self.current_role == UserRole.TECHNICIAN.value

    @rx.var
    def is_receptionist(self) -> bool:
        return self.current_role == UserRole.RECEPTIONIST.value

    @rx.var
    def can_see_operations(self) -> bool:
        """Determina quién puede ver Inventario, Facturación y Proveedores."""
        return self.current_role in [UserRole.ADMIN.value, UserRole.RECEPTIONIST.value]

    @rx.var
    def can_see_settings(self) -> bool:
        """Solo el Admin puede ver la configuración global."""
        return self.is_admin

    @rx.event
    def logout(self):
        self.user_info = {
            "username": "",
            "full_name": "Invitado",
            "role": UserRole.CUSTOMER.value,
            "is_authenticated": False
        }
        return rx.redirect("/")

    @rx.event
    def set_role_mock(self, role: str):
        """Método utilitario para probar el RBAC durante el desarrollo."""
        self.user_info["role"] = role

    # -- Guards de Navegación (Rutas Protegidas) --

    @rx.event
    def check_admin(self):
        """Redirige si el usuario intenta entrar a Ajustes sin ser Admin."""
        if not self.is_admin:
            return rx.redirect("/")

    @rx.event
    def check_operations(self):
        """Redirige si el usuario intenta entrar a Inventario/Facturación sin permisos."""
        if not self.can_see_operations:
            return rx.redirect("/")
