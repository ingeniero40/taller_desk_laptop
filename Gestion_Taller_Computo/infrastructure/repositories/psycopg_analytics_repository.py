from typing import List, Dict, Any, Optional
from datetime import datetime
from ...domain.interfaces.analytics_repository import IAnalyticsRepository
from ..database.psycopg_db import Psycopg2Database


class Psycopg2AnalyticsRepository(IAnalyticsRepository):
    """
    Implementación del repositorio de analíticas utilizando Psycopg2.
    """

    def __init__(self, db_handler: Psycopg2Database = None):
        self.db = db_handler or Psycopg2Database()

    def get_revenue_stats(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Recupera el total recaudado y facturado en el rango de tiempo.
        """
        query_payments = """
            SELECT COALESCE(SUM(amount), 0) FROM payments 
            WHERE payment_date BETWEEN %s AND %s
        """
        query_invoices = """
            SELECT COALESCE(SUM(total), 0) FROM invoices 
            WHERE created_at BETWEEN %s AND %s
        """

        payments_total = self.db.executeRawQuery(
            query_payments, (start_date, end_date), fetch=True
        )
        invoices_total = self.db.executeRawQuery(
            query_invoices, (start_date, end_date), fetch=True
        )

        return {
            "total_collected": float(payments_total[0][0]),
            "total_invoiced": float(invoices_total[0][0]),
            "period": f"{start_date.date()} to {end_date.date()}",
        }

    def get_technician_productivity(self) -> List[Dict[str, Any]]:
        """
        Analiza cuántas órdenes tiene cada técnico por estado.
        """
        query = """
            SELECT u.full_name, wo.status, COUNT(wo.id) as count
            FROM users u
            JOIN work_orders wo ON u.id = wo.technician_id
            GROUP BY u.full_name, wo.status
            ORDER BY u.full_name, wo.status;
        """
        results = self.db.executeRawQuery(query, fetch=True)

        stats = []
        for row in results:
            stats.append(
                {"technician": row[0], "status": row[1], "order_count": int(row[2])}
            )
        return stats

    def get_work_order_summary(self) -> Dict[str, Any]:
        """
        Resumen global de todos los estados en el taller.
        """
        query = "SELECT status, COUNT(*) FROM work_orders GROUP BY status"
        results = self.db.executeRawQuery(query, fetch=True)

        summary = {row[0]: int(row[1]) for row in results}
        summary["total_orders"] = sum(summary.values())
        return summary

    def get_top_moving_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Basado en el nivel de stock (como proxy para uso, ya que aún no tenemos tabla de 'consumo').
        """
        query = """
            SELECT name, sku, stock, min_stock, category 
            FROM products 
            ORDER BY stock ASC 
            LIMIT %s;
        """
        results = self.db.executeRawQuery(query, (limit,), fetch=True)

        top_list = []
        for row in results:
            top_list.append(
                {
                    "name": row[0],
                    "sku": row[1],
                    "stock": int(row[2]),
                    "min_stock": int(row[3]),
                    "category": row[4],
                }
            )
        return top_list

    def get_recent_work_orders(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Une las órdenes con dispositivos y clientes.
        """
        query = """
            SELECT wo.ticket_number, d.brand, d.model, u.full_name, wo.status, wo.created_at
            FROM work_orders wo
            JOIN devices d ON wo.device_id = d.id
            JOIN users u ON d.customer_id = u.id
            ORDER BY wo.created_at DESC
            LIMIT %s;
        """
        results = self.db.executeRawQuery(query, (limit,), fetch=True)

        recent_orders = []
        for row in results:
            recent_orders.append(
                {
                    "ticket": row[0],
                    "device": f"{row[1]} {row[2]}",
                    "customer": row[3],
                    "status": row[4],
                    "date": row[5].strftime("%Y-%m-%d %H:%M") if row[5] else "N/A",
                }
            )
        return recent_orders
