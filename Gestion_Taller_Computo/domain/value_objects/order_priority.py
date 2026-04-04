from enum import Enum


class OrderPriority(str, Enum):
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    CRITICAL = "Crítica"
