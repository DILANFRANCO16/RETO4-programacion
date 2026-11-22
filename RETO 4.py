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

     @abstractmethod
     def obtener_resumen(self) -> str:
         """Método obligatorio para representar el estado de cualquier entidad."""
          pass

# 4.CLASE CLIENTE 
#===================================================================================
class Cliente(EntidadSistema):
    """Representa un cliente con datos encapsulados y gestión interna de historial."""

    def __init__(self, nombre: str, email: str, telefono: str, saldo: float = 0.0):
        super().__init__()
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        self.saldo = saldo
        self.__historial_reservas: List[str] = []

       @property
       def nombre(self) -> str:
           return self.__nombre

       @nombre.setter
       def nombre(self, valor: str) -> None:
           if not isinstance(valor, str) or len(valor.strip()) < 3:
               raise ErrorValidacionDatos("nombre", "Debe tener al menos 3 caracteres.")
            self.__nombre = valor.strip().title()

       @property
        def email(self) -> str:
            return self.__email

       @email.setter
       def email(self, valor: str) -> None:
           patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
           if not isinstance(valor, str) or not re.match(patron, valor):
               raise ErrorValidacionDatos("email", f"Formato de correo inválido: '{valor}'.")
           self.__email = valor.lower().strip()

        @property
        def telefono(self) -> str:
            return self.__telefono

        @telefono.setter
        def telefono(self, valor: str) -> None:
            limpio = re.sub(r"[\s\-\+]", "", str(valor))
            if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
                raise ErrorValidacionDatos("telefono", "Debe contener entre 7 y 15 dígitos.")
            self.__telefono = valor.strip()

        @property
        def saldo(self) -> float:
            return self.__saldo

        @saldo.setter
        def saldo(self, valor: float) -> None:
            if not isinstance(valor, (int, float)) or valor < 0:
                raise ErrorValidacionDatos("saldo", "El saldo no puede ser negativo.")
                self.__saldo = float(valor)

        @property
        def historial_reservas(self) -> List[str]:
            """Devuelve una copia para evitar mutaciones externas de la lista interna."""
            return list(self.__historial_reservas)

        def registrar_reserva_en_historial(self, id_reserva: str) -> None:
            if id_reserva not in self.__historial_reservas:
                self.__historial_reservas.append(id_reserva)

        def descontar_saldo(self, monto: float) -> None:
            if monto <= 0:
                raise ErrorProcesamientoPago("El monto a descontar debe ser mayor a cero.")
            if monto > self.__saldo:
                raise ErrorProcesamientoPago(
                    f"Saldo insuficiente (${self.__saldo:.2f}) para cubrir ${monto:.2f}."
                )
            self.__saldo -= monto

         def obtener_resumen(self) -> str:
             return (
                 f"[Cliente {self.id}] {self.nombre} | Email: {self.email} | "
                 f"Saldo: ${self.saldo:.2f} | Reservas: {len(self.__historial_reservas)}"
             )

#5. CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
#============================================================================================
class Servicio(EntidadSistema, ABC):
    """Clase abstracta que modela cualquier servicio contratado en el sistema."""

    def __init__(self, nombre: str, tarifa_base: float):
        super().__init__()
        if not nombre or len(nombre.strip()) < 3:
            raise ErrorValidacionDatos("nombre_servicio", "Nombre demasiado corto.")
        if tarifa_base <= 0:
            raise ErrorValidacionDatos("tarifa_base", "La tarifa debe ser positiva.")

        self.__nombre: str = nombre.strip()
        self.__tarifa_base: float = float(tarifa_base)

        @property
        def nombre(self) -> str:
            return self.__nombre

        @property
        def tarifa_base(self) -> float:
            return self.__tarifa_base

        @abstractmethod
        def validar_parametros(self, duracion_horas: int) -> None:
            """Valida restricciones específicas de tiempo o recursos del servicio."""
            pass

        @abstractmethod
        def _calculo_base_polimorfico(self, duracion_horas: int) -> float:
            """Cálculo interno específico según las reglas de cada servicio derivado."""
            pass

        @abstractmethod
        def _calculo_base_polimorfico(self, duracion_horas: int) -> float:
            """Cálculo interno específico según las reglas de cada servicio derivado."""
            pass


