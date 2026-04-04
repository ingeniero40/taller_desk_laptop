from typing import List, Dict, Any
from datetime import datetime, timedelta
from ...domain.interfaces.analytics_repository import IAnalyticsRepository


class ReportManager:
    """
    Caso de uso para la generación de reportes operativos y estratégicos.
    """

    def __init__(self, analytics_repo: IAnalyticsRepository):
        self.analytics_repo = analytics_repo

    def get_monthly_financial_report(self) -> Dict[str, Any]:
        """
        Reporte acumulado del mes en curso vs mes anterior usando UTC.
        """
        now = datetime.utcnow()
        start_current = now.replace(day=1, hour=0, minute=0, second=0)
        end_current = now

        last_month = start_current - timedelta(days=1)
        start_last = last_month.replace(day=1, hour=0, minute=0, second=0)
        end_last = last_month

        current_stats = self.analytics_repo.get_revenue_stats(
            start_current, end_current
        )
        previous_stats = self.analytics_repo.get_revenue_stats(start_last, end_last)

        growth = 0.0
        if previous_stats["total_collected"] > 0:
            growth = (
                (current_stats["total_collected"] / previous_stats["total_collected"])
                - 1
            ) * 100

        return {
            "current_month": current_stats,
            "previous_month": previous_stats,
            "revenue_growth_percent": round(growth, 2),
        }

    def get_workshop_dashboard_data(self) -> Dict[str, Any]:
        """
        Provee datos agregados para la visualización del panel de control.
        """
        return {
            "orders_by_status": self.analytics_repo.get_work_order_summary(),
            "technician_performance": self.analytics_repo.get_technician_productivity(),
            "critical_stock_items": self.analytics_repo.get_top_moving_products(
                limit=5
            ),
        }

    def get_audit_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Reporte consolidado para auditoría interna del taller (UTC).
        """
        start = datetime.utcnow() - timedelta(days=days)
        end = datetime.utcnow()

        financials = self.analytics_repo.get_revenue_stats(start, end)
        orders = self.analytics_repo.get_work_order_summary()

        return {
            "period_days": days,
            "financial_summary": financials,
            "operational_status": orders,
        }
