"""
=============================================================
  SISTEMA INTEGRAL - SOFTWARE FJ
  Interfaz Gráfica con Tkinter
  Gestión de Clientes, Servicios y Reservas
=============================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
from datetime import datetime
from abc import ABC, abstractmethod
from PIL import Image, ImageTk

# ─────────────────────────────────────────────
#  PALETA DE COLORES
# ─────────────────────────────────────────────
COLORS = {
    "bg_dark":      "#0f1117",
    "bg_card":      "#1a1d2e",
    "bg_sidebar":   "#111827",
    "accent":       "#6366f1",        # Indigo
    "accent2":      "#8b5cf6",        # Violet
    "success":      "#10b981",
    "warning":      "#f59e0b",
    "danger":       "#ef4444",
    "text_primary": "#f1f5f9",
    "text_muted":   "#94a3b8",
    "border":       "#2d3748",
    "hover":        "#252840",
    "table_even":   "#161929",
    "table_odd":    "#1a1d2e",
    "badge_cons":   "#1e3a5f",
    "badge_dev":    "#1a3a2e",
    "badge_sop":    "#3a1e1e",
    "badge_cap":    "#2e2a1a",
}

# ─────────────────────────────────────────────
#  LÓGICA DEL DOMINIO (importada del original)
# ─────────────────────────────────────────────
LOG_FILE = "software_fj_errores.log"

def registrar_log(nivel, mensaje):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] [{nivel.upper()}] {mensaje}\n"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(linea)
    except IOError:
        pass

class SoftwareFJError(Exception): pass
class ClienteInvalidoError(SoftwareFJError): pass
class ServicioNoDisponibleError(SoftwareFJError): pass
class ReservaInvalidaError(SoftwareFJError): pass
class CapacidadExcedidaError(SoftwareFJError): pass
class DuplicadoError(SoftwareFJError): pass

class Entidad(ABC):
    _contador_ids = 0
    def __init__(self, nombre):
        Entidad._contador_ids += 1
        self.__id = Entidad._contador_ids
        self.__nombre = nombre
        self.__fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    @property
    def id(self): return self.__id
    @property
    def nombre(self): return self.__nombre
    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip(): raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()
    @property
    def fecha_creacion(self): return self.__fecha_creacion
    @abstractmethod
    def mostrar_info(self): pass
    @abstractmethod
    def validar(self): pass
    def __str__(self): return f"[ID:{self.__id}] {self.__nombre}"

class Cliente(Entidad):
    def __init__(self, nombre, email, telefono, edad):
        super().__init__(nombre)
        self.__email = self.__validar_email(email)
        self.__telefono = self.__validar_telefono(telefono)
        self.__edad = self.__validar_edad(edad)
        self.__reservas = []
        self.__activo = True
    def __validar_email(self, email):
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise ClienteInvalidoError(f"Email inválido: '{email}'.")
        return email.lower().strip()
    def __validar_telefono(self, telefono):
        tel = telefono.replace(" ", "").replace("-", "")
        if not tel.isdigit() or len(tel) < 7 or len(tel) > 15:
            raise ClienteInvalidoError(f"Teléfono inválido: '{telefono}'.")
        return tel
    def __validar_edad(self, edad):
        if not isinstance(edad, int) or edad < 0 or edad > 120:
            raise ClienteInvalidoError(f"Edad inválida: '{edad}'.")
        return edad
    @property
    def email(self): return self.__email
    @property
    def telefono(self): return self.__telefono
    @property
    def edad(self): return self.__edad
    @property
    def activo(self): return self.__activo
    @property
    def reservas(self): return list(self.__reservas)
    def agregar_reserva(self, reserva): self.__reservas.append(reserva)
    def desactivar(self): self.__activo = False
    def validar(self): return bool(self.__email and self.__telefono and self.__activo)
    def mostrar_info(self):
        estado = "Activo" if self.__activo else "Inactivo"
        return (f"CLIENTE | {self} | Email: {self.__email} | "
                f"Tel: {self.__telefono} | Edad: {self.__edad} | "
                f"Estado: {estado} | Reservas: {len(self.__reservas)}")

class Servicio(Entidad, ABC):
    def __init__(self, nombre, precio, capacidad_max):
        super().__init__(nombre)
        self.__precio = self.__validar_precio(precio)
        self.__capacidad_max = self.__validar_capacidad(capacidad_max)
        self.__cupos_usados = 0
        self.__disponible = True
    def __validar_precio(self, precio):
        if not isinstance(precio, (int, float)) or precio <= 0:
            raise ServicioNoDisponibleError(f"Precio inválido: {precio}.")
        return float(precio)
    def __validar_capacidad(self, capacidad):
        if not isinstance(capacidad, int) or capacidad <= 0:
            raise ServicioNoDisponibleError(f"Capacidad inválida: {capacidad}.")
        return capacidad
    @property
    def precio(self): return self.__precio
    @property
    def capacidad_max(self): return self.__capacidad_max
    @property
    def cupos_usados(self): return self.__cupos_usados
    @property
    def cupos_disponibles(self): return self.__capacidad_max - self.__cupos_usados
    @property
    def disponible(self): return self.__disponible and self.__cupos_usados < self.__capacidad_max
    def ocupar_cupo(self):
        if not self.__disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' está desactivado.")
        if self.__cupos_usados >= self.__capacidad_max:
            raise CapacidadExcedidaError(f"Servicio '{self.nombre}' sin cupos disponibles.")
        self.__cupos_usados += 1
    def liberar_cupo(self):
        if self.__cupos_usados > 0: self.__cupos_usados -= 1
    def desactivar(self): self.__disponible = False
    def validar(self): return self.__disponible and self.__precio > 0
    @abstractmethod
    def descripcion_tipo(self): pass
    @abstractmethod
    def calcular_costo(self, cantidad=1): pass
    def mostrar_info(self):
        estado = "Disponible" if self.disponible else "No disponible"
        return (f"SERVICIO [{self.descripcion_tipo()}] | {self} | "
                f"Precio base: ${self.__precio:,.2f} | "
                f"Cupos: {self.__cupos_usados}/{self.__capacidad_max} | {estado}")

class ServicioConsultoria(Servicio):
    def __init__(self, nombre, precio_hora, horas, capacidad_max=5):
        super().__init__(nombre, precio_hora, capacidad_max)
        if horas <= 0: raise ServicioNoDisponibleError("Las horas deben ser positivas.")
        self.__horas = horas
    @property
    def horas(self): return self.__horas
    def descripcion_tipo(self): return "CONSULTORÍA"
    def calcular_costo(self, cantidad=1): return self.precio * self.__horas * cantidad
    def mostrar_info(self): return super().mostrar_info() + f" | Horas: {self.__horas} | Costo: ${self.calcular_costo():,.2f}"

class ServicioDesarrollo(Servicio):
    DESCUENTO_VOLUMEN = 0.10
    def __init__(self, nombre, precio, tecnologia, capacidad_max=10):
        super().__init__(nombre, precio, capacidad_max)
        if not tecnologia or not tecnologia.strip():
            raise ServicioNoDisponibleError("La tecnología no puede estar vacía.")
        self.__tecnologia = tecnologia.strip()
    @property
    def tecnologia(self): return self.__tecnologia
    def descripcion_tipo(self): return "DESARROLLO"
    def calcular_costo(self, cantidad=1):
        costo = self.precio * cantidad
        if cantidad >= 3: costo *= (1 - self.DESCUENTO_VOLUMEN)
        return costo
    def mostrar_info(self): return super().mostrar_info() + f" | Tecnología: {self.__tecnologia}"

class ServicioSoporte(Servicio):
    NIVELES = {"basico": 1.0, "estandar": 1.5, "premium": 2.0}
    def __init__(self, nombre, precio_base, nivel="estandar", capacidad_max=20):
        super().__init__(nombre, precio_base, capacidad_max)
        nivel_lower = nivel.lower()
        if nivel_lower not in self.NIVELES:
            raise ServicioNoDisponibleError(f"Nivel inválido: '{nivel}'.")
        self.__nivel = nivel_lower
    @property
    def nivel(self): return self.__nivel
    def descripcion_tipo(self): return "SOPORTE"
    def calcular_costo(self, cantidad=1): return self.precio * self.NIVELES[self.__nivel] * cantidad
    def mostrar_info(self): return super().mostrar_info() + f" | Nivel: {self.__nivel.capitalize()}"

class ServicioCapacitacion(Servicio):
    def __init__(self, nombre, precio_por_persona, tema, capacidad_max=30):
        super().__init__(nombre, precio_por_persona, capacidad_max)
        if not tema or not tema.strip():
            raise ServicioNoDisponibleError("El tema no puede estar vacío.")
        self.__tema = tema.strip()
    @property
    def tema(self): return self.__tema
    def descripcion_tipo(self): return "CAPACITACIÓN"
    def calcular_costo(self, cantidad=1): return self.precio * cantidad
    def mostrar_info(self): return super().mostrar_info() + f" | Tema: {self.__tema}"

class Reserva(Entidad):
    _reservas_activas = []
    def __init__(self, cliente, servicio, cantidad=1, notas=""):
        if not isinstance(cliente, Cliente): raise ReservaInvalidaError("No es un Cliente válido.")
        if not isinstance(servicio, Servicio): raise ReservaInvalidaError("No es un Servicio válido.")
        if not cliente.activo: raise ReservaInvalidaError(f"El cliente '{cliente.nombre}' está inactivo.")
        if not servicio.disponible: raise ReservaInvalidaError(f"El servicio '{servicio.nombre}' no está disponible.")
        if not isinstance(cantidad, int) or cantidad <= 0: raise ReservaInvalidaError(f"Cantidad inválida: {cantidad}.")
        servicio.ocupar_cupo()
        nombre_reserva = f"Reserva-{cliente.nombre}-{servicio.nombre}"
        super().__init__(nombre_reserva)
        self.__cliente = cliente
        self.__servicio = servicio
        self.__cantidad = cantidad
        self.__costo_total = servicio.calcular_costo(cantidad)
        self.__notas = notas.strip()
        self.__estado = "Activa"
        self.__fecha_reserva = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cliente.agregar_reserva(self)
        Reserva._reservas_activas.append(self)
    @property
    def cliente(self): return self.__cliente
    @property
    def servicio(self): return self.__servicio
    @property
    def cantidad(self): return self.__cantidad
    @property
    def costo_total(self): return self.__costo_total
    @property
    def estado(self): return self.__estado
    @property
    def notas(self): return self.__notas
    @property
    def fecha_reserva(self): return self.__fecha_reserva
    def cancelar(self):
        if self.__estado == "Cancelada": raise ReservaInvalidaError("La reserva ya fue cancelada.")
        self.__estado = "Cancelada"
        self.__servicio.liberar_cupo()
        if self in Reserva._reservas_activas: Reserva._reservas_activas.remove(self)
    def validar(self): return self.__estado == "Activa" and self.__cliente.activo and self.__servicio.disponible
    def mostrar_info(self):
        return (f"RESERVA | {self} | Cliente: {self.__cliente.nombre} | "
                f"Servicio: {self.__servicio.nombre} | Cantidad: {self.__cantidad} | "
                f"Costo: ${self.__costo_total:,.2f} | Estado: {self.__estado}")
    @classmethod
    def total_activas(cls): return len(cls._reservas_activas)

class SistemaFJ:
    def __init__(self):
        self.__clientes = []
        self.__servicios = []
        self.__reservas = []
        registrar_log("INFO", "Sistema Software FJ iniciado.")
    @property
    def clientes(self): return list(self.__clientes)
    @property
    def servicios(self): return list(self.__servicios)
    @property
    def reservas(self): return list(self.__reservas)
    def agregar_cliente(self, nombre, email, telefono, edad):
        for c in self.__clientes:
            if c.email == email.lower().strip():
                raise DuplicadoError(f"Ya existe un cliente con el email '{email}'.")
        cliente = Cliente(nombre, email, telefono, edad)
        self.__clientes.append(cliente)
        registrar_log("INFO", f"Cliente registrado: {cliente.mostrar_info()}")
        return cliente
    def agregar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise ServicioNoDisponibleError("No es un Servicio válido.")
        self.__servicios.append(servicio)
        registrar_log("INFO", f"Servicio registrado: {servicio.mostrar_info()}")
        return True
    def crear_reserva(self, cliente, servicio, cantidad=1, notas=""):
        reserva = Reserva(cliente, servicio, cantidad, notas)
        self.__reservas.append(reserva)
        registrar_log("INFO", f"Reserva creada: {reserva.mostrar_info()}")
        return reserva
    def cancelar_reserva(self, reserva):
        reserva.cancelar()
        registrar_log("INFO", f"Reserva cancelada: {reserva}")
        return True
    def get_estadisticas(self):
        total_ingresos = sum(r.costo_total for r in self.__reservas if r.estado == "Activa")
        activas = sum(1 for r in self.__reservas if r.estado == "Activa")
        canceladas = sum(1 for r in self.__reservas if r.estado == "Cancelada")
        clientes_activos = sum(1 for c in self.__clientes if c.activo)
        servicios_disp = sum(1 for s in self.__servicios if s.disponible)
        return {
            "total_clientes": len(self.__clientes),
            "clientes_activos": clientes_activos,
            "total_servicios": len(self.__servicios),
            "servicios_disponibles": servicios_disp,
            "total_reservas": len(self.__reservas),
            "reservas_activas": activas,
            "reservas_canceladas": canceladas,
            "ingresos_totales": total_ingresos,
        }


# ─────────────────────────────────────────────
#  HELPERS UI
# ─────────────────────────────────────────────
def make_button(parent, text, command, style="primary", width=None):
    bg = {"primary": COLORS["accent"], "success": COLORS["success"],
          "danger": COLORS["danger"], "warning": COLORS["warning"],
          "secondary": COLORS["border"]}.get(style, COLORS["accent"])
    btn = tk.Button(parent, text=text, command=command, bg=bg,
                    fg=COLORS["text_primary"], relief="flat", cursor="hand2",
                    font=("Verdana", 13, "bold"), padx=14, pady=7,
                    activebackground=COLORS["hover"], activeforeground=COLORS["text_primary"],
                    bd=0)
    if width: btn.config(width=width)
    return btn

def make_label(parent, text, size=10, bold=False, color=None, **kwargs):
    weight = "bold" if bold else "normal"
    c = color or COLORS["text_primary"]
    return tk.Label(parent, text=text, font=("Verdana", size, weight),
                    fg=c, bg=kwargs.pop("bg", COLORS["bg_card"]), **kwargs)

def make_entry(parent, var, placeholder="", width=28):
    frame = tk.Frame(parent, bg=COLORS["border"], pady=1, padx=1)
    entry = tk.Entry(frame, textvariable=var, width=width,
                     font=("Verdana", 10), bg=COLORS["bg_black"],
                     fg=COLORS["text_primary"], relief="flat",
                     insertbackground=COLORS["text_primary"], bd=4,
                     highlightthickness=0)
    entry.pack()
    if placeholder and not var.get():
        entry.insert(0, placeholder)
        entry.config(fg=COLORS["text_muted"])
        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=COLORS["text_primary"])
        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORS["text_muted"])
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
    return frame, entry


# ─────────────────────────────────────────────
#  VENTANA PRINCIPAL
# ─────────────────────────────────────────────
class AppFJ(tk.Tk):
    def __init__(self):
        super().__init__()

        #Icono 
        self.logo_icon = tk.PhotoImage(file="logo.png.png")
        self.iconphoto(True, self.logo_icon)

        self.sistema = SistemaFJ()
        self._cargar_datos_demo()
        self.title("Software FJ — Sistema Integral de Gestión")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(bg=COLORS["bg_dark"])
        self._build_ui()
        self.current_page = None
        self._show_panelDeControl()


    def _cargar_datos_demo(self):
        """Pre-carga datos de ejemplo para visualización inmediata."""
        try:
            srv1 = ServicioConsultoria("Consultoría Estratégica", 150000, 8, 3)
            srv2 = ServicioDesarrollo("Desarrollo Web Full-Stack", 2500000, "Python/React", 5)
            srv3 = ServicioSoporte("Soporte TI Premium", 80000, "premium", 4)
            srv4 = ServicioCapacitacion("Capacitación Python OOP", 120000, "POO en Python", 6)
            for s in [srv1, srv2, srv3, srv4]:
                self.sistema.agregar_servicio(s)
            c1 = self.sistema.agregar_cliente("Ana Torres",  "ana.torres@gmail.com",  "3001234567", 32)
            c2 = self.sistema.agregar_cliente("Luis Méndez", "luis.mendez@empresa.co","3119876543", 45)
            c3 = self.sistema.agregar_cliente("Sofía Reyes", "sofia.reyes@gmail.com",  "6012345678", 27)
            c4 = self.sistema.agregar_cliente("Carlos Ruiz", "carlos.ruiz@corp.com",  "3205551234", 38)
            c5 = self.sistema.agregar_cliente("Luz Navarro", "luznavarro@gmail.com", "3225493832",21)
            c6 = self.sistema.agregar_cliente("Maria Rodriguez", "maria@gmail.com", "3135656765",40)
            self.sistema.crear_reserva(c1, srv1, 1, "Cliente prioritario")
            self.sistema.crear_reserva(c2, srv2, 3, "Proyecto e-commerce")
            self.sistema.crear_reserva(c3, srv3, 1, "Primer modulo")
            self.sistema.crear_reserva(c4, srv4, 2, "Grupo empresarial")
            self.sistema.crear_reserva(c1, srv3, 1, "Segundo módulo")
            self.sistema.crear_reserva(c5, srv1, 1, "Segundo módulo")
            self.sistema.crear_reserva(c6, srv4, 1, "Primer módulo") 
        except Exception:
            pass

    def _build_ui(self):
        # ─── Sidebar ───
        self.sidebar = tk.Frame(self, bg=COLORS["bg_sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)


        # Logo
        img = Image.open("logo.png.png")
        img =img.resize((100, 100))
        logo=ImageTk.PhotoImage(img)

        label_logo=tk.Label (self.sidebar, image=logo,bg=COLORS["bg_sidebar"])
        label_logo.image =logo
        label_logo.pack(pady=10)
        tk.Label( self.sidebar, text="Software FJ", font=("Verdana", 13, "bold"), fg=COLORS["text_primary"], bg=COLORS["bg_sidebar"]).pack()


        # Nav buttons
        self.nav_buttons = {}
        nav_items = [
            ("Panel De Control", "▦  Panel De Control", self._show_panelDeControl),
            ("clientes",  "👤  Clientes", self._show_clientes),
            ("servicios", "🛠  Servicios", self._show_servicios),
            ("reservas",  "📅  Reservas", self._show_reservas),
        ]
        for key, label, cmd in nav_items:
            btn = tk.Button(self.sidebar, text=label, command=cmd,
                            bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
                            relief="flat", anchor="w", padx=20, pady=10,
                            font=("Verdana", 10), cursor="hand2",
                            activebackground=COLORS["hover"],
                            activeforeground=COLORS["text_primary"], bd=0)
            btn.pack(fill="x")
            self.nav_buttons[key] = btn

        # Footer sidebar
        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=8, side="bottom")
        tk.Label(self.sidebar, text="v1.0  •  POO Python",
                 font=("Verdana", 8), fg=COLORS["text_muted"],
                 bg=COLORS["bg_sidebar"]).pack(side="bottom", pady=8)

        # ─── Content area ───
        self.content = tk.Frame(self, bg=COLORS["bg_dark"])
        self.content.pack(side="left", fill="both", expand=True)

    def _set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg=COLORS["hover"], fg=COLORS["text_primary"],
                           font=("Verdana", 10, "bold"))
            else:
                btn.config(bg=COLORS["bg_sidebar"], fg=COLORS["text_muted"],
                           font=("Verdana", 10))

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ─── Panel De Control ───
    def _show_panelDeControl(self):
        self._clear_content()
        self._set_active_nav("Panel de Control")
        stats = self.sistema.get_estadisticas()

        # Header
        hdr = tk.Frame(self.content, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=28, pady=(24, 8))
        tk.Label(hdr, text="Panel de Control", font=("Verdana", 20, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")
        tk.Label(hdr, text=datetime.now().strftime("  %d %b %Y"),
                 font=("Verdana", 10), fg=COLORS["text_muted"],
                 bg=COLORS["bg_dark"]).pack(side="left", pady=6)

        # KPI Cards
        kpi_frame = tk.Frame(self.content, bg=COLORS["bg_dark"])
        kpi_frame.pack(fill="x", padx=28, pady=8)

        kpis = [
            ("Clientes",     stats["total_clientes"],    COLORS["accent"],  "👤"),
            ("Servicios",    stats["total_servicios"],   COLORS["accent2"], "🛠"),
            ("Reservas Act.",stats["reservas_activas"],  COLORS["success"], "📅"),
            ("Ingresos",     f"${stats['ingresos_totales']:,.0f}", COLORS["warning"], "💰"),
        ]
        for i, (label, value, color, icon) in enumerate(kpis):
            card = tk.Frame(kpi_frame, bg=COLORS["bg_card"], padx=18, pady=16)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            kpi_frame.columnconfigure(i, weight=1)
            tk.Label(card, text=icon, font=("Verdana", 22),
                     fg=color, bg=COLORS["bg_card"]).pack(anchor="w")
            tk.Label(card, text=str(value), font=("Verdana", 24, "bold"),
                     fg=color, bg=COLORS["bg_card"]).pack(anchor="w")
            tk.Label(card, text=label, font=("Verdana", 9),
                     fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w")

        # Charts row
        charts = tk.Frame(self.content, bg=COLORS["bg_dark"])
        charts.pack(fill="both", expand=True, padx=28, pady=12)
        charts.columnconfigure(0, weight=3)
        charts.columnconfigure(1, weight=2)

        # Bar chart — ingresos por servicio
        bar_card = tk.Frame(charts, bg=COLORS["bg_card"])
        bar_card.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        tk.Label(bar_card, text="Ingresos por Servicio",
                 font=("Verdana", 11, "bold"), fg=COLORS["text_primary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(14, 4))

        canvas = tk.Canvas(bar_card, bg=COLORS["bg_card"], height=200,
                           highlightthickness=0)
        canvas.pack(fill="x", padx=16, pady=(4, 14))

        # Aggregate incomes per service type
        ing_por_tipo = {}
        for r in self.sistema.reservas:
            if r.estado == "Activa":
                tipo = r.servicio.descripcion_tipo()
                ing_por_tipo[tipo] = ing_por_tipo.get(tipo, 0) + r.costo_total

        colores_barra = {
            "CONSULTORÍA": COLORS["accent"],
            "DESARROLLO":  COLORS["success"],
            "SOPORTE":     COLORS["warning"],
            "CAPACITACIÓN":COLORS["accent2"],
        }
        canvas.update_idletasks()
        self.after(50, lambda: self._draw_bars(canvas, ing_por_tipo, colores_barra))

        # Pie chart — estado reservas
        pie_card = tk.Frame(charts, bg=COLORS["bg_card"])
        pie_card.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        tk.Label(pie_card, text="Estado de Reservas",
                 font=("Verdana", 11, "bold"), fg=COLORS["text_primary"],
                 bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(14, 4))

        pie_canvas = tk.Canvas(pie_card, bg=COLORS["bg_card"], height=180,
                               highlightthickness=0)
        pie_canvas.pack(fill="both", expand=True, padx=16, pady=(4, 8))
        self.after(50, lambda: self._draw_pie(pie_canvas, stats))

        # Leyenda pie
        leg = tk.Frame(pie_card, bg=COLORS["bg_card"])
        leg.pack(anchor="w", padx=16, pady=(0, 14))
        for label, color in [("Activas", COLORS["success"]),
                              ("Canceladas", COLORS["danger"])]:
            row = tk.Frame(leg, bg=COLORS["bg_card"])
            row.pack(side="left", padx=6)
            tk.Label(row, text="■", fg=color, bg=COLORS["bg_card"],
                     font=("Verdana", 12)).pack(side="left")
            tk.Label(row, text=label, fg=COLORS["text_muted"],
                     bg=COLORS["bg_card"], font=("Verdana", 9)).pack(side="left")

    def _draw_bars(self, canvas, data, colors):
        canvas.update_idletasks()
        W = canvas.winfo_width() or 400
        H = 190
        if not data:
            canvas.create_text(W//2, H//2, text="Sin datos",
                               fill=COLORS["text_muted"], font=("Verdana", 10))
            return
        max_val = max(data.values()) or 1
        bar_w = int((W - 40) / (len(data) * 1.6))
        gap = int(bar_w * 0.6)
        x = 20
        for tipo, val in data.items():
            bar_h = int((val / max_val) * (H - 50))
            y0 = H - 30 - bar_h
            color = colors.get(tipo, COLORS["accent"])
            canvas.create_rectangle(x, y0, x + bar_w, H - 30,
                                    fill=color, outline="", width=0)
            canvas.create_text(x + bar_w//2, H - 18,
                               text=tipo[:3], fill=COLORS["text_muted"],
                               font=("Verdana", 8))
            canvas.create_text(x + bar_w//2, y0 - 10,
                               text=f"${val/1_000_000:.1f}M" if val >= 1_000_000 else f"${val/1000:.0f}K",
                               fill=COLORS["text_primary"], font=("Verdana", 8, "bold"))
            x += bar_w + gap

    def _draw_pie(self, canvas, stats):
        canvas.update_idletasks()
        W = canvas.winfo_width() or 200
        H = 175
        cx, cy, r = W // 2, H // 2, min(W, H) // 2 - 15
        total = stats["total_reservas"]
        if total == 0:
            canvas.create_text(cx, cy, text="Sin reservas",
                               fill=COLORS["text_muted"], font=("Verdana", 10))
            return
        activas = stats["reservas_activas"]
        canceladas = stats["reservas_canceladas"]
        slices = [(activas, COLORS["success"]), (canceladas, COLORS["danger"])]
        start = -90
        for val, color in slices:
            ext = (val / total) * 360
            canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                              start=start, extent=ext, fill=color, outline=COLORS["bg_card"], width=2)
            start += ext

        # Center label
        canvas.create_oval(cx-35, cy-35, cx+35, cy+35, fill=COLORS["bg_card"], outline="")
        canvas.create_text(cx, cy - 8, text=str(total),
                           fill=COLORS["text_primary"], font=("Verdana", 16, "bold"))
        canvas.create_text(cx, cy + 10, text="total",
                           fill=COLORS["text_muted"], font=("Verdana", 8))

    # ─── CLIENTES ───
    def _show_clientes(self):
        self._clear_content()
        self._set_active_nav("clientes")
        self._page_header("👤  Gestión de Clientes",
                          lambda: self._modal_nuevo_cliente())

        # Tabla
        table_frame = tk.Frame(self.content, bg=COLORS["bg_card"])
        table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        cols = ("ID", "Nombre", "Email", "Teléfono", "Edad", "Estado", "Reservas")
        tree = self._make_treeview(table_frame, cols)

        for c in self.sistema.clientes:
            estado = "✅ Activo" if c.activo else "❌ Inactivo"
            tree.insert("", "end", values=(
                c.id, c.nombre, c.email, c.telefono,
                c.edad, estado, len(c.reservas)
            ))

        # Action bar debajo
        action_bar = tk.Frame(self.content, bg=COLORS["bg_dark"])
        action_bar.pack(fill="x", padx=28, pady=(0, 16))
        make_button(action_bar, "⊕ Nuevo Cliente",
                    lambda: self._modal_nuevo_cliente()).pack(side="left", padx=4)
        make_button(action_bar, "✕ Desactivar",
                    lambda: self._desactivar_cliente(tree), "danger").pack(side="left", padx=4)

    def _modal_nuevo_cliente(self):
        win = self._make_modal("Nuevo Cliente", 420, 400)
        v_nom = tk.StringVar()
        v_email = tk.StringVar()
        v_tel = tk.StringVar()
        v_edad = tk.StringVar()

        fields = [
            ("Nombre completo", v_nom, "Ej: María García"),
            ("Email",           v_email, "usuario@dominio.com"),
            ("Teléfono",        v_tel, "3001234567"),
            ("Edad",            v_edad, "25"),
        ]
        for label, var, ph in fields:
            tk.Label(win, text=label, font=("Verdana", 9),
                     fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w", padx=24, pady=(10, 0))
            f, _ = make_entry(win, var, ph, 38)
            f.pack(padx=24, fill="x")

        def guardar():
            try:
                edad = int(v_edad.get())
                self.sistema.agregar_cliente(v_nom.get(), v_email.get(), v_tel.get(), edad)
                messagebox.showinfo("Éxito", f"Cliente '{v_nom.get()}' registrado.", parent=win)
                win.destroy()
                self._show_clientes()
            except (ClienteInvalidoError, DuplicadoError, ValueError) as e:
                messagebox.showerror("Error", str(e), parent=win)

        make_button(win, "Guardar Cliente", guardar).pack(pady=20)

    def _desactivar_cliente(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un cliente.")
            return
        vals = tree.item(sel[0])["values"]
        cid = vals[0]
        cliente = next((c for c in self.sistema.clientes if c.id == cid), None)
        if cliente:
            if not cliente.activo:
                messagebox.showinfo("Info", "El cliente ya está inactivo.")
                return
            if messagebox.askyesno("Confirmar", f"¿Desactivar a '{cliente.nombre}'?"):
                cliente.desactivar()
                self._show_clientes()

    # ─── SERVICIOS ───
    def _show_servicios(self):
        self._clear_content()
        self._set_active_nav("servicios")
        self._page_header("🛠  Gestión de Servicios",
                          lambda: self._modal_nuevo_servicio())

        table_frame = tk.Frame(self.content, bg=COLORS["bg_card"])
        table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        cols = ("ID", "Nombre", "Tipo", "Precio Base", "Cupos Disp.", "Cap. Máx.", "Estado")
        tree = self._make_treeview(table_frame, cols)

        tipo_color = {
            "CONSULTORÍA": "#d51945e5", "DESARROLLO": "#1078b9",
            "SOPORTE": "#cd481c", "CAPACITACIÓN": "#239c05"
        }
        for s in self.sistema.servicios:
            estado = "✅ Disponible" if s.disponible else "❌ Inactivo"
            tree.insert("", "end", values=(
                s.id, s.nombre, s.descripcion_tipo(),
                f"${s.precio:,.0f}", s.cupos_disponibles, s.capacidad_max, estado
            ))

        action_bar = tk.Frame(self.content, bg=COLORS["bg_dark"])
        action_bar.pack(fill="x", padx=28, pady=(0, 16))
        make_button(action_bar, "⊕ Nuevo Servicio",
                    lambda: self._modal_nuevo_servicio()).pack(side="left", padx=4)
        make_button(action_bar, "✕ Desactivar",
                    lambda: self._desactivar_servicio(tree), "danger").pack(side="left", padx=4)

    def _modal_nuevo_servicio(self):
        win = self._make_modal("Nuevo Servicio", 460, 520)
        tipo_var = tk.StringVar(value="CONSULTORÍA")
        v_nom = tk.StringVar()
        v_precio = tk.StringVar()
        v_cap = tk.StringVar(value="5")
        v_extra1 = tk.StringVar()
        v_extra2 = tk.StringVar()

        tk.Label(win, text="Tipo de Servicio", font=("Segoe UI", 9),
                 fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w", padx=24, pady=(14, 0))
        combo = ttk.Combobox(win, textvariable=tipo_var, state="readonly",
                             values=["CONSULTORÍA", "DESARROLLO", "SOPORTE", "CAPACITACIÓN"],
                             font=("Verdana", 11), width=36)
        combo.pack(padx=24, anchor="w")

        for label, var, ph in [
            ("Nombre del Servicio", v_nom, "Ej: Consultoría Estratégica"),
            ("Precio Base ($)",     v_precio, "150000"),
            ("Capacidad Máxima",    v_cap, "5"),
        ]:
            tk.Label(win, text=label, font=("Verdana", 9),
                     fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w", padx=24, pady=(10, 0))
            f, _ = make_entry(win, var, ph, 38)
            f.pack(padx=24, fill="x")

        # Dynamic extra field
        extra1_lbl = tk.Label(win, text="Horas (consultoría)", font=("Verdana", 9),
                              fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        extra1_lbl.pack(anchor="w", padx=24, pady=(10, 0))
        f_extra1, _ = make_entry(win, v_extra1, "8", 38)
        f_extra1.pack(padx=24, fill="x")

        extra2_lbl = tk.Label(win, text="Tecnología / Nivel / Tema", font=("Verdana", 9),
                              fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        extra2_lbl.pack(anchor="w", padx=24, pady=(10, 0))
        f_extra2, _ = make_entry(win, v_extra2, "Python/React / premium / POO", 38)
        f_extra2.pack(padx=24, fill="x")

        def actualizar_labels(*_):
            tipo = tipo_var.get()
            labels = {
                "CONSULTORÍA": ( "—","Horas de Consultoría"),
                "DESARROLLO":  ("—", "Tecnología (ej: Python/React)"),
                "SOPORTE":     ("—", "Nivel (basico/estandar/premium)"),
                "CAPACITACIÓN":("—", "Tema del curso"),
            }
            l1, l2 = labels.get(tipo, ("—", "—"))
            extra1_lbl.config(text=l1)
            extra2_lbl.config(text=l2)
        tipo_var.trace_add("write", actualizar_labels)

        def guardar():
            try:
                nombre = v_nom.get().strip()
                precio = float(v_precio.get())
                cap = int(v_cap.get())
                tipo = tipo_var.get()
                if tipo == "CONSULTORÍA":
                    horas = int(v_extra1.get())
                    srv = ServicioConsultoria(nombre, precio, horas, cap)
                elif tipo == "DESARROLLO":
                    srv = ServicioDesarrollo(nombre, precio, v_extra2.get(), cap)
                elif tipo == "SOPORTE":
                    srv = ServicioSoporte(nombre, precio, v_extra2.get(), cap)
                else:
                    srv = ServicioCapacitacion(nombre, precio, v_extra2.get(), cap)
                self.sistema.agregar_servicio(srv)
                messagebox.showinfo("Éxito", f"Servicio '{nombre}' registrado.", parent=win)
                win.destroy()
                self._show_servicios()
            except (ServicioNoDisponibleError, ValueError) as e:
                messagebox.showerror("Error", str(e), parent=win)

        make_button(win, "Guardar Servicio", guardar).pack(pady=18)

    def _desactivar_servicio(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un servicio")
            return
        vals = tree.item(sel[0])["values"]
        sid = vals[0]
        srv = next((s for s in self.sistema.servicios if s.id == sid), None)
        if srv:
            if not srv.disponible:
                messagebox.showinfo("Info", "El servicio ya está inactivo.")
                return
            if messagebox.askyesno("Confirmar", f"¿Desactivar '{srv.nombre}'?"):
                srv.desactivar()
                self._show_servicios()

    # ─── RESERVAS ───
    def _show_reservas(self):
        self._clear_content()
        self._set_active_nav("reservas")
        self._page_header("📅  Gestión de Reservas",
                          lambda: self._modal_nueva_reserva())

        table_frame = tk.Frame(self.content, bg=COLORS["bg_card"])
        table_frame.pack(fill="both", expand=True, padx=28, pady=(0, 8))

        cols = ("ID", "Cliente", "Servicio", "Tipo", "Cant.", "Costo", "Estado", "Fecha")
        tree = self._make_treeview(table_frame, cols)

        for r in self.sistema.reservas:
            tree.insert("", "end", values=(
                r.id, r.cliente.nombre, r.servicio.nombre,
                r.servicio.descripcion_tipo(), r.cantidad,
                f"${r.costo_total:,.0f}", r.estado,
                r.fecha_reserva[:10]
            ))

        action_bar = tk.Frame(self.content, bg=COLORS["bg_dark"])
        action_bar.pack(fill="x", padx=28, pady=(0, 16))
        make_button(action_bar, "⊕ Nueva Reserva",
                    lambda: self._modal_nueva_reserva()).pack(side="left", padx=4)
        make_button(action_bar, "✕ Cancelar Reserva",
                    lambda: self._cancelar_reserva(tree), "danger").pack(side="left", padx=4)

        # Summary bar
        stats = self.sistema.get_estadisticas()
        summary = tk.Frame(self.content, bg=COLORS["bg_card"])
        summary.pack(fill="x", padx=28, pady=(0, 20))
        for text, color in [
            (f"  Activas: {stats['reservas_activas']}", COLORS["success"]),
            (f"  Canceladas: {stats['reservas_canceladas']}", COLORS["danger"]),
            (f"  Ingresos: ${stats['ingresos_totales']:,.0f}", COLORS["warning"]),
        ]:
            tk.Label(summary, text=text, font=("Verdana", 10, "bold"),
                     fg=color, bg=COLORS["bg_card"], padx=14, pady=8).pack(side="left")

    def _modal_nueva_reserva(self):
        clientes = [c for c in self.sistema.clientes if c.activo]
        servicios = [s for s in self.sistema.servicios if s.disponible]
        if not clientes or not servicios:
            messagebox.showwarning("Sin datos",
                                   "Necesitas clientes activos y servicios disponibles.")
            return

        win = self._make_modal("Nueva Reserva", 440, 400)
        c_names = [f"[{c.id}] {c.nombre}" for c in clientes]
        s_names = [f"[{s.id}] {s.nombre}" for s in servicios]

        v_cliente = tk.StringVar(value=c_names[0])
        v_servicio = tk.StringVar(value=s_names[0])
        v_cantidad = tk.StringVar(value="1")
        v_notas = tk.StringVar()

        for label, var, opts in [
            ("Cliente", v_cliente, c_names),
            ("Servicio", v_servicio, s_names),
        ]:
            tk.Label(win, text=label, font=("Verdana", 9),
                     fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w", padx=24, pady=(14, 0))
            ttk.Combobox(win, textvariable=var, state="readonly", values=opts,
                         font=("Verdana", 10), width=40).pack(padx=24, anchor="w")

        for label, var, ph in [
            ("Cantidad", v_cantidad, "1"),
            ("Notas (opcional)", v_notas, "Observaciones..."),
        ]:
            tk.Label(win, text=label, font=("Verdana", 9),
                     fg=COLORS["text_muted"], bg=COLORS["bg_card"]).pack(anchor="w", padx=24, pady=(10, 0))
            f, _ = make_entry(win, var, ph, 40)
            f.pack(padx=24, fill="x")

        def guardar():
            try:
                cid = int(v_cliente.get().split("]")[0][1:])
                sid = int(v_servicio.get().split("]")[0][1:])
                cliente = next(c for c in self.sistema.clientes if c.id == cid)
                servicio = next(s for s in self.sistema.servicios if s.id == sid)
                cantidad = int(v_cantidad.get())
                self.sistema.crear_reserva(cliente, servicio, cantidad, v_notas.get())
                messagebox.showinfo("Éxito", "Reserva creada exitosamente.", parent=win)
                win.destroy()
                self._show_reservas()
            except (ReservaInvalidaError, CapacidadExcedidaError, ValueError) as e:
                messagebox.showerror("Error", str(e), parent=win)

        make_button(win, "Crear Reserva", guardar).pack(pady=20)

    def _cancelar_reserva(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona una reserva.")
            return
        vals = tree.item(sel[0])["values"]
        rid = vals[0]
        reserva = next((r for r in self.sistema.reservas if r.id == rid), None)
        if reserva:
            if reserva.estado == "Cancelada":
                messagebox.showinfo("Info", "La reserva ya está cancelada.")
                return
            if messagebox.askyesno("Confirmar", f"¿Cancelar reserva #{rid}?"):
                try:
                    self.sistema.cancelar_reserva(reserva)
                    self._show_reservas()
                except ReservaInvalidaError as e:
                    messagebox.showerror("Error", str(e))

    # ─── HELPERS ───
    def _page_header(self, title, new_cmd=None):
        hdr = tk.Frame(self.content, bg=COLORS["bg_dark"])
        hdr.pack(fill="x", padx=28, pady=(24, 16))
        tk.Label(hdr, text=title, font=("Verdana", 18, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_dark"]).pack(side="left")

    def _make_treeview(self, parent, cols):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("FJ.Treeview",
                         background=COLORS["bg_card"],
                         foreground=COLORS["text_primary"],
                         fieldbackground=COLORS["bg_card"],
                         rowheight=32,
                         borderwidth=0,
                         font=("Verdana", 10))
        style.configure("FJ.Treeview.Heading",
                         background=COLORS["bg_sidebar"],
                         foreground=COLORS["text_muted"],
                         relief="flat",
                         font=("Verdana", 10, "bold"))
        style.map("FJ.Treeview",
                  background=[("selected", COLORS["hover"])],
                  foreground=[("selected", COLORS["text_primary"])])

        frame = tk.Frame(parent, bg=COLORS["bg_card"])
        frame.pack(fill="both", expand=True, padx=16, pady=12)

        sb = ttk.Scrollbar(frame, orient="vertical")
        sb.pack(side="right", fill="y")

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             style="FJ.Treeview", yscrollcommand=sb.set)
        sb.config(command=tree.yview)

        for col in cols:
            w = 100
            if col in ("Nombre", "Email", "Servicio", "Cliente"): w = 160
            if col in ("ID", "Cant."): w = 50
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor="center" if col in ("ID", "Cant.") else "w")

        tree.pack(fill="both", expand=True)
        return tree

    def _make_modal(self, title, w=400, h=380):
        win = tk.Toplevel(self)
        win.title(title)
        win.geometry(f"{w}x{h}")
        win.configure(bg=COLORS["bg_card"])
        win.resizable(False, False)
        win.grab_set()
        win.transient(self)
        # Header
        tk.Label(win, text=title, font=("Verdana", 14, "bold"),
                 fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(
            anchor="w", padx=24, pady=(20, 4))
        tk.Frame(win, bg=COLORS["border"], height=1).pack(fill="x", padx=24, pady=(0, 8))
        return win


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = AppFJ()
    app.mainloop()
