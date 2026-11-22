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

# Serivicios especializados
class ReservaSala(Servicio):
    """Servicio especializado para reserva de salas de trabajo o reuniones."""

    def __init__(self, nombre: str, tarifa_base: float, capacidad: int):
        super().__init__(nombre, tarifa_base)
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ErrorValidacionDatos("capacidad", "La capacidad de la sala debe ser mayor a 0.")
        self.__capacidad: int = capacidad

    @property
    def capacidad(self) -> int:
        return self.__capacidad

    def validar_parametros(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or duracion_horas < 1 or duracion_horas > 12:
            raise ErrorValidacionDatos(
                "duracion_horas",
                "La reserva de sala debe tener una duración entre 1 y 12 horas."
            )

    def _calculo_base_polimorfico(self, duracion_horas: int) -> float:
        self.validar_parametros(duracion_horas)
        recargo_capacidad = 1.15 if self.__capacidad > 10 else 1.0
        return float(self.tarifa_base * duracion_horas * recargo_capacidad)

    def calcular_costo(
        self,
        duracion_horas: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        incluye_equipamiento_av: bool = False
    ) -> float:
        """Calcula el costo total permitiendo parámetros opcionales, descuento e impuesto."""
        if not (0.0 <= descuento_pct < 1.0):
            raise ErrorOperacionReserva("El porcentaje de descuento debe estar entre 0 y 1 (excluyendo 1).")
        if impuesto_pct < 0.0:
            raise ErrorOperacionReserva("El porcentaje de impuesto no puede ser negativo.")

        subtotal = self._calculo_base_polimorfico(duracion_horas)
        if incluye_equipamiento_av:
            subtotal += 25000.0 * duracion_horas

        con_descuento = subtotal * (1.0 - descuento_pct)
        total = con_descuento * (1.0 + impuesto_pct)
        return round(total, 2)

    def obtener_resumen(self) -> str:
        return (
            f"[Sala {self.id}] {self.nombre} | Capacidad: {self.__capacidad} personas | "
            f"Tarifa base/h: ${self.tarifa_base:.2f} | Activo: {self.activo}"
        )


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos."""

    def __init__(self, nombre: str, tarifa_base: float, tipo_equipo: str, stock_disponible: int):
        super().__init__(nombre, tarifa_base)
        if not tipo_equipo or len(tipo_equipo.strip()) < 2:
            raise ErrorValidacionDatos("tipo_equipo", "Debe indicar el tipo de equipo.")
        if not isinstance(stock_disponible, int) or stock_disponible < 0:
            raise ErrorValidacionDatos("stock_disponible", "El stock no puede ser negativo.")

        self.__tipo_equipo: str = tipo_equipo.strip()
        self.__stock_disponible: int = stock_disponible

    @property
    def tipo_equipo(self) -> str:
        return self.__tipo_equipo

    @property
    def stock_disponible(self) -> int:
        return self.__stock_disponible

    def reservar_unidad(self) -> None:
        if self.__stock_disponible <= 0:
            raise ErrorOperacionReserva(f"No hay unidades disponibles para '{self.nombre}'.")
        self.__stock_disponible -= 1

    def liberar_unidad(self) -> None:
        self.__stock_disponible += 1

    def validar_parametros(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or duracion_horas < 2 or duracion_horas > 72:
            raise ErrorValidacionDatos(
                "duracion_horas",
                "El alquiler de equipos requiere entre 2 y 72 horas."
            )

    def _calculo_base_polimorfico(self, duracion_horas: int) -> float:
        self.validar_parametros(duracion_horas)
        factor_extendido = 0.90 if duracion_horas >= 24 else 1.0
        return float(self.tarifa_base * duracion_horas * factor_extendido)

    def calcular_costo(
        self,
        duracion_horas: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        seguro_danos: float = 0.0
    ) -> float:
        """Variante de cálculo con parámetros opcionales de descuento, impuesto y seguro."""
        if not (0.0 <= descuento_pct < 1.0):
            raise ErrorOperacionReserva("Descuento fuera de rango válido.")
        if impuesto_pct < 0.0 or seguro_danos < 0.0:
            raise ErrorOperacionReserva("Impuesto y seguro no pueden ser negativos.")

        subtotal = self._calculo_base_polimorfico(duracion_horas) + seguro_danos
        total = (subtotal * (1.0 - descuento_pct)) * (1.0 + impuesto_pct)
        return round(total, 2)

    def obtener_resumen(self) -> str:
        return (
            f"[Equipo {self.id}] {self.nombre} ({self.__tipo_equipo}) | "
            f"Stock: {self.__stock_disponible} | Tarifa base/h: ${self.tarifa_base:.2f}"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o de ingeniería."""

    def __init__(self, nombre: str, tarifa_base: float, especialidad: str):
        super().__init__(nombre, tarifa_base)
        if not especialidad or len(especialidad.strip()) < 3:
            raise ErrorValidacionDatos("especialidad", "La especialidad es obligatoria.")
        self.__especialidad: str = especialidad.strip()

    @property
    def especialidad(self) -> str:
        return self.__especialidad

    def validar_parametros(self, duracion_horas: int) -> None:
        if not isinstance(duracion_horas, int) or duracion_horas < 1 or duracion_horas > 8:
            raise ErrorValidacionDatos(
                "duracion_horas",
                "Las sesiones de asesoría especializada deben durar entre 1 y 8 horas."
            )

    def _calculo_base_polimorfico(self, duracion_horas: int) -> float:
        self.validar_parametros(duracion_horas)
        return float(self.tarifa_base * duracion_horas)

    def calcular_costo(
        self,
        duracion_horas: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        tarifa_fija_diagnostico: float = 0.0
    ) -> float:
        """Variante de cálculo con diagnóstico opcional, descuento e impuesto."""
        if not (0.0 <= descuento_pct < 1.0):
            raise ErrorOperacionReserva("Descuento inválido para asesoría.")
        if impuesto_pct < 0.0 or tarifa_fija_diagnostico < 0.0:
            raise ErrorOperacionReserva("Valores de impuesto o diagnóstico inválidos.")

        subtotal = self._calculo_base_polimorfico(duracion_horas) + tarifa_fija_diagnostico
        total = (subtotal * (1.0 - descuento_pct)) * (1.0 + impuesto_pct)
        return round(total, 2)

    def obtener_resumen(self) -> str:
        return (
            f"[Asesoría {self.id}] {self.nombre} | Área: {self.__especialidad} | "
            f"Tarifa base/h: ${self.tarifa_base:.2f}"
        )


#Clases de reserva y excepciones
class Reserva(EntidadSistema):
    """Integra Cliente, Servicio, duración, costo calculado y ciclo de vida."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19
    ):
        super().__init__()
        if not isinstance(cliente, Cliente) or not cliente.activo:
            raise ErrorOperacionReserva("El cliente no es válido o está inactivo.")
        if not isinstance(servicio, Servicio) or not servicio.activo:
            raise ErrorOperacionReserva("El servicio no es válido o no está disponible.")

        servicio.validar_parametros(duracion_horas)

        self.__cliente: Cliente = cliente
        self.__servicio: Servicio = servicio
        self.__duracion_horas: int = duracion_horas
        self.__descuento_pct: float = descuento_pct
        self.__impuesto_pct: float = impuesto_pct
        self.__estado: str = "PENDIENTE"
        self.__monto_cobrado: float = 0.0

    @property
    def cliente(self) -> Cliente:
        return self.__cliente

    @property
    def servicio(self) -> Servicio:
        return self.__servicio

    @property
    def duracion_horas(self) -> int:
        return self.__duracion_horas

    @property
    def estado(self) -> str:
        return self.__estado

    @property
    def monto_cobrado(self) -> float:
        return self.__monto_cobrado

    def calcular_total_reserva(self, **kwargs) -> float:
        """Permite calcular el costo usando argumentos opcionales adicionales."""
        descuento = kwargs.get("descuento_pct", self.__descuento_pct)
        impuesto = kwargs.get("impuesto_pct", self.__impuesto_pct)

        if isinstance(self.__servicio, ReservaSala):
            return self.__servicio.calcular_costo(
                self.__duracion_horas,
                descuento_pct=descuento,
                impuesto_pct=impuesto,
                incluye_equipamiento_av=kwargs.get("incluye_equipamiento_av", False)
            )
        if isinstance(self.__servicio, AlquilerEquipo):
            return self.__servicio.calcular_costo(
                self.__duracion_horas,
                descuento_pct=descuento,
                impuesto_pct=impuesto,
                seguro_danos=kwargs.get("seguro_danos", 0.0)
            )
        if isinstance(self.__servicio, AsesoriaEspecializada):
            return self.__servicio.calcular_costo(
                self.__duracion_horas,
                descuento_pct=descuento,
                impuesto_pct=impuesto,
                tarifa_fija_diagnostico=kwargs.get("tarifa_fija_diagnostico", 0.0)
            )
        raise ErrorOperacionReserva("Tipo de servicio no soportado para cálculo de costo.")

    def procesar_y_confirmar(self, **kwargs) -> float:
        """Procesa el pago y confirma la reserva usando try/except/else/finally y encadenamiento."""
        if self.__estado != "PENDIENTE":
            raise ErrorOperacionReserva(
                f"No se puede confirmar la reserva {self.id} en estado '{self.__estado}'."
            )

        unidad_descontada = False
        try:
            total = self.calcular_total_reserva(**kwargs)
            if total <= 0:
                raise ErrorProcesamientoPago("El cálculo del total generó un monto no válido.")

            if isinstance(self.__servicio, AlquilerEquipo):
                self.__servicio.reservar_unidad()
                unidad_descontada = True

            self.__cliente.descontar_saldo(total)
        except ErrorProcesamientoPago as exc_pago:
            if unidad_descontada and isinstance(self.__servicio, AlquilerEquipo):
                self.__servicio.liberar_unidad()
            logger.error(f"Fallo de pago en reserva {self.id}: {exc_pago}")
            raise ErrorOperacionReserva(
                f"No fue posible procesar el pago de la reserva {self.id}."
            ) from exc_pago
        except ErrorSistemaBase as exc_sis:
            if unidad_descontada and isinstance(self.__servicio, AlquilerEquipo):
                self.__servicio.liberar_unidad()
            logger.error(f"Error de sistema al confirmar reserva {self.id}: {exc_sis}")
            raise
        else:
            self.__monto_cobrado = total
            self.__estado = "CONFIRMADA"
            self.__cliente.registrar_reserva_en_historial(self.id)
            logger.info(
                f"Reserva {self.id} CONFIRMADA para cliente {self.__cliente.id} "
                f"por ${self.__monto_cobrado:.2f}."
            )
            return self.__monto_cobrado
        finally:
            logger.info(
                f"Intento de confirmación finalizado para reserva {self.id} "
                f"(estado actual: {self.__estado})."
            )

    def cancelar(self, reembolsar: bool = True) -> None:
        """Cancela la reserva y, si aplica, devuelve el saldo al cliente."""
        if self.__estado == "CANCELADA":
            raise ErrorOperacionReserva(f"La reserva {self.id} ya se encuentra cancelada.")

        try:
            if self.__estado == "CONFIRMADA" and reembolsar and self.__monto_cobrado > 0:
                self.__cliente.saldo = self.__cliente.saldo + self.__monto_cobrado
                self.__monto_cobrado = 0.0
            if isinstance(self.__servicio, AlquilerEquipo) and self.__estado == "CONFIRMADA":
                self.__servicio.liberar_unidad()
        except Exception as exc:
            logger.error(f"Error al cancelar reserva {self.id}: {exc}")
            raise ErrorOperacionReserva(f"Fallo durante la cancelación de {self.id}.") from exc
        else:
            self.__estado = "CANCELADA"
            logger.info(f"Reserva {self.id} CANCELADA.")
        finally:
            logger.info(f"Proceso de cancelación ejecutado para reserva {self.id}.")

    def obtener_resumen(self) -> str:
        return (
            f"[Reserva {self.id}] Estado: {self.__estado} | Cliente: {self.__cliente.nombre} | "
            f"Servicio: {self.__servicio.nombre} ({self.__duracion_horas}h) | "
            f"Total: ${self.__monto_cobrado:.2f}"
        )


#Gestor en memoria
class GestorSoftwareFJ:
    """Administra en memoria clientes, servicios y reservas sin usar base de datos."""

    def __init__(self, nombre_empresa: str = "Software FJ"):
        self.nombre_empresa = nombre_empresa
        self.__clientes: List[Cliente] = []
        self.__servicios: List[Servicio] = []
        self.__reservas: List[Reserva] = []

    def registrar_cliente(self, nombre: str, email: str, telefono: str, saldo: float = 0.0) -> Cliente:
        cliente = Cliente(nombre, email, telefono, saldo)
        self.__clientes.append(cliente)
        logger.info(f"Cliente registrado: {cliente.obtener_resumen()}")
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise ErrorValidacionDatos("servicio", "Objeto de servicio no válido.")
        self.__servicios.append(servicio)
        logger.info(f"Servicio registrado: {servicio.obtener_resumen()}")
        return servicio

    def crear_y_procesar_reserva(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion_horas: int,
        descuento_pct: float = 0.0,
        impuesto_pct: float = 0.19,
        **kwargs
    ) -> Reserva:
        reserva = Reserva(cliente, servicio, duracion_horas, descuento_pct, impuesto_pct)
        self.__reservas.append(reserva)
        reserva.procesar_y_confirmar(**kwargs)
        return reserva

    def listar_resumenes(self) -> None:
        print(f"\n=== ESTADO FINAL EN MEMORIA - {self.nombre_empresa} ===")
        print("--- Clientes ---")
        for c in self.__clientes:
            print(" ", c.obtener_resumen())
        print("--- Servicios ---")
        for s in self.__servicios:
            print(" ", s.obtener_resumen())
        print("--- Reservas ---")
        for r in self.__reservas:
            print(" ", r.obtener_resumen())


def ejecutar_simulacion_software_fj() -> None:
    """Corre varias pruebas del sistema para ver casos válidos y errores."""
    gestor = GestorSoftwareFJ("Software FJ")
    operaciones = [
        # Registrar primer cliente
        ("Op 1 - Registro cliente válido 1", lambda: gestor.registrar_cliente(
            "Laura Gómez", "laura.gomez@softwarefj.co", "+57 310 555 0192", 500000.0
        )),
        # Probar error al registrar cliente con correo mal escrito
        ("Op 2 - Registro cliente inválido (email)", lambda: gestor.registrar_cliente(
            "Carlos Pérez", "correo_invalido", "3001234567", 100000.0
        )),
        # Registrar segundo cliente
        ("Op 3 - Registro cliente válido 2", lambda: gestor.registrar_cliente(
            "Andrés Rojas", "andres.rojas@empresa.com", "3159876543", 50000.0
        )),
        # Crear servicio de sala
        ("Op 4 - Crear servicio Sala", lambda: gestor.registrar_servicio(
            ReservaSala("Sala Ejecutiva Norte", 40000.0, capacidad=12)
        )),
        # Probar error al crear equipo con tarifa negativa
        ("Op 5 - Crear servicio inválido (tarifa)", lambda: gestor.registrar_servicio(
            AlquilerEquipo("Portátil Dev", -15000.0, "Laptop", stock_disponible=3)
        )),
        # Crear servicio de equipo 
        ("Op 6 - Crear servicio Equipo", lambda: gestor.registrar_servicio(
            AlquilerEquipo("Estación Workstation", 20000.0, "Workstation", stock_disponible=1)
        )),
        # Crear servicio de asesoría 
        ("Op 7 - Crear servicio Asesoría", lambda: gestor.registrar_servicio(
            AsesoriaEspecializada("Arquitectura Cloud", 80000.0, "Cloud & DevOps")
        )),
        # Hacer reserva de sala con descuento y equipo audiovisual
        ("Op 8 - Reserva exitosa Sala", lambda: gestor.crear_y_procesar_reserva(
            gestor._GestorSoftwareFJ__clientes[0],
            gestor._GestorSoftwareFJ__servicios[0],
            duracion_horas=3,
            descuento_pct=0.10,
            incluye_equipamiento_av=True
        )),
        # Probar reserva que falla porque Andrés no tiene suficiente saldo
        ("Op 9 - Reserva fallida (saldo insuficiente)", lambda: gestor.crear_y_procesar_reserva(
            gestor._GestorSoftwareFJ__clientes[1],
            gestor._GestorSoftwareFJ__servicios[2],
            duracion_horas=2
        )),
        # Probar reserva que falla por pedir 10 horas en asesoría (el máximo es 8)
        ("Op 10 - Reserva fallida (duración inválida)", lambda: gestor.crear_y_procesar_reserva(
            gestor._GestorSoftwareFJ__clientes[0],
            gestor._GestorSoftwareFJ__servicios[2],
            duracion_horas=10
        )),
        # Hacer reserva de equipo exitosa con seguro
        ("Op 11 - Reserva exitosa Equipo", lambda: gestor.crear_y_procesar_reserva(
            gestor._GestorSoftwareFJ__clientes[0],
            gestor._GestorSoftwareFJ__servicios[1],
            duracion_horas=4,
            seguro_danos=15000.0
        )),
        # Cancelar la primera reserva confirmada y devolver el dinero
        ("Op 12 - Cancelación de reserva confirmada", lambda: (
            gestor._GestorSoftwareFJ__reservas[0].cancelar(reembolsar=True)
        )),
    ]

    for descripcion, accion in operaciones:
        try:
            resultado = accion()
        except ErrorSistemaBase as err:
            print(f"[CONTROLADO] {descripcion} -> {type(err).__name__} ({err.codigo}): {err}")
            logger.warning(f"{descripcion} falló controladamente: {err}")
        except Exception as err:
            print(f"[INESPERADO] {descripcion} -> {type(err).__name__}: {err}")
            logger.error(f"{descripcion} tuvo error inesperado: {err}")
        else:
            print(f"[OK] {descripcion} -> {resultado}")

    gestor.listar_resumenes()


if __name__ == "__main__":
    ejecutar_simulacion_software_fj()



