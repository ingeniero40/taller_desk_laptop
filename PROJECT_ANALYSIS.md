# Análisis del Proyecto: Gestión_Taller_Computo

## 1. Resumen Ejecutivo

**Sistema de Gestión de Taller de Cómputo** - Aplicación web full-stack para la administración integral de un taller de reparación de computadoras (Desk & Laptop).

### Tecnologías Principales
- **Backend/Frontend**: [Reflex](https://reflex.dev/) (Framework Python Full-Stack)
- **Base de Datos**: PostgreSQL con Psycopg2
- **ORM**: SQLModel
- **Frontend UI**: Tailwind CSS v4 + Radix UI
- **Arquitectura**: Clean Architecture (Domain-Driven Design)

---

## 2. Arquitectura del Sistema

### Estructura de Capas (Clean Architecture)

```
Gestion_Taller_Computo/
├── domain/                    # Capa de Negocio (Inner Circle)
│   ├── entities/              # Entidades del dominio
│   ├── interfaces/            # Contratos/Abstracciones
│   └── value_objects/         # Objetos de valor inmutables
├── application/               # Casos de Uso
│   └── use_cases/             # Lógica de negocio orquestada
├── infrastructure/            # Implementaciones Externas
│   ├── database/               # Acceso a datos (Psycopg2)
│   └── repositories/           # Implementaciones de repositorios
└── presentation/              # Capa de Presentación
    ├── pages/                  # Páginas/Pistas de Reflex
    ├── components/             # Componentes reutilizables
    └── state/                 # Estados de la aplicación
```

### Principios Aplicados

✅ **Separación de Concerns**: Cada capa tiene responsabilidad única
✅ **Inversión de Dependencias**: Depende de abstracciones, no implementaciones
✅ **Single Responsibility**: Clases con una sola razón para cambiar
✅ **Repository Pattern**: Abstrae el acceso a datos

---

## 3. Módulos Funcionales

### 3.1 Gestión de Órdenes de Trabajo
| Característica | Descripción |
|----------------|-------------|
| Estados | RECEIVED → IN_DIAGNOSIS → IN_REPAIR → ON_HOLD → DELIVERED/CANCELLED |
| Prioridades | ALTA, MEDIA, BAJA |
| Auditoría | Historial completo de cambios de estado |
| Ticket | Generación automática TK-YYMMDDHHMMSS |

**Archivos clave**:
- `domain/entities/work_order.py:10` - Entidad principal
- `application/use_cases/work_order_manager.py:10` - Caso de uso

### 3.2 Gestión de Dispositivos
- Registro de equipos con marca, modelo, número de serie
- Asociación con clientes
- Estado físico y accesorios al momento de admisión
- Historial de reparaciones por dispositivo

### 3.3 Gestión de Inventario
- Control de productos/piezas
- Alertas de stock mínimo
- Asociación con proveedores

### 3.4 Facturación
- Generación de cotizaciones
- Control de pagos
- Facturación e invoices

### 3.5 Módulo de Seguimiento (Tracking)
- Consulta pública por número de ticket
- Estados visibles para clientes

### 3.6 Dashboard Administrativo
- KPIs financieros (ingresos, crecimiento)
- Órdenes activas por estado
- Desempeño de técnicos
- Alertas de stock crítico

---

## 4. Patrones de Diseño Implementados

### 4.1 Repository Pattern
```
IWorkOrderRepository (Interface)
    └── Psycopg2WorkOrderRepository (Implementación)
```

### 4.2 Value Objects
```python
WorkOrderStatus  # Estados inmutables de órdenes
OrderPriority     # Prioridades predefinidas
UserRole          # Roles de usuario
```

### 4.3 Connection Pooling
```python
Psycopg2.pool.ThreadedConnectionPool
    └── minconn=1, maxconn=20
```

---

## 5. Modelo de Datos (ER Simplificado)

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│    User     │────<│     Device       │────<│  WorkOrder  │
├─────────────┤     ├──────────────────┤     ├─────────────┤
│ id (PK)     │     │ id (PK)          │     │ id (PK)     │
│ email       │     │ brand            │     │ ticket_number│
│ role        │     │ model            │     │ status      │
│ password    │     │ serial_number    │     │ device_id(FK)│
└─────────────┘     │ customer_id (FK) │     │ technician_id│
                    └──────────────────┘     │ priority    │
                                             │ quoted_price│
┌─────────────┐     ┌──────────────────┐     └─────────────┘
│   Product   │────<│ WorkOrderHistory │
├─────────────┤     ├──────────────────┤
│ id (PK)     │     │ id (PK)          │
│ name        │     │ work_order_id(FK)│
│ stock       │     │ from_status      │
│ min_stock   │     │ to_status        │
│ supplier_id │     │ changed_by_id    │
└─────────────┘     └──────────────────┘
```

---

## 6. Páginas de la Aplicación

| Ruta | Página | Estado | Descripción |
|------|--------|--------|-------------|
| `/` | Dashboard | DashboardState | Panel principal con KPIs |
| `/inventory` | Inventario | InventoryState | Gestión de productos |
| `/billing` | Facturación | BillingState | Cotizaciones y pagos |
| `/orders` | Órdenes | OrderState | Listado de órdenes |
| `/devices` | Dispositivos | DeviceState | Registro de equipos |
| `/suppliers` | Proveedores | SupplierState | Gestión de proveedores |
| `/settings` | Configuración | SettingsState | Ajustes del sistema |
| `/support` | Soporte | - | Página de ayuda |
| `/agenda` | Agenda | AgendaState | Programación |
| `/admission` | Admisión | AdmissionState | Registro de ingresos |
| `/tracking` | Seguimiento | TrackingState | Consulta pública |

---

## 7. Seguridad Implementada

### Autenticación y Autorización
```python
AuthState.check_operations()   # Verifica acceso a operaciones
AuthState.check_admin()        # Verifica rol de administrador
```

### Buenas Prácticas
✅ Parameters en queries (previene SQL Injection)
✅ Environment variables para credenciales
✅ Pool de conexiones para control de recursos
✅ Codificación UTF-8 para caracteres especiales

---

## 8. Scripts de Mantenimiento

| Script | Propósito |
|--------|-----------|
| `migrate_*.py` | Migración de datos |
| `sync_db.py` | Sincronización de base de datos |
| `reinstall_db.py` | Reinstalación de esquema |
| `diagnostic_conexion.py` | Diagnóstico de conexión |
| `test_*_connection.py` | Pruebas de conexión y funcionalidad |

---

## 9. Fortalezas del Proyecto

1. **Arquitectura escalable**: Clean Architecture permite crecer sin deuda técnica
2. **Patrones bien aplicados**: Repository, Value Objects, Use Cases
3. **UI moderna**: Tailwind v4 + Radix con tema cyan
4. **Auditoría completa**: Historial de cambios en órdenes
5. **Pool de conexiones**: Manejo eficiente de recursos DB
6. **Type hints**: Python moderno con tipado

---

## 10. Áreas de Mejora Sugeridas

### Alta Prioridad
1. **Migración a AsyncIO**: Reemplazar psycopg2 por asyncpg para mejor rendimiento
2. **Caché**: Implementar Redis para queries frecuentes
3. **Tests**: Ampliar cobertura de tests unitarios
4. **Validación**: Agregar Pydantic validators en entities

### Media Prioridad
1. **WebSockets**: Actualizaciones en tiempo real de estados
2. **Logging**: Sistema centralizado de logs
3. **API REST**: Exponer endpoints para integraciones
4. **Docker**: Contenerizar la aplicación

### Baja Prioridad
1. **GraphQL**: Alternativa a REST
2. **Multi-tenancy**: Soporte para múltiples talleres
3. **Móvil**: PWA o app móvil

---

## 11. Dependencias Principales

```
reflex>=0.6.0          # Framework full-stack
psycopg2-binary        # Driver PostgreSQL
sqlmodel               # ORM
python-dotenv          # Variables de entorno
```

---

## 12. Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| Archivos Python | ~70 |
| Entidades | 12+ |
| Repositorios | 11 |
| Use Cases | 6 |
| Páginas | 11 |
| Líneas de código (est.) | ~5,000-8,000 |

---

*Generado: 2026-04-02*
