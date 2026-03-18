from abc import ABC, abstractmethod

class IDatabaseHandler(ABC):
    """
    Interfaz para los manejadores de base de datos.
    Siguiendo el principio de inversión de dependencias de Gravity.
    """
    
    @abstractmethod
    def executeRawQuery(self, query: str, params: tuple = None, fetch: bool = False):
        """
        Ejecuta una consulta SQL pura.
        """
        pass

    @abstractmethod
    def testConnection(self) -> bool:
        """
        Valida que la base de datos sea accesible.
        """
        pass
