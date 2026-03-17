from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    TECHNICIAN = "technician"
    RECEPTIONIST = "receptionist"
    CUSTOMER = "customer"
