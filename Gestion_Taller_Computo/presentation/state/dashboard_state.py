import reflex as rx
from typing import Dict, Any, List

# Importar Managers (Application Layer)
from ...infrastructure.repositories.psycopg_analytics_repository import Psycopg2AnalyticsRepository
from ...application.use_cases.report_manager import ReportManager

class DashboardState(rx.State):
    """
    Estado del Dashboard Administrativo.
    Se comunica con el ReportManager para extraer métricas frescas.
    """
    
    # KPIs resumidos
    summary: Dict[str, Any] = {
        "COMPLETED": 0,
        "RECEIVED": 0,
        "total_orders": 0
    }
    
    financials: Dict[str, Any] = {
        "total_collected": 0.0,
        "revenue_growth": 0.0,
        "last_7_days": []  # Para la gráfica
    }
    
    avg_hours: float = 0.0
    top_incidents: List[Dict[str, Any]] = []
    technicians: List[Dict[str, Any]] = []
    critical_stock: List[Dict[str, Any]] = []
    recent_orders: List[Dict[str, Any]] = []
    
    is_loading: bool = True


    def on_load(self):
        """Inicializa los datos al cargar la página."""
        self.is_loading = True
        return self.fetch_metrics()

    @rx.event
    def fetch_metrics(self):
        """Extrae la información consolidada desde el backend."""
        try:
            # En un entorno productivo estos managers se inyectarían
            repo = Psycopg2AnalyticsRepository()
            mgr = ReportManager(repo)
            
            # 1. Estados de órdenes
            self.summary = mgr.get_workshop_dashboard_data()["orders_by_status"]
            
            # 2. Financieros y TAT
            fin_report = mgr.get_monthly_financial_report()
            dash_data = mgr.get_workshop_dashboard_data()
            curr = fin_report["current_month"]
            
            self.financials = {
                "total_collected": curr["total_collected"],
                "total_invoiced": curr["total_invoiced"],
                "revenue_growth": fin_report["revenue_growth_percent"],
                "last_7_days": dash_data["daily_revenue"][::-1] # Invertir para orden cronológico
            }
            self.avg_hours = round(dash_data.get("avg_repair_time", 0), 1)
            
            # 3. Técnicos, Stock e Incidencias
            self.technicians = dash_data["technician_performance"]
            self.critical_stock = dash_data["critical_stock_items"]
            self.top_incidents = dash_data["top_incidents"]
            self.recent_orders = repo.get_recent_work_orders(limit=10)

            
        except Exception as e:
            print(f"Error cargando dashboard: {e}")
            
        finally:
            self.is_loading = False
