import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from groq import Groq
import threading
import time
import os
import json
import cv2
from datetime import datetime
import base64
from tkinter import filedialog
import mysql.connector
import fitz          # pymupdf
from docx import Document as DocxDocument
import openpyxl

def recurso_path(relative_path):
    import sys
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

API_KEY = ""  # ← Pon aquí tu clave de GroqCloud

# ─────────────────────────────────────────────
#  CONFIGURACIÓN MySQL
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host":     "",  # ← Tu host va aqui
    "port":     ,    # ← Tu puerto va aqui
    "user":     "",  # ← Tu usuario MySQL
    "password": "",  # ← Tu contraseña MySQL
    "database": ""   # ← Nombre de tu base de datos
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def crear_incidencia_db(usuario, problema, urgencia="media"):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO incidencias (usuario, problema, urgencia) VALUES (%s, %s, %s)",
            (usuario, problema, urgencia)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] Error creando incidencia: {e}")
        return False
client = Groq(api_key=API_KEY)
MODELO_TEXTO  = "llama-3.3-70b-versatile"
MODELO_VISION = "meta-llama/llama-4-scout-17b-16e-instruct"
MODELO = MODELO_TEXTO

SYSTEM_PROMPT = """Eres DigiHelp, asistente de soporte técnico IT. Tu única función es resolver problemas técnicos.

INSTRUCCIÓN PRINCIPAL: SIEMPRE saluda al principio y haz nada mas que un saludo. Luego responde directamente al problema.

EJEMPLOS DE CÓMO DEBES RESPONDER:

Usuario: "la impresora no me va"
TÚ: "No te preocupes, vamos a arreglarlo juntos. Sigue estos pasos:
1. Apaga la impresora — busca el botón de encendido y mantenlo pulsado hasta que se apague.
2. Desenchufa el cable de la luz — el que va a la pared.
3. Espera 30 segundos.
4. Vuelve a enchufarlo y enciende la impresora.
¿Ha vuelto a funcionar?"

Usuario: "no tengo internet"
TÚ: "Vamos a solucionarlo paso a paso:
1. Mira el router — esa cajita con lucecitas que da el wifi. ¿Las luces están encendidas?
2. Si alguna luz está roja o apagada, apaga el router (botón detrás) y vuelve a encenderlo.
3. Espera 1 minuto y prueba de nuevo.
¿Ha funcionado?"

REGLAS:
- En la primera conversacion empieza con un saludo (¡Hola!, ¡Buenos días!, ¡Buenas tardes!, etc.).
- Responde directamente al problema sin rodeos.
- Si hay una imagen analízala describiendo qué ves.
- Si la pregunta no es de IT (recetas, noticias...) responde: "Solo puedo ayudarte con problemas técnicos. ¿Tienes alguna incidencia IT?"
- Usa lenguaje muy simple, como si hablaras con alguien que nunca ha usado un ordenador.
- Pasos cortos, máximo 2 líneas cada uno.
- Siempre pregunta al final si ha funcionado."""

C = {
    "bg_app":        "#F0F2F5",
    "sidebar_bg":    "#1B2A4A",
    "sidebar_hover": "#243557",
    "sidebar_btn":   "#2C3E6B",
    "accent":        "#2563EB",
    "accent_dark":   "#1D4ED8",
    "bubble_user":   "#2563EB",
    "bubble_ia":     "#FFFFFF",
    "text_dark":     "#1E293B",
    "text_light":    "#FFFFFF",
    "text_muted":    "#94A3B8",
    "input_bg":      "#FFFFFF",
    "border":        "#CBD5E1",
    "card":          "#FFFFFF",
    "header_bg":     "#FFFFFF",
    "video_bg":      "#0F172A",
}

class BurbujaChat(ctk.CTkFrame):
    def __init__(self, parent, texto, es_ia, avatar_ia=None, timestamp="", imagen_ruta=None):
        super().__init__(parent, fg_color="transparent")
        self.pack(fill="x", padx=16, pady=6)
        if es_ia:
            self._burbuja_ia(texto, avatar_ia, timestamp)
        else:
            self._burbuja_usuario(texto, timestamp, imagen_ruta)

    def _burbuja_ia(self, texto, avatar, timestamp):
        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", anchor="w")
        avatar_frame = ctk.CTkFrame(fila, width=36, height=36, corner_radius=18, fg_color="transparent")
        avatar_frame.pack(side="left", anchor="n", padx=(0, 10), pady=2)
        avatar_frame.pack_propagate(False)
        if avatar:
            ctk.CTkLabel(avatar_frame, image=avatar, text="").pack(expand=True)
        else:
            # Intentar cargar avatar.png como fallback
            try:
                img = Image.open(recurso_path("avatar.png")).convert("RGBA")
                s = min(img.size)
                img = img.crop(((img.width-s)//2, (img.height-s)//2, (img.width+s)//2, (img.height+s)//2))
                img = img.resize((36, 36), Image.LANCZOS)
                mask = Image.new("L", (36, 36), 0)
                ImageDraw.Draw(mask).ellipse((0, 0, 36, 36), fill=255)
                out = Image.new("RGBA", (36, 36), (0,0,0,0))
                out.paste(img, (0, 0), mask)
                ctk_img = ctk.CTkImage(light_image=out, dark_image=out, size=(36, 36))
                ctk.CTkLabel(avatar_frame, image=ctk_img, text="").pack(expand=True)
                avatar_frame._img_ref = ctk_img
            except Exception:
                ctk.CTkLabel(avatar_frame, text="D", font=("Georgia", 14, "bold"), text_color="white").pack(expand=True)
        contenido = ctk.CTkFrame(fila, fg_color="transparent")
        contenido.pack(side="left", fill="x", expand=True)
        cabecera = ctk.CTkFrame(contenido, fg_color="transparent")
        cabecera.pack(fill="x", anchor="w")
        ctk.CTkLabel(cabecera, text="DigiHelp AI", font=("Helvetica", 11, "bold"), text_color=C["accent"]).pack(side="left")
        ctk.CTkLabel(cabecera, text=f"  {timestamp}", font=("Helvetica", 10), text_color=C["text_muted"]).pack(side="left")
        burbuja = ctk.CTkFrame(contenido, fg_color=C["bubble_ia"], corner_radius=12, border_width=1, border_color=C["border"])
        burbuja.pack(fill="x", anchor="w", pady=(4, 0))
        self.lbl = ctk.CTkLabel(burbuja, text=texto, font=("Helvetica", 13), text_color=C["text_dark"],
                                wraplength=520, justify="left", padx=14, pady=12, anchor="w")
        self.lbl.pack(fill="x")

    def _burbuja_usuario(self, texto, timestamp, imagen_ruta=None):
        fila = ctk.CTkFrame(self, fg_color="transparent")
        fila.pack(fill="x", anchor="e")
        contenido = ctk.CTkFrame(fila, fg_color="transparent")
        contenido.pack(side="right")

        cabecera = ctk.CTkFrame(contenido, fg_color="transparent")
        cabecera.pack(fill="x", anchor="e")
        ctk.CTkLabel(cabecera, text=f"{timestamp}  ", font=("Helvetica", 10), text_color=C["text_muted"]).pack(side="right")
        ctk.CTkLabel(cabecera, text="Tú", font=("Helvetica", 11, "bold"), text_color=C["text_muted"]).pack(side="right")

        burbuja = ctk.CTkFrame(contenido, fg_color=C["bubble_user"], corner_radius=12)
        burbuja.pack(anchor="e", pady=(4, 0))

        # Miniatura de imagen si existe
        if imagen_ruta and os.path.exists(imagen_ruta):
            try:
                img = Image.open(imagen_ruta).convert("RGB")
                img.thumbnail((220, 160), Image.LANCZOS)
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                lbl_img = ctk.CTkLabel(burbuja, image=ctk_img, text="", cursor="hand2")
                lbl_img.image = ctk_img
                lbl_img.pack(padx=10, pady=(10, 4))
            except Exception:
                pass

        # Texto (solo si hay algo que mostrar)
        texto_limpio = texto.replace("  🖼️", "").strip()
        if texto_limpio:
            self.lbl = ctk.CTkLabel(burbuja, text=texto_limpio, font=("Helvetica", 13),
                                    text_color=C["text_light"], wraplength=400,
                                    justify="right", padx=14, pady=10)
            self.lbl.pack()
        else:
            self.lbl = ctk.CTkLabel(burbuja, text="", font=("Helvetica", 1))
            self.lbl.pack()

    def actualizar_texto(self, texto):
        self.lbl.configure(text=texto)


class DigiHelpApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        self.title("DigiHelp AI — Soporte IT Corporativo")
        self.geometry("1200x800")
        self.minsize(900, 600)
        self.configure(fg_color=C["bg_app"])

        # Icono de la ventana y barra de tareas
        try:
            ruta_ico = recurso_path("avatar.ico")
            if os.path.exists(ruta_ico):
                self.iconbitmap(ruta_ico)
        except Exception:
            pass

        self._imagen_adjunta = None  # (ruta, base64_data, media_type)
        self._doc_adjunto = None      # (ruta, texto_extraido)
        self._intentos = 0            # Contador de intentos de resolución
        self._problema_inicial = None # Primer mensaje del usuario
        self._esperando_confirmacion = False  # Esperando si se resolvió
        self.historial = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.chat_id = f"chat_{int(time.time())}"
        self._chat_titulo = None  # Se genera en el primer mensaje y se reutiliza
        self._chat_archivo = None  # Nombre del archivo JSON de este chat
        self.sidebar_visible = True
        self.video_cap = None
        self.video_activo = False
        self.welcome = None
        self._video_delay = 0.033

        os.makedirs("conversaciones", exist_ok=True)
        os.makedirs("videos", exist_ok=True)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._construir_sidebar()
        self._construir_main()
        self.cargar_sidebar()

    def _construir_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=270, corner_radius=0, fg_color=C["sidebar_bg"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(2, weight=1)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=72)
        logo_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(20, 0))
        logo_frame.grid_propagate(False)
        icono = ctk.CTkFrame(logo_frame, width=38, height=38, corner_radius=10, fg_color=C["accent"])
        icono.pack(side="left", padx=(0, 10))
        icono.pack_propagate(False)
        try:
            img = Image.open(recurso_path("avatar.png")).convert("RGBA")
            s = min(img.size)
            img = img.crop(((img.width-s)//2, (img.height-s)//2, (img.width+s)//2, (img.height+s)//2))
            img = img.resize((38, 38), Image.LANCZOS)
            mask = Image.new("L", (38, 38), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 38, 38), fill=255)
            out = Image.new("RGBA", (38, 38), (0,0,0,0))
            out.paste(img, (0, 0), mask)
            ctk_logo = ctk.CTkImage(light_image=out, dark_image=out, size=(38, 38))
            ctk.CTkLabel(icono, image=ctk_logo, text="").pack(expand=True)
            icono._img_ref = ctk_logo
        except Exception:
            ctk.CTkLabel(icono, text="D", font=("Georgia", 18, "bold"), text_color="white").pack(expand=True)
        ctk.CTkLabel(logo_frame, text="DigiHelp AI", font=("Helvetica", 17, "bold"), text_color="white").pack(side="left", anchor="w")

        self.btn_nuevo = ctk.CTkButton(self.sidebar, text="＋  Nuevo chat", font=("Helvetica", 13, "bold"),
            height=42, corner_radius=10, fg_color=C["accent"], hover_color=C["accent_dark"],
            text_color="white", command=self.nuevo_chat)
        self.btn_nuevo.grid(row=1, column=0, sticky="ew", padx=16, pady=(16, 8))

        self.lista_frame = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent",
                                                   scrollbar_button_color=C["sidebar_hover"])
        self.lista_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=4)

        footer = ctk.CTkFrame(self.sidebar, fg_color=C["sidebar_hover"], corner_radius=10, height=52)
        footer.grid(row=3, column=0, sticky="ew", padx=12, pady=12)
        footer.grid_propagate(False)
        ctk.CTkLabel(footer, text="Soporte IT · v2.0", font=("Helvetica", 11), text_color=C["text_muted"]).pack(expand=True)

    def cargar_sidebar(self):
        for w in self.lista_frame.winfo_children():
            w.destroy()
        if not os.path.exists("conversaciones"):
            return
        for arch in sorted(os.listdir("conversaciones"), reverse=True):
            if not arch.endswith(".json"):
                continue
            try:
                with open(f"conversaciones/{arch}", encoding="utf-8") as f:
                    data = json.load(f)

                # Ignorar chats vacíos (solo tienen el system prompt)
                mensajes_reales = [m for m in data.get("mensajes", []) if m["role"] != "system"]
                if not mensajes_reales:
                    continue

                titulo = data.get("titulo", "").strip() or "Chat sin título"
                fecha  = data.get("fecha", "")

                # Usar CTkButton directamente — área de click completa garantizada
                texto_btn = "💬  " + titulo[:26] + "\n" + fecha
                btn = ctk.CTkButton(
                    self.lista_frame,
                    text=texto_btn,
                    font=("Helvetica", 12),
                    height=56,
                    corner_radius=8,
                    fg_color=C["sidebar_btn"],
                    hover_color=C["sidebar_hover"],
                    text_color="white",
                    anchor="w",
                    command=lambda a=arch: self.cargar_chat(a)
                )
                btn.pack(fill="x", pady=3, padx=4)
            except Exception:
                pass

    def cargar_chat(self, archivo):
        try:
            with open(f"conversaciones/{archivo}", encoding="utf-8") as f:
                data = json.load(f)
            self.historial = data["mensajes"]
            self._limpiar_chat()
            for m in self.historial:
                if m["role"] == "system":
                    continue
                contenido = m["content"]
                imagen_ruta = m.get("imagen_ruta", None)
                if isinstance(contenido, list):
                    texto = next((p["text"] for p in contenido if p.get("type") == "text"), "📎 Imagen adjunta")
                    texto = (texto or "📎 Imagen adjunta") + "  🖼️"
                else:
                    texto = contenido
                BurbujaChat(self.chat_frame, texto, es_ia=(m["role"] == "assistant"),
                            avatar_ia=self.avatar_ia, imagen_ruta=imagen_ruta)
            # Forzar actualización del layout antes de scrollear
            self.chat_frame.update_idletasks()
            self.after(50, self._scroll_arriba)
        except Exception:
            pass

    def _construir_main(self):
        self.main = ctk.CTkFrame(self, fg_color=C["bg_app"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(1, weight=1)
        self.main.grid_columnconfigure(0, weight=1)
        self._construir_header()
        self._construir_area_chat()
        self._construir_panel_video()
        self._construir_entrada()

    def _construir_header(self):
        header = ctk.CTkFrame(self.main, height=64, corner_radius=0,
                              fg_color=C["header_bg"], border_width=1, border_color=C["border"])
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_propagate(False)
        self.btn_toggle = ctk.CTkButton(header, text="☰", width=40, height=40,
            fg_color="transparent", hover_color=C["bg_app"], text_color=C["text_dark"],
            font=("Helvetica", 18), corner_radius=8, command=self.toggle_sidebar)
        self.btn_toggle.pack(side="left", padx=12)
        ctk.CTkLabel(header, text="Soporte de Incidencias IT", font=("Helvetica", 16, "bold"),
                     text_color=C["text_dark"]).pack(side="left", padx=4)
        ctk.CTkLabel(header, text="● En línea", font=("Helvetica", 12), text_color="#22C55E").pack(side="right", padx=20)

    def _construir_area_chat(self):
        self.chat_frame = ctk.CTkScrollableFrame(self.main, fg_color=C["bg_app"], scrollbar_button_color=C["border"])
        self.chat_frame.grid(row=1, column=0, sticky="nsew")
        self.welcome = ctk.CTkFrame(self.chat_frame, fg_color=C["card"], corner_radius=16,
                                    border_width=1, border_color=C["border"])
        self.welcome.pack(fill="x", padx=24, pady=32)
        ctk.CTkLabel(self.welcome, text="👋  Bienvenido a DigiHelp AI",
                     font=("Helvetica", 20, "bold"), text_color=C["text_dark"]).pack(pady=(24, 8))
        ctk.CTkLabel(self.welcome, text="Describe tu incidencia IT y te ayudaré a resolverla paso a paso.",
                     font=("Helvetica", 13), text_color=C["text_muted"]).pack(pady=(0, 8))
        sugerencias = ["Mi impresora no conecta a la red", "No puedo acceder a la VPN",
                       "Mi equipo está muy lento", "Olvidé mi contraseña de dominio"]
        grid = ctk.CTkFrame(self.welcome, fg_color="transparent")
        grid.pack(pady=(8, 24), padx=24)
        for i, s in enumerate(sugerencias):
            btn = ctk.CTkButton(grid, text=s, height=36, corner_radius=18,
                fg_color=C["bg_app"], hover_color=C["border"], text_color=C["accent"],
                border_width=1, border_color=C["accent"], font=("Helvetica", 12),
                command=lambda t=s: self._enviar_sugerencia(t))
            btn.grid(row=i // 2, column=i % 2, padx=6, pady=4, sticky="ew")
        self.avatar_ia = self._crear_avatar()

    def _construir_panel_video(self):
        # Panel lateral eliminado — ahora el video abre en ventana independiente
        self.video_label = None  # se crea dinámicamente en la ventana

    def _construir_entrada(self):
        self._entrada_bg = ctk.CTkFrame(self.main, corner_radius=0,
                                  fg_color=C["header_bg"], border_width=1, border_color=C["border"])
        self._entrada_bg.grid(row=2, column=0, columnspan=2, sticky="ew")

        # Preview de imagen adjunta (oculto por defecto)
        self._preview_frame = ctk.CTkFrame(self._entrada_bg, fg_color="#EFF6FF",
                                           corner_radius=8, border_width=1, border_color=C["accent"])
        self._lbl_preview = ctk.CTkLabel(self._preview_frame, text="",
                                         font=("Helvetica", 12), text_color=C["accent"])
        self._lbl_preview.pack(side="left", padx=10, pady=6)
        ctk.CTkButton(self._preview_frame, text="✕", width=24, height=24,
                      fg_color="transparent", hover_color="#DBEAFE",
                      text_color=C["accent"], font=("Helvetica", 12),
                      command=self._quitar_imagen).pack(side="right", padx=6)

        inner = ctk.CTkFrame(self._entrada_bg, fg_color="transparent", height=70)
        inner.pack(fill="x", expand=True, padx=20, pady=10)
        inner.pack_propagate(False)

        # Botón único de adjuntar
        self.btn_adjuntar = ctk.CTkButton(inner, text="📎", width=46, height=46,
            corner_radius=23, fg_color=C["bg_app"], hover_color=C["border"],
            text_color=C["text_dark"], font=("Helvetica", 18), border_width=1,
            border_color=C["border"], command=self._toggle_panel_adjuntar)
        self.btn_adjuntar.pack(side="left", padx=(0, 10))

        self._panel_adjuntar = None  # se crea como Toplevel al pulsar el botón

        self.entry = ctk.CTkEntry(inner, placeholder_text="Describe tu incidencia IT aquí...",
            height=46, corner_radius=23, fg_color=C["input_bg"], border_color=C["border"],
            border_width=1, font=("Helvetica", 13), text_color=C["text_dark"])
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.entry.bind("<Return>", lambda e: self.lanzar_hilo())

        self.btn_enviar = ctk.CTkButton(inner, text="Enviar  ➤", width=110, height=46,
            corner_radius=23, fg_color=C["accent"], hover_color=C["accent_dark"],
            font=("Helvetica", 13, "bold"), text_color="white", command=self.lanzar_hilo)
        self.btn_enviar.pack(side="right")

    def _toggle_panel_adjuntar(self):
        if self._panel_adjuntar and self._panel_adjuntar.winfo_exists():
            self._cerrar_panel_adjuntar()
            return

        # Calcular posición encima del botón usando coordenadas absolutas
        self.update_idletasks()
        bx = self.btn_adjuntar.winfo_rootx()
        by = self.btn_adjuntar.winfo_rooty()

        # Crear ventana popup sin bordes
        popup = ctk.CTkToplevel(self)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(fg_color=C["card"])
        popup.resizable(False, False)

        # Borde manual con frame exterior
        outer = ctk.CTkFrame(popup, fg_color=C["card"], corner_radius=12,
                             border_width=1, border_color=C["border"])
        outer.pack(fill="both", expand=True, padx=1, pady=1)

        ctk.CTkLabel(outer, text="Adjuntar archivo",
            font=("Helvetica", 11, "bold"), text_color=C["text_muted"]).pack(
            pady=(10, 4), padx=16, anchor="w")

        ctk.CTkButton(outer, text="  🖼️   Imagen",
            height=40, corner_radius=8, anchor="w", width=190,
            fg_color="transparent", hover_color=C["bg_app"],
            text_color=C["text_dark"], font=("Helvetica", 13),
            command=lambda: [self._cerrar_panel_adjuntar(), self._adjuntar_imagen()]
        ).pack(fill="x", padx=8, pady=2)

        ctk.CTkButton(outer, text="  📄   Documento",
            height=40, corner_radius=8, anchor="w", width=190,
            fg_color="transparent", hover_color=C["bg_app"],
            text_color=C["text_dark"], font=("Helvetica", 13),
            command=lambda: [self._cerrar_panel_adjuntar(), self._adjuntar_documento()]
        ).pack(fill="x", padx=8, pady=(2, 10))

        # Posicionar encima del botón
        popup.update_idletasks()
        ph = popup.winfo_reqheight()
        pw = popup.winfo_reqwidth()
        popup.geometry(f"{pw}x{ph}+{bx}+{by - ph - 6}")

        self._panel_adjuntar = popup
        self.btn_adjuntar.configure(fg_color="#DBEAFE", border_color=C["accent"])

        # Cerrar al hacer click en cualquier sitio de la app principal
        self.bind("<Button-1>", self._click_fuera_panel, add="+")
        self.bind_all("<Escape>", lambda e: self._cerrar_panel_adjuntar())

    def _click_fuera_panel(self, event):
        self.after(50, self._cerrar_panel_adjuntar)

    def _cerrar_panel_adjuntar(self):
        if self._panel_adjuntar and self._panel_adjuntar.winfo_exists():
            self._panel_adjuntar.destroy()
        self._panel_adjuntar = None
        self.btn_adjuntar.configure(fg_color=C["bg_app"], border_color=C["border"])
        try:
            self.unbind("<Button-1>")
            self.unbind("<Escape>")
        except Exception:
            pass

    def _adjuntar_documento(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar documento",
            filetypes=[
                ("Documentos", "*.pdf *.docx *.xlsx *.txt"),
                ("PDF", "*.pdf"), ("Word", "*.docx"),
                ("Excel", "*.xlsx"), ("Texto", "*.txt"),
                ("Todos", "*.*")
            ]
        )
        if not ruta:
            return
        try:
            texto = self._extraer_texto_doc(ruta)
            if not texto.strip():
                raise ValueError("El documento está vacío o no se pudo leer.")
            # Truncar a 8000 caracteres para no saturar el contexto
            if len(texto) > 8000:
                texto = texto[:8000] + "\n\n[... documento truncado ...]"
            self._doc_adjunto = (ruta, texto)
            nombre = os.path.basename(ruta)
            self._lbl_preview.configure(text=f"📄  {nombre}")
            self._preview_frame.pack(fill="x", padx=20, pady=(8, 0),
                                     before=self._entrada_bg.winfo_children()[1])
            self.btn_adjuntar.configure(fg_color="#DBEAFE", border_color=C["accent"])
        except Exception as e:
            self._lbl_preview.configure(text=f"⚠️ Error: {e}")
            self._preview_frame.pack(fill="x", padx=20, pady=(8, 0),
                                     before=self._entrada_bg.winfo_children()[1])

    def _extraer_texto_doc(self, ruta):
        ext = ruta.lower().split(".")[-1]
        if ext == "pdf":
            doc = fitz.open(ruta)
            return "\n".join(page.get_text() for page in doc)
        elif ext == "docx":
            doc = DocxDocument(ruta)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        elif ext == "xlsx":
            wb = openpyxl.load_workbook(ruta, data_only=True)
            lineas = []
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                lineas.append(f"--- Hoja: {sheet} ---")
                for row in ws.iter_rows(values_only=True):
                    fila = [str(c) if c is not None else "" for c in row]
                    if any(fila):
                        lineas.append("\t".join(fila))
            return "\n".join(lineas)
        elif ext == "txt":
            with open(ruta, encoding="utf-8", errors="ignore") as f:
                return f.read()
        return ""

    def _quitar_documento(self):
        self._doc_adjunto = None
        self.btn_adjuntar.configure(fg_color=C["bg_app"], border_color=C["border"])

    def _mostrar_error_imagen(self, err):
        BurbujaChat(self.chat_frame, f"⚠️ No se pudo procesar la imagen: {err}",
                    es_ia=True, avatar_ia=self.avatar_ia)
        self._scroll_abajo()

    def _adjuntar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.webp"), ("Todos", "*.*")]
        )
        if not ruta:
            return
        # Solo guardar la ruta — el base64 se genera en el hilo secundario al enviar
        ext = ruta.lower().split(".")[-1]
        media_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                      "png": "image/png", "gif": "image/gif",
                      "webp": "image/webp"}.get(ext, "image/png")
        self._imagen_adjunta = (ruta, None, media_type)  # base64 pendiente
        nombre = os.path.basename(ruta)
        self._lbl_preview.configure(text=f"📎  {nombre}")
        self._preview_frame.pack(fill="x", padx=20, pady=(8, 0), before=self._entrada_bg.winfo_children()[1])
        self.btn_adjuntar.configure(fg_color="#DBEAFE", border_color=C["accent"])

    def _quitar_imagen(self):
        self._imagen_adjunta = None
        self.btn_adjuntar.configure(fg_color=C["bg_app"], border_color=C["border"])
        if not self._doc_adjunto:
            self._preview_frame.pack_forget()

    def _enviar_sugerencia(self, texto):
        self.entry.delete(0, "end")
        self.entry.insert(0, texto)
        self.lanzar_hilo()

    def lanzar_hilo(self):
        msg = self.entry.get().strip()
        if not msg and not self._imagen_adjunta:
            return
        if self.welcome and self.welcome.winfo_exists():
            self.welcome.destroy()
            self.welcome = None
        self.entry.delete(0, "end")
        self.btn_enviar.configure(state="disabled", text="Enviando…")
        ts = datetime.now().strftime("%H:%M")

        # Si estamos esperando confirmación de resolución
        if self._esperando_confirmacion:
            msg_lower = msg.lower()
            # Detectar primero frases negativas (tienen prioridad)
            no_resuelto = any(p in msg_lower for p in [
                "no", "sigue", "todavía", "aún", "nada", "no funciona",
                "no va", "igual", "mismo", "sin funcionar", "tampoco",
                "sigue igual", "no me va", "no sirve", "no ha funcionado",
                "no funciona", "mal", "peor", "falla"
            ])
            # Solo marcar como resuelto si NO hay palabras negativas
            resuelto = not no_resuelto and any(p in msg_lower for p in [
                "sí", "si", "funciona", "resuelto", "gracias", "perfecto",
                "ya va", "solucionado", "ok", "vale", "genial", "listo",
                "ya funciona", "perfecto", "bien"
            ])

            if resuelto:
                # Problema resuelto — resetear todo
                self._intentos = 0
                self._esperando_confirmacion = False
                self._problema_inicial = None
                BurbujaChat(self.chat_frame, "¡Perfecto! Me alegra que se haya resuelto. Si tienes cualquier otra incidencia, aquí estaré. 😊",
                            es_ia=True, avatar_ia=self.avatar_ia, timestamp=ts)
                self._scroll_abajo()
                self.btn_enviar.configure(state="normal", text="Enviar  ➤")
                return

            elif no_resuelto:
                self._intentos += 1
                self._esperando_confirmacion = False

                if self._intentos >= 5:
                    # Máximo de intentos alcanzado — mostrar diálogo y NO continuar
                    BurbujaChat(self.chat_frame,
                                "He agotado mis intentos para resolver esta incidencia. Voy a crear un ticket para que el equipo de IT te ayude directamente.",
                                es_ia=True, avatar_ia=self.avatar_ia, timestamp=ts)
                    self._scroll_abajo()
                    self.after(800, self._mostrar_dialogo_incidencia)
                    self.btn_enviar.configure(state="normal", text="Enviar  ➤")
                    return
                # Si no llegó a 5, continuar con la IA normalmente

        imagen = self._imagen_adjunta
        doc    = self._doc_adjunto
        self._quitar_imagen()
        if doc:
            self._quitar_documento()
            self._preview_frame.pack_forget()

        # Mostrar burbuja del usuario
        if imagen and doc:
            texto_burbuja = (msg or "📎 Adjunto") + "  🖼️📄"
        elif imagen:
            texto_burbuja = (msg or "📎 Imagen adjunta") + "  🖼️"
        elif doc:
            nombre_doc = os.path.basename(doc[0])
            texto_burbuja = (msg or f"📄 {nombre_doc}") + f"  📄"
        else:
            texto_burbuja = msg
        ruta_img = imagen[0] if imagen else None
        BurbujaChat(self.chat_frame, texto_burbuja, es_ia=False, timestamp=ts, imagen_ruta=ruta_img)
        self._scroll_abajo()

        es_primero = len([m for m in self.historial if m["role"] == "user"]) == 0
        texto_para_video = msg or "imagen"
        # Pasar imagen como tupla (ruta, None, media_type) — base64 se genera en el hilo
        threading.Thread(
            target=self._responder_ia,
            args=(msg, es_primero, ts, imagen, doc),
            daemon=True
        ).start()

    def _fijar_titulo(self, texto_usuario):
        titulo = self._generar_titulo(texto_usuario)
        nuevo_archivo = "".join(c for c in titulo if c.isalnum() or c in " _-")[:40].strip()
        if nuevo_archivo and nuevo_archivo != self._chat_archivo:
            viejo = f"conversaciones/{self._chat_archivo}.json"
            if os.path.exists(viejo):
                os.remove(viejo)
            self._chat_archivo = nuevo_archivo
        self._chat_titulo = titulo

    def _responder_ia(self, texto_usuario, es_primero, ts, imagen=None, doc=None):
        # Fijar archivo desde el principio para todos los mensajes del chat
        if not self._chat_archivo:
            self._chat_archivo = self.chat_id

        # Codificar imagen a base64 aquí (hilo secundario, no bloquea la UI)
        usa_vision = False
        if imagen:
            try:
                ruta, _, media_type = imagen
                with open(ruta, "rb") as f:
                    b64 = base64.standard_b64encode(f.read()).decode("utf-8")
                contenido_user = [
                    {"type": "text", "text": texto_usuario or "Analiza esta imagen y ayúdame a resolver el problema de IT que ves."},
                    {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{b64}"}}
                ]
                usa_vision = True
            except Exception as e:
                contenido_user = texto_usuario or ""
                self.after(0, lambda: self._mostrar_error_imagen(str(e)))
        else:
            contenido_user = texto_usuario or ""

        # Si hay documento adjunto, añadir su contenido al mensaje
        if doc:
            _, texto_doc = doc
            nombre_doc = os.path.basename(doc[0])
            if isinstance(contenido_user, list):
                contenido_user[0]["text"] += f"\n\n---\nDocumento adjunto: {nombre_doc}\n{texto_doc}"
            else:
                contenido_user = f"{contenido_user}\n\n---\nDocumento adjunto: {nombre_doc}\n{texto_doc}".strip()

        # AÑADIR MENSAJE DEL USUARIO AL HISTORIAL
        entrada = {"role": "user", "content": contenido_user}
        if imagen:
            entrada["imagen_ruta"] = imagen[0]
        if doc:
            entrada["doc_nombre"] = os.path.basename(doc[0])
        self.historial.append(entrada)

        # Comprobar si hay video con mensaje predefinido
        ruta_v, msg_v = self._buscar_video(texto_usuario)
        if ruta_v and msg_v:
            self.historial.append({"role": "assistant", "content": msg_v})
            self.after(0, lambda m=msg_v: BurbujaChat(
                self.chat_frame, m, es_ia=True,
                avatar_ia=self.avatar_ia, timestamp=ts))
            self.after(0, self._scroll_abajo)
            self.after(300, lambda r=ruta_v: self.reproducir_video(r))
            if es_primero:
                self._fijar_titulo(texto_usuario)
            self._guardar_chat()
            self.after(0, self.cargar_sidebar)
            self.after(0, lambda: self.btn_enviar.configure(state="normal", text="Enviar  ➤"))
            return

        # Respuesta normal de la IA
        burbuja_ref = [None]
        creada = threading.Event()

        def crear_burbuja():
            burbuja_ref[0] = BurbujaChat(self.chat_frame, "⏳ Analizando tu incidencia…",
                                         es_ia=True, avatar_ia=self.avatar_ia, timestamp=ts)
            self._scroll_abajo()
            creada.set()

        self.after(0, crear_burbuja)
        creada.wait(timeout=3.0)

        respuesta = ""
        try:
            # Usar visión si el mensaje actual o alguno anterior tiene imagen
            hay_imagen_en_historial = any(
                isinstance(m["content"], list) for m in self.historial
            )
            modelo_actual = MODELO_VISION if (usa_vision or hay_imagen_en_historial) else MODELO_TEXTO

            # Limpiar historial: quitar imagen_ruta pero mantener imágenes en formato API
            historial_limpio = []
            for m in self.historial:
                historial_limpio.append({"role": m["role"], "content": m["content"]})
            stream = client.chat.completions.create(
                model=modelo_actual, messages=historial_limpio,
                max_tokens=1024, stream=True, timeout=30)
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    respuesta += delta
                    snap = respuesta
                    if burbuja_ref[0]:
                        self.after(0, lambda t=snap: burbuja_ref[0].actualizar_texto(t))
                    self.after(0, self._scroll_abajo)

            self.historial.append({"role": "assistant", "content": respuesta})

            if es_primero:
                self._fijar_titulo(texto_usuario)
                self._problema_inicial = texto_usuario
            self._guardar_chat()
            self.after(0, self.cargar_sidebar)

            if ruta_v:
                self.after(200, lambda r=ruta_v: self.reproducir_video(r))

            # Activar espera de confirmación tras cada respuesta IT
            if respuesta.strip() and not (ruta_v and msg_v):
                self._esperando_confirmacion = True

        except Exception as e:
            err = str(e)
            if burbuja_ref[0]:
                self.after(0, lambda: burbuja_ref[0].actualizar_texto(f"⚠️ Error: {err}"))
        finally:
            self.after(0, lambda: self.btn_enviar.configure(state="normal", text="Enviar  ➤"))

    def _crear_incidencia_flujo(self, msg, ts):
        # Pedir nombre y urgencia al usuario mediante ventana
        self.after(0, lambda: self._mostrar_dialogo_incidencia())

    def _mostrar_dialogo_incidencia(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Crear Incidencia")
        ventana.geometry("420x320")
        ventana.configure(fg_color=C["card"])
        ventana.attributes("-topmost", True)
        ventana.resizable(False, False)

        ctk.CTkLabel(ventana, text="⚠️ No hemos podido resolver tu incidencia",
                     font=("Helvetica", 14, "bold"), text_color=C["text_dark"],
                     wraplength=360).pack(pady=(24, 4), padx=24)
        ctk.CTkLabel(ventana, text="Vamos a crear un ticket para el equipo de IT.",
                     font=("Helvetica", 12), text_color=C["text_muted"]).pack(pady=(0, 20))

        ctk.CTkLabel(ventana, text="Tu nombre:", font=("Helvetica", 12),
                     text_color=C["text_dark"], anchor="w").pack(fill="x", padx=24)
        entry_nombre = ctk.CTkEntry(ventana, placeholder_text="Ej: Juan García",
                                    height=38, corner_radius=8)
        entry_nombre.pack(fill="x", padx=24, pady=(4, 12))

        ctk.CTkLabel(ventana, text="Nivel de urgencia:", font=("Helvetica", 12),
                     text_color=C["text_dark"], anchor="w").pack(fill="x", padx=24)
        urgencia_var = ctk.StringVar(value="media")
        frame_urg = ctk.CTkFrame(ventana, fg_color="transparent")
        frame_urg.pack(fill="x", padx=24, pady=(4, 20))
        for u in ["baja", "media", "alta"]:
            ctk.CTkRadioButton(frame_urg, text=u.capitalize(), variable=urgencia_var,
                               value=u, font=("Helvetica", 12)).pack(side="left", padx=8)

        def confirmar():
            nombre = entry_nombre.get().strip() or "Usuario desconocido"
            urgencia = urgencia_var.get()
            problema = self._problema_inicial or "Sin descripción"
            exito = crear_incidencia_db(nombre, problema, urgencia)
            ventana.destroy()
            ts = datetime.now().strftime("%H:%M")
            if exito:
                msg_ticket = f"✅ Ticket creado correctamente para {nombre}. El equipo de IT revisará tu incidencia lo antes posible."
            else:
                msg_ticket = "⚠️ No se pudo crear el ticket. Por favor contacta directamente con el equipo de IT."
            self.after(0, lambda m=msg_ticket: BurbujaChat(
                self.chat_frame, m, es_ia=True, avatar_ia=self.avatar_ia, timestamp=ts))
            self.after(0, self._scroll_abajo)
            self._intentos = 0
            self._problema_inicial = None
            self._esperando_confirmacion = False

        ctk.CTkButton(ventana, text="Crear ticket", height=40, corner_radius=10,
                      fg_color=C["accent"], hover_color=C["accent_dark"],
                      text_color="white", font=("Helvetica", 13, "bold"),
                      command=confirmar).pack(padx=24, fill="x")

    def _crear_ticket_automatico(self, ts):
        problema = self._problema_inicial or "Sin descripcion"
        pl = problema.lower()
        if any(p in pl for p in ["no enciende","pantalla azul","virus","hackeado","datos perdidos","no arranca","caido","servidor"]):
            urgencia = "alta"
        elif any(p in pl for p in ["impresora","internet","red","correo","contrasena","vpn","lento","cuelga"]):
            urgencia = "media"
        else:
            urgencia = "baja"
        nombre = "Usuario desconocido"
        for m in self.historial:
            if m["role"] == "user" and isinstance(m["content"], str):
                txt = m["content"].lower()
                for prefix in ["soy ", "me llamo ", "mi nombre es "]:
                    if prefix in txt:
                        partes = txt.split(prefix)
                        if len(partes) > 1:
                            nombre = partes[1].split()[0].capitalize()
                            break
        exito = crear_incidencia_db(nombre, problema, urgencia)
        ts_actual = datetime.now().strftime("%H:%M")
        sep = chr(10)
        if exito:
            msg_ticket = ("Avisame de que he agotado mis intentos para resolver esta incidencia." + sep +
                          "He creado un ticket automaticamente:" + sep +
                          "Problema: " + problema + sep +
                          "Urgencia: " + urgencia.upper() + sep +
                          "El equipo de IT lo revisara lo antes posible.")
        else:
            msg_ticket = "He agotado mis intentos y no pude crear el ticket. Contacta con IT directamente."
        self.after(0, lambda m=msg_ticket: BurbujaChat(
            self.chat_frame, m, es_ia=True, avatar_ia=self.avatar_ia, timestamp=ts_actual))
        self.after(0, self._scroll_abajo)
        self._intentos = 0
        self._problema_inicial = None
        self._esperando_confirmacion = False

    def _guardar_chat(self):
        if not self._chat_archivo:
            self._chat_archivo = self.chat_id
        if not self._chat_titulo:
            self._chat_titulo = self._chat_archivo

        # Limpiar mensajes con imagen antes de guardar (no guardar base64, sí guardar ruta)
        mensajes_limpios = []
        for m in self.historial:
            if isinstance(m["content"], list):
                texto = next((p["text"] for p in m["content"] if p.get("type") == "text"), "")
                ruta_img = m.get("imagen_ruta", "")
                mensajes_limpios.append({
                    "role": m["role"],
                    "content": (texto or "📎 Imagen adjunta") + "  🖼️",
                    "imagen_ruta": ruta_img
                })
            else:
                mensajes_limpios.append(m)

        datos = {
            "titulo": self._chat_titulo,
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "mensajes": mensajes_limpios
        }
        with open(f"conversaciones/{self._chat_archivo}.json", "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _generar_titulo(self, msg):
        try:
            r = client.chat.completions.create(model=MODELO, max_tokens=20,
                messages=[{"role": "user", "content": f"Resume en 4 palabras máximo (solo el título, sin comillas ni puntos): {msg}"}])
            titulo = r.choices[0].message.content.strip().strip('"').strip("'").strip(".")
            return titulo if titulo else "Incidencia IT"
        except Exception:
            return "Incidencia IT"

    def _buscar_video(self, texto):
        if not texto:
            return None, None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT palabra_clave, ruta_video, mensaje FROM videos")
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            texto_lower = texto.lower()
            for row in rows:
                if row["palabra_clave"].lower() in texto_lower:
                    return row["ruta_video"], row.get("mensaje")
        except Exception as e:
            print(f"[DB] Error: {e}")
        return None, None

    def reproducir_video(self, ruta_video):
        if not os.path.isabs(ruta_video):
            ruta_video = recurso_path(ruta_video)
        if not os.path.exists(ruta_video):
            print(f"[Video] No encontrado: {ruta_video}")
            return
        self.cerrar_video()

        # Estado del reproductor
        self.video_activo  = True
        self.video_pausado = False
        self.video_cap     = cv2.VideoCapture(ruta_video)
        if not self.video_cap.isOpened():
            print(f"[Video] No se pudo abrir: {ruta_video}")
            return

        self._total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        self._video_delay  = 1.0 / fps if fps > 0 else 0.033

        # ── Ventana ──────────────────────────────────
        self._ventana_video = ctk.CTkToplevel(self)
        self._ventana_video.title("DigiHelp — Tutorial")
        self._ventana_video.geometry("740x560")
        self._ventana_video.configure(fg_color=C["video_bg"])
        self._ventana_video.attributes("-topmost", True)
        self._ventana_video.protocol("WM_DELETE_WINDOW", self.cerrar_video)
        self._ventana_video.resizable(False, False)

        # ── Header ───────────────────────────────────
        header_v = ctk.CTkFrame(self._ventana_video, fg_color="#1E293B", height=48)
        header_v.pack(fill="x")
        header_v.pack_propagate(False)
        ctk.CTkLabel(header_v, text="▶  Tutorial DigiHelp",
                     font=("Helvetica", 14, "bold"), text_color="white").pack(side="left", padx=16)
        ctk.CTkButton(header_v, text="✕ Cerrar", width=80, height=30,
                      fg_color="#EF4444", hover_color="#DC2626", text_color="white",
                      font=("Helvetica", 12), command=self.cerrar_video).pack(side="right", padx=12, pady=8)

        # ── Área de video ─────────────────────────────
        self.video_label = ctk.CTkLabel(self._ventana_video, text="Cargando...",
                                        text_color=C["text_muted"], fg_color="#000000")
        self.video_label.pack(expand=True, fill="both", padx=0, pady=0)

        # ── Barra de progreso ─────────────────────────
        self._progress_var = ctk.DoubleVar(value=0)
        self._slider = ctk.CTkSlider(
            self._ventana_video, from_=0, to=max(self._total_frames - 1, 1),
            variable=self._progress_var, button_color=C["accent"],
            button_hover_color=C["accent_dark"], progress_color=C["accent"],
            fg_color="#374151", height=14,
            command=self._saltar_a_frame
        )
        self._slider.pack(fill="x", padx=16, pady=(8, 4))

        # ── Tiempo ────────────────────────────────────
        self._lbl_tiempo = ctk.CTkLabel(self._ventana_video, text="0:00 / 0:00",
                                        font=("Helvetica", 11), text_color=C["text_muted"])
        self._lbl_tiempo.pack()

        # ── Controles ─────────────────────────────────
        controles = ctk.CTkFrame(self._ventana_video, fg_color="#1E293B", height=60)
        controles.pack(fill="x", pady=(4, 0))
        controles.pack_propagate(False)

        estilo_btn = dict(width=52, height=40, corner_radius=10,
                          fg_color="#374151", hover_color="#4B5563",
                          text_color="white", font=("Helvetica", 16))

        ctk.CTkButton(controles, text="⏮", **estilo_btn,
                      command=lambda: self._saltar_segundos(-30)).pack(side="left", padx=(16, 4), pady=10)
        ctk.CTkButton(controles, text="⏪", **estilo_btn,
                      command=lambda: self._saltar_segundos(-10)).pack(side="left", padx=4, pady=10)

        self._btn_play = ctk.CTkButton(controles, text="⏸", width=64, height=40,
                      corner_radius=10, fg_color=C["accent"], hover_color=C["accent_dark"],
                      text_color="white", font=("Helvetica", 18),
                      command=self._toggle_pausa)
        self._btn_play.pack(side="left", padx=8, pady=10)

        ctk.CTkButton(controles, text="⏩", **estilo_btn,
                      command=lambda: self._saltar_segundos(10)).pack(side="left", padx=4, pady=10)
        ctk.CTkButton(controles, text="⏭", **estilo_btn,
                      command=lambda: self._saltar_segundos(30)).pack(side="left", padx=4, pady=10)

        threading.Thread(target=self._stream_video, daemon=True).start()

    def _toggle_pausa(self):
        self.video_pausado = not self.video_pausado
        self._btn_play.configure(text="▶" if self.video_pausado else "⏸")

    def _saltar_segundos(self, segundos):
        if not self.video_cap:
            return
        fps = 1.0 / self._video_delay
        frame_actual = int(self.video_cap.get(cv2.CAP_PROP_POS_FRAMES))
        nuevo_frame  = max(0, min(frame_actual + int(segundos * fps), self._total_frames - 1))
        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, nuevo_frame)

    def _saltar_a_frame(self, valor):
        if self.video_cap:
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, int(valor))

    def _stream_video(self):
        fps = 1.0 / self._video_delay
        while self.video_activo and self.video_cap and self.video_cap.isOpened():
            if self.video_pausado:
                time.sleep(0.05)
                continue

            ret, frame = self.video_cap.read()
            if not ret:
                # Rebobinar al terminar
                self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.video_pausado = True
                self.after(0, lambda: self._btn_play.configure(text="▶"))
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb).resize((740, 416), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(740, 416))

            frame_actual = int(self.video_cap.get(cv2.CAP_PROP_POS_FRAMES))

            if self.video_label and self.video_label.winfo_exists():
                self.after(0, lambda i=ctk_img: self.video_label.configure(image=i, text=""))
                self.video_label._img_ref = ctk_img

            # Actualizar slider y tiempo
            def _update_ui(f=frame_actual):
                self._progress_var.set(f)
                seg_actual = int(f / fps)
                seg_total  = int(self._total_frames / fps)
                self._lbl_tiempo.configure(
                    text=f"{seg_actual // 60}:{seg_actual % 60:02d} / {seg_total // 60}:{seg_total % 60:02d}"
                )
            self.after(0, _update_ui)

            time.sleep(self._video_delay)

        if self.video_cap:
            self.video_cap.release()

    def cerrar_video(self):
        self.video_activo = False
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None
        if hasattr(self, "_ventana_video") and self._ventana_video.winfo_exists():
            self._ventana_video.destroy()

    def _crear_avatar(self):
        try:
            img = Image.open(recurso_path("avatar.png")).convert("RGBA")
            s = min(img.size)
            img = img.crop(((img.width-s)//2, (img.height-s)//2, (img.width+s)//2, (img.height+s)//2))
            img = img.resize((36, 36), Image.LANCZOS)
            mask = Image.new("L", (36, 36), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 36, 36), fill=255)
            out = Image.new("RGBA", (36, 36), (0, 0, 0, 0))
            out.paste(img, (0, 0), mask)
            return ctk.CTkImage(light_image=out, dark_image=out, size=(36, 36))
        except Exception:
            return None

    def _limpiar_chat(self):
        for w in self.chat_frame.winfo_children():
            w.destroy()
        self.welcome = None

    def _scroll_arriba(self):
        self.chat_frame._parent_canvas.yview_moveto(0.0)

    def _scroll_abajo(self):
        self.chat_frame._parent_canvas.yview_moveto(1.0)

    def nuevo_chat(self):
        self.chat_id = f"chat_{int(time.time())}"
        self._chat_titulo = None
        self._chat_archivo = None
        self._imagen_adjunta = None
        self._doc_adjunto = None
        self._intentos = 0            # Contador de intentos de resolución
        self._problema_inicial = None # Primer mensaje del usuario
        self._esperando_confirmacion = False  # Esperando si se resolvió
        self.historial = [{"role": "system", "content": SYSTEM_PROMPT}]
        self._limpiar_chat()
        self.cerrar_video()
        self.welcome = ctk.CTkFrame(self.chat_frame, fg_color=C["card"], corner_radius=16,
                                    border_width=1, border_color=C["border"])
        self.welcome.pack(fill="x", padx=24, pady=32)
        ctk.CTkLabel(self.welcome, text="👋  Bienvenido a DigiHelp AI",
                     font=("Helvetica", 20, "bold"), text_color=C["text_dark"]).pack(pady=(24, 8))
        ctk.CTkLabel(self.welcome, text="Describe tu incidencia IT y te ayudaré a resolverla paso a paso.",
                     font=("Helvetica", 13), text_color=C["text_muted"]).pack(pady=(0, 24))

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.grid_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.grid(row=0, column=0, sticky="nsew")
            self.sidebar_visible = True

if __name__ == "__main__":
    app = DigiHelpApp()
    app.mainloop()