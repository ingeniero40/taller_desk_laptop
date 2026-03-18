from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime

class IAnalyticsRepository(ABC):
    """
    Interfaz para la extracción de métricas y reportes agregados.
    """
    
    @abstractmethod
    def get_revenue_stats(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Obtiene estadísticas de ingresos en un periodo."""
        pass
    
    @abstractmethod
    def get_technician_productivity(self) -> List[Dict[str, Any]]:
        """Métricas de desempeño por técnico."""
        pass
    
    @abstractmethod
    def get_work_order_summary(self) -> Dict[str, Any]:
        """Resumen de estados de las órdenes actuales."""
        pass
    
    @abstractmethod
    def get_top_moving_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Productos más utilizados o vendidos."""
        pass
