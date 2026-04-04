import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

# Domain / Application Imports
from ...infrastructure.repositories.psycopg_product_repository import Psycopg2ProductRepository
from ...infrastructure.repositories.psycopg_supplier_repository import Psycopg2SupplierRepository
from ...infrastructure.repositories.psycopg_inventory_movement_repository import Psycopg2InventoryMovementRepository
from ...application.use_cases.inventory_manager import InventoryManager
from ...domain.entities.product import Product
from ...domain.entities.supplier import Supplier

class InventoryState(rx.State):
    """
    Estado de la Gestión de Inventario.
    Maneja el catálogo de productos, stock y proveedores.
    """
    
    # Datos del Catálogo
    products: List[Dict[str, Any]] = []
    suppliers: List[Dict[str, Any]] = []
    
    # Búsqueda y Filtros
    search_query: str = ""
    selected_category: str = "Todas"
    categories: List[str] = ["Todas", "Hardware", "Software", "Periféricos", "Repuestos", "Otros"]
    
    # Modales de Gestión de Inventario
    show_product_modal: bool = False
    is_editing_product: bool = False
    
    # Campos del formulario de producto
    product_form: Dict[str, Any] = {
        "id": "",
        "sku": "",
        "name": "",
        "description": "",
        "cost_price": 0.0,
        "sale_price": 0.0,
        "stock": 0,
        "min_stock": 5,
        "category": "Hardware",
        "supplier_id": ""
    }
    
    # Modales de Stock
    show_stock_modal: bool = False
    stock_adjustment: int = 0
    selected_product_id: str = ""
    
    # Carga de datos
    is_loading: bool = True

    def on_load(self):
        """Inicializa los datos al cargar la página."""
        self.is_loading = True
        self.fetch_all_data()

    @rx.event
    def fetch_all_data(self):
        """Extrae productos y proveedores del backend."""
        try:
            prod_repo = Psycopg2ProductRepository()
            supp_repo = Psycopg2SupplierRepository()
            mov_repo = Psycopg2InventoryMovementRepository()
            mgr = InventoryManager(prod_repo, supp_repo, mov_repo)
            
            # 1. Obtener Productos
            all_prods = prod_repo.findAll()
            self.products = [self._prod_to_dict(p) for p in all_prods]
            
            # 2. Obtener Proveedores
            all_supps = mgr.get_all_suppliers()
            self.suppliers = [self._supp_to_dict(s) for s in all_supps]
            
        except Exception as e:
            print(f"Error fetching inventory: {e}")
        finally:
            self.is_loading = False

    def _prod_to_dict(self, p: Product) -> Dict[str, Any]:
        return {
            "id": str(p.id),
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "stock": p.stock,
            "min_stock": p.min_stock,
            "sale_price": p.sale_price,
            "cost_price": p.cost_price,
            "status_color": "red" if p.stock <= p.min_stock else "cyan" if p.stock > 0 else "gray",
            "is_low_stock": p.stock <= p.min_stock
        }

    def _supp_to_dict(self, s: Supplier) -> Dict[str, Any]:
        return {
            "id": str(s.id),
            "name": s.name,
            "contact": s.contact_name or "N/A"
        }

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def set_selected_category(self, category: str):
        self.selected_category = category

    @rx.var
    def filtered_products(self) -> List[Dict[str, Any]]:
        """Aplica filtros de búsqueda y categoría en memoria para el frontend."""
        prods = self.products
        
        # Filtro de búsqueda
        if self.search_query:
            query = self.search_query.lower()
            prods = [p for p in prods if query in p["name"].lower() or query in p["sku"].lower()]
            
        # Filtro de categoría
        if self.selected_category != "Todas":
            prods = [p for p in prods if p["category"] == self.selected_category]
            
        return prods
    
    @rx.var
    def supplier_ids(self) -> List[str]:
        return [s["id"] for s in self.suppliers]

    @rx.var
    def low_stock_count(self) -> int:
        """Contador rápido de productos con stock bajo o nulo."""
        return len([p for p in self.products if p["is_low_stock"]])

    @rx.var
    def total_value(self) -> str:
        """Valor total estimado del inventario (Costo * Stock)."""
        total = sum(float(p["cost_price"]) * int(p["stock"]) for p in self.products)
        return f"${total:,.2f}"


    # --- Acciones de Producto ---
    
    @rx.event
    def open_add_product_modal(self):
        self.is_editing_product = False
        self.product_form = {
            "id": "",
            "sku": f"SKU-{uuid.uuid4().hex[:6].upper()}",
            "name": "",
            "description": "",
            "cost_price": 0.0,
            "sale_price": 0.0,
            "stock": 0,
            "min_stock": 5,
            "category": "Hardware",
            "supplier_id": self.suppliers[0]["id"] if self.suppliers else ""
        }
        self.show_product_modal = True

    @rx.event
    def save_product(self, form_data: Dict[str, Any]):
        """Crea o actualiza un producto en el inventario."""
        try:
            prod_repo = Psycopg2ProductRepository()
            supp_repo = Psycopg2SupplierRepository()
            mov_repo = Psycopg2InventoryMovementRepository()
            mgr = InventoryManager(prod_repo, supp_repo, mov_repo)
            
            # Sanitizar y Convertir Tipos
            sku = form_data.get("sku")
            name = form_data.get("name")
            cost = float(form_data.get("cost_price", 0))
            price = float(form_data.get("sale_price", 0))
            stock = int(form_data.get("stock", 0))
            min_stock = int(form_data.get("min_stock", 5))
            category = form_data.get("category", "Otros")
            supplier_id = form_data.get("supplier_id")
            
            if not sku or not name:
                return rx.window_alert("SKU y Nombre son obligatorios.")

            mgr.add_product(
                sku=sku, name=name, cost=cost, price=price,
                stock=stock, min_stock=min_stock, category=category,
                supplier_id=uuid.UUID(supplier_id) if supplier_id else None
            )
            
            self.show_product_modal = False
            return self.fetch_all_data() # Recargar la tabla
            
        except Exception as e:
            return rx.window_alert(f"Error al guardar: {str(e)}")

    # --- Acciones de Stock ---
    
    @rx.event
    def set_stock_adjustment(self, value: str):
        try:
            self.stock_adjustment = int(value) if value else 0
        except ValueError:
            self.stock_adjustment = 0
    
    @rx.event
    def open_adjust_stock_modal(self, product_id: str):
        self.selected_product_id = product_id
        self.stock_adjustment = 0
        self.show_stock_modal = True

    @rx.event
    def confirm_stock_adjustment(self):
        """Aplica el cambio de stock en el repositorio y registra el movimiento."""
        if not self.selected_product_id:
            return
            
        try:
            prod_repo = Psycopg2ProductRepository()
            supp_repo = Psycopg2SupplierRepository()
            mov_repo = Psycopg2InventoryMovementRepository()
            mgr = InventoryManager(prod_repo, supp_repo, mov_repo)
            
            mgr.adjust_stock(uuid.UUID(self.selected_product_id), self.stock_adjustment, notes="Ajuste manual")
            self.show_stock_modal = False
            return self.fetch_all_data()
        except Exception as e:
            return rx.window_alert(f"Error al ajustar stock: {str(e)}")
