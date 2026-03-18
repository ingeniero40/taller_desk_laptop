import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Añadir el raíz del proyecto para importar
sys.path.append(os.getcwd())

from Gestion_Taller_Computo.infrastructure.repositories.psycopg_analytics_repository import Psycopg2AnalyticsRepository
from Gestion_Taller_Computo.application.use_cases.report_manager import ReportManager

def test_reporting_module():
    """
    Test para validar la extracción de reportes y analíticas.
    """
    print("--- 📊 Probando Módulo de Reportes ---")
    load_dotenv()
    
    # 1. Setup
    analytics_repo = Psycopg2AnalyticsRepository()
    report_mgr = ReportManager(analytics_repo)
    
    try:
        # A. Datos para Dashboard
        print("A. Generando datos para Dashboard...")
        dash_data = report_mgr.get_workshop_dashboard_data()
        
        print(f"✅ Total de órdenes recibidas: {dash_data['orders_by_status'].get('RECEIVED', 0)}")
        print(f"✅ Total de órdenes completadas: {dash_data['orders_by_status'].get('COMPLETED', 0)}")
        
        # B. Productividad por Técnico
        print("B. Analizando productividad por técnico...")
        techs = dash_data['technician_performance']
        if techs:
            for t in techs:
                print(f"   👤 {t['technician']} | Estado: {t['status']} | Cantidad: {t['order_count']}")
        else:
            print("   ⚠️ No se encontraron técnicos con órdenes asignadas.")
            
        # C. Reporte Financiero Mensual
        print("C. Generando reporte financiero mensual...")
        financial_report = report_mgr.get_monthly_financial_report()
        curr_month = financial_report["current_month"]
        
        print(f"✅ Recaudado el mes de hoy: ${curr_month['total_collected']:.2f}")
        print(f"✅ Facturado (total proyectado): ${curr_month['total_invoiced']:.2f}")
        print(f"📈 Crecimiento vs mes anterior: {financial_report['revenue_growth_percent']}%")
        
        # D. Stock Crítico
        print("D. Buscando productos críticos (vistos en inventario)...")
        low_stock = dash_data['critical_stock_items']
        if low_stock:
            print(f"   ⚠️  Alerta: {len(low_stock)} productos con bajo stock.")
            for p in low_stock[:3]: # Mostrar top 3
                print(f"   - {p['name']} (SKU: {p['sku']}) | Stock Actual: {p['stock']}")
        else:
            print("   ✅ Stock saludable.")
            
    except Exception as e:
        print(f"❌ Fallo en el módulo de reportes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reporting_module()
