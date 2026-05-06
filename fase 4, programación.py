from abc import ABC, abstractmethod
from datetime import datetime


# ============================================================
# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS
# Empresa: Software FJ
# ============================================================


# ---------------------- LOGS ----------------------

def registrar_log(mensaje):
    """Registra eventos y errores en un archivo de logs."""
    with open("logs_sistema.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"{datetime.now()} - {mensaje}\n")


# ---------------------- EXCEPCIONES PERSONALIZADAS ----------------------

class SistemaError(Exception):
    """Excepción general del sistema."""
    pass


class DatosInvalidosError(SistemaError):
    """Error para datos inválidos."""
    pass


class ServicioNoDisponibleError(SistemaError):
    """Error cuando un servicio no está disponible."""
    pass


class ReservaError(SistemaError):
    """Error en el proceso de reserva."""
    pass


# ---------------------- CLASE ABSTRACTA GENERAL ----------------------

class EntidadSistema(ABC):
    def __init__(self, identificador):
        if not identificador:
            raise DatosInvalidosError("El identificador no puede estar vacío.")
        self._identificador = identificador

    @abstractmethod
    def describir(self):
        pass


# ---------------------- CLASE CLIENTE ----------------------

class Cliente(EntidadSistema):
    def __init__(self, identificador, nombre, documento, correo):
        super().__init__(identificador)

        if not nombre or len(nombre.strip()) < 3:
            raise DatosInvalidosError("El nombre del cliente no es válido.")

        if not documento or not documento.isdigit():
            raise DatosInvalidosError("El documento debe contener solo números.")

        if "@" not in correo or "." not in correo:
            raise DatosInvalidosError("El correo electrónico no es válido.")

        self.__nombre = nombre
        self.__documento = documento
        self.__correo = correo

    def get_nombre(self):
        return self.__nombre

    def get_documento(self):
        return self.__documento

    def get_correo(self):
        return self.__correo

    def describir(self):
        return f"Cliente: {self.__nombre}, Documento: {self.__documento}, Correo: {self.__correo}"


# ---------------------- CLASE ABSTRACTA SERVICIO ----------------------

class Servicio(EntidadSistema):
    def __init__(self, identificador, nombre, tarifa_base, disponible=True):
        super().__init__(identificador)

        if not nombre:
            raise DatosInvalidosError("El nombre del servicio no puede estar vacío.")

        if tarifa_base <= 0:
            raise DatosInvalidosError("La tarifa base debe ser mayor que cero.")

        self.nombre = nombre
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def describir(self):
        pass


# ---------------------- SERVICIOS ESPECIALIZADOS ----------------------

class ReservaSala(Servicio):
    def validar_parametros(self, duracion):
        if duracion <= 0 or duracion > 8:
            raise DatosInvalidosError("La reserva de sala debe estar entre 1 y 8 horas.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        total = subtotal + (subtotal * impuesto) - descuento

        if total < 0:
            raise DatosInvalidosError("El costo calculado no puede ser negativo.")

        return total

    def describir(self):
        return f"Servicio de reserva de sala: {self.nombre}, tarifa por hora: {self.tarifa_base}"


class AlquilerEquipo(Servicio):
    def validar_parametros(self, duracion):
        if duracion <= 0 or duracion > 15:
            raise DatosInvalidosError("El alquiler de equipo debe estar entre 1 y 15 horas.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        total = subtotal + (subtotal * impuesto) - descuento

        if total < 0:
            raise DatosInvalidosError("El costo calculado no puede ser negativo.")

        return total

    def describir(self):
        return f"Servicio de alquiler de equipo: {self.nombre}, tarifa por hora: {self.tarifa_base}"


class AsesoriaEspecializada(Servicio):
    def validar_parametros(self, duracion):
        if duracion <= 0 or duracion > 5:
            raise DatosInvalidosError("La asesoría especializada debe estar entre 1 y 5 horas.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)
        subtotal = self.tarifa_base * duracion
        total = subtotal + (subtotal * impuesto) - descuento

        if total < 0:
            raise DatosInvalidosError("El costo calculado no puede ser negativo.")

        return total

    def describir(self):
        return f"Servicio de asesoría especializada: {self.nombre}, tarifa por hora: {self.tarifa_base}"


# ---------------------- CLASE RESERVA ----------------------

class Reserva(EntidadSistema):
    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)

        if not isinstance(cliente, Cliente):
            raise ReservaError("El cliente asociado a la reserva no es válido.")

        if not isinstance(servicio, Servicio):
            raise ReservaError("El servicio asociado a la reserva no es válido.")

        if not servicio.disponible:
            raise ServicioNoDisponibleError("El servicio seleccionado no está disponible.")

        servicio.validar_parametros(duracion)

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar(self):
        if self.estado == "Cancelada":
            raise ReservaError("No se puede confirmar una reserva cancelada.")

        self.estado = "Confirmada"
        registrar_log(f"Reserva confirmada: {self._identificador}")

    def cancelar(self):
        if self.estado == "Confirmada":
            raise ReservaError("No se puede cancelar una reserva ya confirmada.")

        self.estado = "Cancelada"
        registrar_log(f"Reserva cancelada: {self._identificador}")

    def procesar(self):
        try:
            costo = self.servicio.calcular_costo(self.duracion, impuesto=0.19, descuento=5000)
        except DatosInvalidosError as error:
            raise ReservaError("No fue posible procesar el costo de la reserva.") from error
        else:
            self.confirmar()
            return costo
        finally:
            registrar_log(f"Proceso de reserva finalizado para: {self._identificador}")

    def describir(self):
        return (
            f"Reserva {self._identificador} | Cliente: {self.cliente.get_nombre()} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} horas | Estado: {self.estado}"
        )


# ---------------------- GESTOR DEL SISTEMA ----------------------

class SistemaReservas:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def agregar_cliente(self, cliente):
        self.clientes.append(cliente)
        registrar_log(f"Cliente registrado: {cliente.get_nombre()}")

    def agregar_servicio(self, servicio):
        self.servicios.append(servicio)
        registrar_log(f"Servicio registrado: {servicio.nombre}")

    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)
        registrar_log(f"Reserva registrada: {reserva._identificador}")

    def mostrar_resumen(self):
        print("\n--- RESUMEN DEL SISTEMA ---")
        print(f"Clientes registrados: {len(self.clientes)}")
        print(f"Servicios registrados: {len(self.servicios)}")
        print(f"Reservas registradas: {len(self.reservas)}")


# ---------------------- SIMULACIÓN DE 10 OPERACIONES ----------------------

sistema = SistemaReservas()

print("INICIO DEL SISTEMA SOFTWARE FJ\n")

# Operación 1: Cliente válido
try:
    cliente1 = Cliente("C001", "Nelson Javier Solorzano", "1080292740", "nelson@gmail.com")
except SistemaError as error:
    registrar_log(f"Error operación 1: {error}")
    print("Error operación 1:", error)
else:
    sistema.agregar_cliente(cliente1)
    print("Operación 1 exitosa: cliente válido registrado.")
finally:
    print("Operación 1 finalizada.\n")


# Operación 2: Cliente inválido
try:
    cliente2 = Cliente("C002", "", "abc", "correo_invalido")
except SistemaError as error:
    registrar_log(f"Error operación 2: {error}")
    print("Operación 2 controlada:", error)
finally:
    print("Operación 2 finalizada.\n")


# Operación 3: Servicio sala válido
try:
    servicio1 = ReservaSala("S001", "Sala de reuniones empresarial", 40000)
except SistemaError as error:
    registrar_log(f"Error operación 3: {error}")
    print("Error operación 3:", error)
else:
    sistema.agregar_servicio(servicio1)
    print("Operación 3 exitosa: servicio de sala registrado.")
finally:
    print("Operación 3 finalizada.\n")


# Operación 4: Servicio equipo válido
try:
    servicio2 = AlquilerEquipo("S002", "Computador portátil", 25000)
except SistemaError as error:
    registrar_log(f"Error operación 4: {error}")
    print("Error operación 4:", error)
else:
    sistema.agregar_servicio(servicio2)
    print("Operación 4 exitosa: servicio de equipo registrado.")
finally:
    print("Operación 4 finalizada.\n")


# Operación 5: Servicio asesoría válido
try:
    servicio3 = AsesoriaEspecializada("S003", "Asesoría en desarrollo de software", 80000)
except SistemaError as error:
    registrar_log(f"Error operación 5: {error}")
    print("Error operación 5:", error)
else:
    sistema.agregar_servicio(servicio3)
    print("Operación 5 exitosa: servicio de asesoría registrado.")
finally:
    print("Operación 5 finalizada.\n")


# Operación 6: Servicio inválido
try:
    servicio4 = ReservaSala("S004", "Sala inválida", -10000)
except SistemaError as error:
    registrar_log(f"Error operación 6: {error}")
    print("Operación 6 controlada:", error)
finally:
    print("Operación 6 finalizada.\n")


# Operación 7: Reserva exitosa
try:
    reserva1 = Reserva("R001", cliente1, servicio1, 3)
    costo = reserva1.procesar()
except SistemaError as error:
    registrar_log(f"Error operación 7: {error}")
    print("Error operación 7:", error)
else:
    sistema.agregar_reserva(reserva1)
    print("Operación 7 exitosa:", reserva1.describir())
    print(f"Costo total: ${costo:,.0f}")
finally:
    print("Operación 7 finalizada.\n")


# Operación 8: Reserva con duración inválida
try:
    reserva2 = Reserva("R002", cliente1, servicio1, 12)
except SistemaError as error:
    registrar_log(f"Error operación 8: {error}")
    print("Operación 8 controlada:", error)
finally:
    print("Operación 8 finalizada.\n")


# Operación 9: Reserva con servicio no disponible
try:
    servicio_no_disponible = AlquilerEquipo("S005", "Proyector", 30000, disponible=False)
    reserva3 = Reserva("R003", cliente1, servicio_no_disponible, 2)
except SistemaError as error:
    registrar_log(f"Error operación 9: {error}")
    print("Operación 9 controlada:", error)
finally:
    print("Operación 9 finalizada.\n")


# Operación 10: Encadenamiento de excepciones
try:
    try:
        reserva4 = Reserva("R004", cliente1, servicio3, -2)
    except DatosInvalidosError as error_original:
        raise ReservaError("Error al crear reserva por parámetros inconsistentes.") from error_original
except SistemaError as error:
    registrar_log(f"Error operación 10: {error}")
    print("Operación 10 controlada:", error)
finally:
    print("Operación 10 finalizada.\n")


sistema.mostrar_resumen()

print("\nEl sistema finalizó sin detenerse, incluso ante errores controlados.")
print("Revise el archivo logs_sistema.txt para ver eventos y errores registrados.")



#YO
import tkinter as tk
from tkinter import messagebox

# Sistema
sistema = SistemaReservas()

# Interfz

def limpiar():
    for widget in contenido.winfo_children():
        widget.destroy()

# Clientes
def vista_clientes():
    limpiar()

    tk.Label(contenido, text="Clientes", font=("Helvetica", 16, "bold")).pack(pady=10)

    entry_id = tk.Entry(contenido)
    entry_id.pack()
    entry_id.insert(0, "ID")

    entry_nombre = tk.Entry(contenido)
    entry_nombre.pack()
    entry_nombre.insert(0, "Nombre")

    entry_doc = tk.Entry(contenido)
    entry_doc.pack()
    entry_doc.insert(0, "Documento")

    entry_correo = tk.Entry(contenido)
    entry_correo.pack()
    entry_correo.insert(0, "Correo")

    def registrar():
        try:
            cliente = Cliente(
                entry_id.get(),
                entry_nombre.get(),
                entry_doc.get(),
                entry_correo.get()
            )

            sistema.agregar_cliente(cliente)
            messagebox.showinfo("OK", "Cliente registrado")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(contenido, text="Registrar", command=registrar).pack(pady=10)

# Servicios
def vista_servicios():
    limpiar()

    tk.Label(contenido, text="Servicios", font=("Helvetica", 16, "bold")).pack(pady=10)

    def crear_sala():
        try:
            s = ReservaSala("S" + str(len(sistema.servicios)+1), "Sala", 40000)
            sistema.agregar_servicio(s)
            messagebox.showinfo("OK", "Sala creada")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crear_equipo():
        try:
            s = AlquilerEquipo("S" + str(len(sistema.servicios)+1), "Equipo", 25000)
            sistema.agregar_servicio(s)
            messagebox.showinfo("OK", "Equipo creado")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def crear_asesoria():
        try:
            s = AsesoriaEspecializada("S" + str(len(sistema.servicios)+1), "Asesoría", 80000)
            sistema.agregar_servicio(s)
            messagebox.showinfo("OK", "Asesoría creada")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(contenido, text="Reserva Sala", command=crear_sala).pack(pady=5)
    tk.Button(contenido, text="Alquiler Equipo", command=crear_equipo).pack(pady=5)
    tk.Button(contenido, text="Asesoría", command=crear_asesoria).pack(pady=5)

# Reservas 
def vista_reservas():
    limpiar()

    tk.Label(contenido, text="Reservas", font=("Helvetica", 16, "bold")).pack(pady=10)

    def crear_reserva():
        try:
            if not sistema.clientes or not sistema.servicios:
                raise Exception("Debe haber clientes y servicios")

            r = Reserva(
                "R" + str(len(sistema.reservas)+1),
                sistema.clientes[0],
                sistema.servicios[0],
                2
            )

            costo = r.procesar()
            sistema.agregar_reserva(r)

            messagebox.showinfo("OK", f"Reserva creada\nCosto: {costo}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(contenido, text="Crear Reserva", command=crear_reserva).pack(pady=10)

# Ventana 
ventana = tk.Tk()
ventana.title("Software FJ")
ventana.geometry("400x300")

menu = tk.Frame(ventana, bg="#4243A7", width=200)
menu.pack(side="left", fill="y")

contenido = tk.Frame(ventana, bg="#EFFCFF")
contenido.pack(side="right", expand=True, fill="both")

tk.Button(menu, text="Clientes", command=vista_clientes).pack(fill="x")
tk.Button(menu, text="Servicios", command=vista_servicios).pack(fill="x")
tk.Button(menu, text="Reservas", command=vista_reservas).pack(fill="x")

ventana.mainloop()