# 1. MÓDULO DE REGISTRO DE EVENTOS Y ERRORES (LOGS)
#==================================================================
class GestorLogs:
    """Administra la escritura de eventos y excepciones en un archivo plano."""
    def __init__(self, archivo_log: str = "sistema_fj.log"):
        self.__archivo_log = archivo_log
        def registrar(self, nivel: str, mensaje: str, detalle_error: Exception = None):
            marca_tiempo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            linea = f"[{marca_tiempo}] [{nivel.upper()}] {mensaje}"
            if detalle_error is not None:
                linea += f" | Excepción: {type(detalle_error).__name__}: {detalle_error}"
                if detalle_error.__cause__:
                    linea += f" (Causa original: {type(detalle_error.__cause__).__name__}: {detalle_error.__cause__})"
                    linea += "\n"
                    try:
                        with open(self.__archivo_log, "a", encoding="utf-8") as archivo: archivo.write(linea)