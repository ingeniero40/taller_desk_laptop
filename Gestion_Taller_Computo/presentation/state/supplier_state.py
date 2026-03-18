import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_supplier_repository import Psycopg2SupplierRepository
from ...infrastructure.repositories.psycopg_product_repository import Psycopg2ProductRepository
from ...application.use_cases.inventory_manager import InventoryManager
from ...domain.entities.supplier import Supplier

class SupplierState(rx.State):
    """
    Estado de Gestión de Proveedores.
    Maneja el catálogo de proveedores y sus datos de contacto.
    """
    
    suppliers: List[Dict[str, Any]] = []
    
    # Búsqueda y Filtros
    search_query: str = ""
    show_inactive: bool = False
    
    # Modales
    show_supplier_modal: bool = False
    is_editing: bool = False
    
    # Formulario de Proveedor
    supplier_form: Dict[str, Any] = {
        "id": "",
        "name": "",
        "contact_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "is_active": True
    }
    
    is_loading: bool = True

    def on_load(self):
        """Inicializa los datos al cargar la página."""
        self.is_loading = True
        self.fetch_all_data()

    @rx.event
    def fetch_all_data(self):
        """Extrae proveedores del backend."""
        try:
            prod_repo = Psycopg2ProductRepository()
            supp_repo = Psycopg2SupplierRepository()
            mgr = InventoryManager(prod_repo, supp_repo)
            
            # Obtener Proveedores (incluyendo activos/inactivos según filtro)
            all_supps = supp_repo.findAll(only_active=not self.show_inactive)
            
            # Formatear para el frontend
            self.suppliers = []
            for s in all_supps:
                self.suppliers.append({
                    "id": str(s.id),
                    "name": s.name,
                    "contact": s.contact_name or "N/A",
                    "email": s.email or "N/A",
                    "phone": s.phone or "N/A",
                    "address": s.address or "Sin dirección",
                    "is_active": s.is_active,
                    "status_color": "emerald" if s.is_active else "red"
                })
                
        except Exception as e:
            print(f"Error fetching suppliers: {e}")
        finally:
            self.is_loading = False

    @rx.var
    def filtered_suppliers(self) -> List[Dict[str, Any]]:
        if not self.search_query:
            return self.suppliers
        q = self.search_query.lower()
        return [
            s for s in self.suppliers 
            if q in s["name"].lower() or q in s["contact"].lower() or q in s["email"].lower()
        ]

    @rx.event
    def toggle_inactive_filter(self):
        self.show_inactive = not self.show_inactive
        return self.fetch_all_data()

    @rx.event
    def open_add_supplier_modal(self):
        self.is_editing = False
        self.supplier_form = {
            "id": "",
            "name": "",
            "contact_name": "",
            "email": "",
            "phone": "",
            "address": "",
            "is_active": True
        }
        self.show_supplier_modal = True

    @rx.event
    def open_edit_supplier_modal(self, supplier: Dict[str, Any]):
        self.is_editing = True
        self.supplier_form = supplier.copy()
        # Mapear nombres de campos si es necesario (ya coinciden en gran parte)
        if "contact" in self.supplier_form:
            self.supplier_form["contact_name"] = self.supplier_form.pop("contact")
        self.show_supplier_modal = True

    @rx.event
    def save_supplier(self, form_data: Dict[str, Any]):
        """Crea o actualiza un proveedor."""
        try:
            supp_repo = Psycopg2SupplierRepository()
            
            name = form_data.get("name")
            contact = form_data.get("contact_name")
            email = form_data.get("email")
            phone = form_data.get("phone")
            address = form_data.get("address")
            
            if not name:
                return rx.window_alert("El nombre de la empresa es obligatorio.")

            if self.is_editing:
                supplier_id = uuid.UUID(self.supplier_form["id"])
                existing = supp_repo.findById(supplier_id)
                if existing:
                    existing.name = name
                    existing.contact_name = contact
                    existing.email = email
                    existing.phone = phone
                    existing.address = address
                    supp_repo.update(existing)
            else:
                new_supp = Supplier(
                    name=name,
                    contact_name=contact,
                    email=email,
                    phone=phone,
                    address=address
                )
                supp_repo.create(new_supp)
            
            self.show_supplier_modal = False
            return self.fetch_all_data()
            
        except Exception as e:
            return rx.window_alert(f"Error al guardar proveedor: {str(e)}")

    @rx.event
    def toggle_supplier_status(self, supplier_id: str):
        """Desactiva o activa un proveedor."""
        try:
            supp_repo = Psycopg2SupplierRepository()
            s = supp_repo.findById(uuid.UUID(supplier_id))
            if s:
                s.is_active = not s.is_active
                supp_repo.update(s)
                return self.fetch_all_data()
        except Exception as e:
             return rx.window_alert(f"Error al cambiar estado: {str(e)}")
