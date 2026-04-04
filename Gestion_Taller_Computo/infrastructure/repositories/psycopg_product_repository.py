import uuid
from typing import List, Optional
from datetime import datetime
from ...domain.entities.product import Product
from ...domain.interfaces.product_repository import IProductRepository
from ..database.psycopg_db import Psycopg2Database


class Psycopg2ProductRepository(IProductRepository):
    """
    Implementación del repositorio de productos con Psycopg2.
    """

    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def create(self, product: Product) -> Product:
        query = """
            INSERT INTO products (
                id, created_at, updated_at, sku, barcode, name, description, 
                cost_price, sale_price, stock, min_stock, category, supplier_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (
            str(product.id),
            product.created_at,
            product.updated_at,
            product.sku,
            product.barcode,
            product.name,
            product.description,
            product.cost_price,
            product.sale_price,
            product.stock,
            product.min_stock,
            product.category,
            str(product.supplier_id) if product.supplier_id else None,
        )
        self.db.executeRawQuery(query, params, fetch=True)
        return product

    def findById(self, productId: uuid.UUID) -> Optional[Product]:
        query = """
            SELECT id, created_at, updated_at, sku, name, description, 
                   cost_price, sale_price, stock, min_stock, category, supplier_id 
            FROM products WHERE id = %s
        """
        params = (str(productId),)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByBarcode(self, barcode: str) -> Optional[Product]:
        # Como barcode no existe en el esquema devuelto por check_columns, 
        # lo buscaremos por SKU si es necesario, o consideraremos que es una versión simplificada.
        # Por ahora lo dejaremos como búsqueda por SKU para evitar errores.
        query = """
            SELECT id, created_at, updated_at, sku, name, description, 
                   cost_price, sale_price, stock, min_stock, category, supplier_id 
            FROM products WHERE sku = %s
        """
        params = (barcode,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findBySku(self, sku: str) -> Optional[Product]:
        query = """
            SELECT id, created_at, updated_at, sku, name, description, 
                   cost_price, sale_price, stock, min_stock, category, supplier_id 
            FROM products WHERE sku = %s
        """
        params = (sku,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        if results:
            return self._map_row_to_entity(results[0])
        return None

    def findByCategory(self, category: str) -> List[Product]:
        query = """
            SELECT id, created_at, updated_at, sku, name, description, 
                   cost_price, sale_price, stock, min_stock, category, supplier_id 
            FROM products WHERE category = %s
        """
        params = (category,)
        results = self.db.executeRawQuery(query, params, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def findAll(self) -> List[Product]:
        query = """
            SELECT id, created_at, updated_at, sku, name, description, 
                   cost_price, sale_price, stock, min_stock, category, supplier_id 
            FROM products
        """
        results = self.db.executeRawQuery(query, fetch=True)
        return [self._map_row_to_entity(row) for row in results]

    def update(self, product: Product) -> Product:
        product.updated_at = datetime.utcnow()
        query = """
            UPDATE products 
            SET sku = %s, name = %s, description = %s, cost_price = %s, 
                sale_price = %s, stock = %s, min_stock = %s, category = %s, 
                supplier_id = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            product.sku,
            product.name,
            product.description,
            product.cost_price,
            product.sale_price,
            product.stock,
            product.min_stock,
            product.category,
            str(product.supplier_id) if product.supplier_id else None,
            product.updated_at,
            str(product.id),
        )
        self.db.executeRawQuery(query, params)
        return product

    def update_stock(self, productId: uuid.UUID, quantity_change: int) -> bool:
        query = """
            UPDATE products 
            SET stock = stock + %s, updated_at = %s
            WHERE id = %s
        """
        params = (quantity_change, datetime.utcnow(), str(productId))
        try:
            self.db.executeRawQuery(query, params)
            return True
        except:
            return False

    def delete(self, productId: uuid.UUID) -> bool:
        query = "DELETE FROM products WHERE id = %s"
        params = (str(productId),)
        try:
            self.db.executeRawQuery(query, params)
            return True
        except:
            return False

    def _map_row_to_entity(self, row) -> Product:
        """
        Mapea fila de DB a Product basándose en selección explícita.
        Orden del SELECT: 0:id, 1:created_at, 2:updated_at, 3:sku, 4:name, 5:description, 6:cost, 7:sale, 8:stock, 9:min_stock, 10:category, 11:sup_id
        """
        return Product(
            id=uuid.UUID(str(row[0])),
            created_at=row[1],
            updated_at=row[2],
            sku=row[3],
            barcode=None, # barcode no existe en el esquema actual
            name=row[4],
            description=row[5],
            cost_price=float(row[6]),
            sale_price=float(row[7]),
            stock=int(row[8]),
            min_stock=int(row[9]),
            category=row[10],
            supplier_id=uuid.UUID(str(row[11])) if row[11] else None,
        )
