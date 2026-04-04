from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    RECEPTIONIST = "RECEPTIONIST"
    CUSTOMER = "CUSTOMER"
