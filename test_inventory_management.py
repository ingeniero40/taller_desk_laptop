import os
import sys
import uuid
from dotenv import load_dotenv

# Añadir el raíz del proyecto para importar
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.infrastructure.repositories.psycopg_product_repository import Psycopg2ProductRepository
from Gestion_Taller_Computo.infrastructure.repositories.psycopg_supplier_repository import Psycopg2SupplierRepository
from Gestion_Taller_Computo.application.use_cases.inventory_manager import InventoryManager

def test_inventory_flow():
    """
    Test de integración para la gestión de inventario y proveedores.
    """
    print("--- 📦 Probando Gestión de Inventario ---")
    load_dotenv()
    
    # 1. Setup inicial
    product_repo = Psycopg2ProductRepository()
    supplier_repo = Psycopg2SupplierRepository()
    inventory_mgr = InventoryManager(product_repo, supplier_repo)
    
    try:
        # A. Registrar un Proveedor
        print("A. Registrando proveedor...")
        supplier_name = f"REPUESTOS-MX-{uuid.uuid4().hex[:4].upper()}"
        supplier = inventory_mgr.register_supplier(
            name=supplier_name,
            contact="Carlos Gomez",
            email="ventas@repuestos.com",
            phone="555-4001"
        )
        print(f"✅ Proveedor '{supplier.name}' registrado con ID: {supplier.id}")
        
        # B. Agregar Productos al Catálogo
        print("B. Agregando productos (Discos SSD y RAM)...")
        ssd_sku = f"SSD-{uuid.uuid4().hex[:6].upper()}"
        ram_sku = f"RAM-{uuid.uuid4().hex[:6].upper()}"
        
        ssd = inventory_mgr.add_product(
            sku=ssd_sku,
            name="SSD Kington 480GB A400",
            cost=450.00,
            price=850.00,
            stock=10,
            min_stock=5,
            category="Hardware",
            supplier_id=supplier.id
        )
        
        ram = inventory_mgr.add_product(
            sku=ram_sku,
            name="Memoria RAM DDR4 8GB 3200MHz",
            cost=320.00,
            price=680.00,
            stock=15,
            min_stock=5,
            category="Hardware",
            supplier_id=supplier.id
        )
        print(f"✅ Producto '{ssd.name}' (SKU: {ssd.sku}) registrado.")
        print(f"✅ Producto '{ram.name}' (SKU: {ram.sku}) registrado.")
        
        # C. Ajuste de Stock
        print(f"C. Ajustando stock del producto {ssd.sku} (-2 piezas)...")
        inventory_mgr.adjust_stock(ssd.id, -2)
        
        ssd_updated = product_repo.findById(ssd.id)
        print(f"✅ Nuevo stock de {ssd_updated.sku}: {ssd_updated.stock}")
        
        # D. Valuación de Inventario
        print("D. Calculando valuación de inventario...")
        valuation = inventory_mgr.get_inventory_valuation()
        print(f"💰 Valor total del inventario (costo): ${valuation:.2f}")
        
        # E. Reporte de Stock Bajo
        print("E. Generando reporte de stock crítico...")
        # Forzar uno a stock bajo para el reporte
        inventory_mgr.adjust_stock(ram.id, -12) # Quedan 3 (menos del min_stock que es 5)
        
        low_stock = inventory_mgr.get_low_stock_reports()
        print(f"⚠️  Productos con stock bajo encontrados: {len(low_stock)}")
        for p in low_stock:
            print(f"   - {p.name} (SKU: {p.sku}) | Stock Actual: {p.stock} | Mínimo: {p.min_stock}")
            
    except Exception as e:
        print(f"❌ Fallo en el flujo de inventario: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inventory_flow()
