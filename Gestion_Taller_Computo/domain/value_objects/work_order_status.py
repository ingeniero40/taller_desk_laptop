from enum import Enum

class WorkOrderStatus(str, Enum):
    RECEIVED = "received"
    IN_DIAGNOSIS = "in_diagnosis"
    IN_REPAIR = "in_repair"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    DELIVERED = "delivered"
