import reflex as rx
from typing import List, Dict, Any, Optional
import uuid

from ...infrastructure.repositories.psycopg_device_repository import Psycopg2DeviceRepository
from ...infrastructure.repositories.psycopg_user_repository import Psycopg2UserRepository
from ...infrastructure.repositories.psycopg_work_order_repository import Psycopg2WorkOrderRepository
from ...application.use_cases.device_manager import DeviceManager
from ...application.use_cases.user_manager import UserManager
from ...application.use_cases.work_order_manager import WorkOrderManager
from ...domain.entities.user import User
from ...domain.entities.device import Device
from ...domain.value_objects.user_role import UserRole
from ...domain.value_objects.order_priority import OrderPriority


class AdmissionState(rx.State):
    """
    Estado del Flujo de Admisión de Equipos (Wizard multi-paso).
    
    Pasos:
        1 - Identificar o registrar cliente
        2 - Capturar detalles del equipo
        3 - Descripción del problema + prioridad
        4 - Confirmación y generación automática de OT
    """

    # ── Control del Wizard ────────────────────────────────────────────────
    current_step: int = 1
    total_steps: int = 4
    is_loading: bool = False
    success_message: str = ""
    error_message: str = ""

    # ── Resultado final ───────────────────────────────────────────────────
    generated_ticket: str = ""
    admission_complete: bool = False

    # ── PASO 1: Cliente ──────────────────────────────────────────────────
    customer_search: str = ""
    customers_found: List[Dict[str, Any]] = []
    selected_customer_id: str = ""
    selected_customer_name: str = ""

    # Si el cliente no existe => registrar nuevo
    new_customer_mode: bool = False
    new_customer_name: str = ""
    new_customer_email: str = ""
    new_customer_phone: str = ""

    # ── PASO 2: Dispositivo ───────────────────────────────────────────────
    device_type: str = "Laptop"
    device_brand: str = ""
    device_model: str = ""
    device_serial: str = ""
    physical_condition: str = "Bueno"
    accessories: str = ""
    has_existing_device: bool = False
    customer_devices: List[Dict[str, str]] = []
    selected_device_id: str = ""
    entry_images_urls: List[str] = []

    @rx.var
    def device_options(self) -> List[str]:
        """Retorna solo los nombres/labels de los dispositivos para el rx.select."""
        return [d["label"] for d in self.customer_devices]


    # ── PASO 3: Problema ─────────────────────────────────────────────────
    problem_description: str = ""
    problem_priority: str = OrderPriority.MEDIUM.value

    # ── PASO 4: Resumen ───────────────────────────────────────────────────
    @rx.var
    def step_label(self) -> str:
        labels = {
            1: "Identificar Cliente",
            2: "Datos del Equipo",
            3: "Descripción del Problema",
            4: "Confirmación",
        }
        return labels.get(self.current_step, "")

    @rx.var
    def step_progress(self) -> int:
        return int((self.current_step / self.total_steps) * 100)

    @rx.var
    def can_go_next_step1(self) -> bool:
        if self.new_customer_mode:
            return bool(self.new_customer_name and self.new_customer_email)
        return bool(self.selected_customer_id)

    @rx.var
    def can_go_next_step2(self) -> bool:
        if self.has_existing_device:
            return bool(self.selected_device_id)
        return bool(self.device_brand and self.device_model and self.device_serial)

    @rx.var
    def can_go_next_step3(self) -> bool:
        return bool(self.problem_description)

    # ── Navegación ────────────────────────────────────────────────────────

    @rx.event
    def next_step(self):
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.error_message = ""

    @rx.event
    def prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.error_message = ""

    @rx.event
    def reset_wizard(self):
        """Reinicia el wizard para una nueva admisión."""
        self.current_step = 1
        self.customer_search = ""
        self.customers_found = []
        self.selected_customer_id = ""
        self.selected_customer_name = ""
        self.new_customer_mode = False
        self.new_customer_name = ""
        self.new_customer_email = ""
        self.new_customer_phone = ""
        self.device_type = "Laptop"
        self.device_brand = ""
        self.device_model = ""
        self.device_serial = ""
        self.physical_condition = "Bueno"
        self.accessories = ""
        self.has_existing_device = False
        self.customer_devices = []
        self.selected_device_id = ""
        self.problem_description = ""
        self.problem_priority = OrderPriority.MEDIUM.value
        self.generated_ticket = ""
        self.admission_complete = False
        self.success_message = ""
        self.error_message = ""
        self.entry_images_urls = []

    @rx.event
    async def handle_entry_image_upload(self, files: List[rx.UploadFile]):
        """Sube y registra imágenes del equipo al ingresar."""
        import os
        upload_dir = os.path.join("assets", "uploads", "check_in")
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        for file in files:
            upload_data = await file.read()
            # Nombre de archivo único: uuid_original.ext
            ext = os.path.splitext(file.filename)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            outfile = os.path.join(upload_dir, filename)
            with open(outfile, "wb") as f:
                f.write(upload_data)
            
            # Guardamos la ruta relativa para el frontend/DB
            self.entry_images_urls.append(f"/uploads/check_in/{filename}")

    # ── PASO 1 Eventos ───────────────────────────────────────────────────

    @rx.event
    def set_customer_search(self, val: str):
        self.customer_search = val

    @rx.event
    def search_customer(self):
        """Busca clientes por nombre o correo."""
        if not self.customer_search.strip():
            self.customers_found = []
            return
        try:
            repo = Psycopg2UserRepository()
            mgr = UserManager(repo)
            all_users = mgr.get_all_users()
            q = self.customer_search.lower()
            self.customers_found = [
                {"id": str(u.id), "name": u.full_name, "email": u.email, "phone": u.phone or ""}
                for u in all_users
                if u.role == UserRole.CUSTOMER and u.is_active
                and (q in u.full_name.lower() or q in u.email.lower())
            ]
            if not self.customers_found:
                self.error_message = "No se encontraron clientes. Puedes registrar uno nuevo."
        except Exception as e:
            self.error_message = f"Error en búsqueda: {e}"

    @rx.event
    def select_customer(self, cid: str, cname: str):
        """Selecciona un cliente existente y carga sus dispositivos."""
        self.selected_customer_id = cid
        self.selected_customer_name = cname
        self.new_customer_mode = False
        self.error_message = ""
        self._load_customer_devices(cid)

    def _load_customer_devices(self, customer_id: str):
        try:
            repo = Psycopg2DeviceRepository()
            devices = repo.findByCustomerId(uuid.UUID(customer_id))
            self.customer_devices = [
                {"id": str(d.id), "label": f"{d.brand} {d.model} — {d.serial_number}"}
                for d in devices
            ]
        except Exception as e:
            self.customer_devices = []

    @rx.event
    def enable_new_customer(self):
        self.new_customer_mode = True
        self.selected_customer_id = ""
        self.selected_customer_name = ""
        self.customers_found = []
        self.error_message = ""

    @rx.event
    def set_new_customer_name(self, val: str):
        self.new_customer_name = val

    @rx.event
    def set_new_customer_email(self, val: str):
        self.new_customer_email = val

    @rx.event
    def set_new_customer_phone(self, val: str):
        self.new_customer_phone = val

    # ── PASO 2 Eventos ───────────────────────────────────────────────────

    @rx.event
    def set_device_type(self, val: str):
        self.device_type = val

    @rx.event
    def set_device_brand(self, val: str):
        self.device_brand = val

    @rx.event
    def set_device_model(self, val: str):
        self.device_model = val

    @rx.event
    def set_device_serial(self, val: str):
        self.device_serial = val

    @rx.event
    def set_physical_condition(self, val: str):
        self.physical_condition = val

    @rx.event
    def set_accessories(self, val: str):
        self.accessories = val

    @rx.event
    def toggle_existing_device(self, val: bool):
        self.has_existing_device = val

    @rx.event
    def set_selected_device(self, val: str):
        # El select devuelve el label, buscamos su ID correspondiente
        for d in self.customer_devices:
            if d["label"] == val:
                self.selected_device_id = d["id"]
                break


    # ── PASO 3 Eventos ───────────────────────────────────────────────────

    @rx.event
    def set_problem_description(self, val: str):
        self.problem_description = val

    @rx.event
    def set_problem_priority(self, val: str):
        self.problem_priority = val

    # ── PASO 4: Finalizar Admisión ────────────────────────────────────────

    @rx.event
    def finalize_admission(self):
        """
        Ejecuta el flujo completo de admisión:
        1. Registra cliente si es nuevo
        2. Registra dispositivo si es nuevo
        3. Genera la Orden de Trabajo automáticamente
        """
        self.is_loading = True
        self.error_message = ""
        try:
            user_repo = Psycopg2UserRepository()
            user_mgr = UserManager(user_repo)

            device_repo = Psycopg2DeviceRepository()
            dev_mgr = DeviceManager(device_repo)

            order_repo = Psycopg2WorkOrderRepository()
            order_mgr = WorkOrderManager(order_repo)

            # 1. Registrar cliente nuevo si aplica
            customer_id_str = self.selected_customer_id
            if self.new_customer_mode:
                new_user = user_mgr.create_user(
                    username=self.new_customer_email.split("@")[0],
                    email=self.new_customer_email,
                    password_hash="welcome2024",
                    full_name=self.new_customer_name,
                    role=UserRole.CUSTOMER,
                )
                customer_id_str = str(new_user.id)

            customer_uuid = uuid.UUID(customer_id_str)

            # 2. Registrar dispositivo nuevo si aplica
            device_uuid = None
            if self.has_existing_device and self.selected_device_id:
                device_uuid = uuid.UUID(self.selected_device_id)
            else:
                new_device = dev_mgr.register_device(
                    brand=self.device_brand,
                    model=self.device_model,
                    serial_number=self.device_serial,
                    customer_id=customer_uuid,
                )
                # Actualizar campos adicionales de admisión
                new_device.physical_condition = self.physical_condition
                new_device.accessories = self.accessories
                new_device.device_type = self.device_type
                device_repo.update(new_device)
                device_uuid = new_device.id

            # 3. Crear la Orden de Trabajo automáticamente
            order = order_mgr.open_order(
                device_id=device_uuid,
                diagnostic_notes=self.problem_description,
            )
            # Aplicar prioridad
            from ...domain.value_objects.order_priority import OrderPriority
            order.priority = OrderPriority(self.problem_priority)
            
            # Guardar evidencia fotográfica (Contexto 9)
            if self.entry_images_urls:
                order.entry_images = ";".join(self.entry_images_urls)
                
            order_repo.update(order)

            self.generated_ticket = order.ticket_number
            self.admission_complete = True
            self.success_message = f"¡Admisión completada! Orden de trabajo: {order.ticket_number}"

        except Exception as e:
            self.error_message = f"Error al procesar la admisión: {str(e)}"
        finally:
            self.is_loading = False
