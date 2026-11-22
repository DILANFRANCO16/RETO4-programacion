# 1. CONFIGURACION DEL SISTEMA DE LOGS
#==================================================================
logging.basicConfig(
    filename="sistema_reservas.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    logger = logging.getLogger("SistemaIntegralPOO")

# 2. JERARQUIA DE EXCEPCIONES PERSONALIZADAS 
#====================================================================
    class ErrorSistemaBase(exception):
        """Excepción raíz para todos los errores controlados del sistema."""
        def_init_(self, mensaje:str, codigo: int = 500):
           super()._init_(mensaje)
           self.codigo = codigo
           self.timestamp = datetime.now()

     class ErrorValidacionDatos(ErrorSistemaBase):
         """Lanzada cuando un atributo no cumple las reglas de negocio."""
          def __init__(self, campo: str, mensaje: str):
            super().__init__(f"Error en '{campo}': {mensaje}", codigo=400)
             self.campo = campo
     class ErrorOperacionReserva(ErrorSistemaBase):
        """Lanzada cuando ocurre un fallo en el ciclo de vida de una reserva."""
         def __init__(self, mensaje: str):
            super().__init__(mensaje, codigo=409)
      class ErrorProcesamientoPago(ErrorSistemaBase):
         """Lanzada cuando falla la transacción o cálculo financiero."""

         def __init__(self, mensaje: str):
             super().__init__(mensaje, codigo=402)

#3. CLASE ABSTRACTA BASE DEL SISTEMA 
#====================================================================
class EntidadSistema(ABC):
    """Clase abstracta raíz que define identidad y auditoría para las entidades."""

     def __init__(self):
         self.__id: str = str(uuid.uuid4())[:8].upper()
         self.__fecha_creacion: datetime = datetime.now()
         self.__activo: bool = True

     @property
     def id(self) -> str:
         return self.__id

     @property
     def fecha_creacion(self) -> datetime:
         return self.__fecha_creacion

     @property
      def activo(self) -> bool:
          return self.__activo

     def desactivar(self) -> None:
         self.__activo = False
         logger.info(f"Entidad {self.__id} ({self.__class__.__name__}) desactivada.")



             
    
        

    
