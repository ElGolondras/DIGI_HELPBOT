# 🤖 DigiHelp AI — Chatbot de Soporte IT

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-1B2A4A?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq_API-LLaMA_3.3-F55036?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

**Asistente de soporte técnico IT con IA, login corporativo, análisis de imágenes y tutoriales en vídeo.**

</div>

---

## 📋 Índice

- [¿Qué es DigiHelp AI?](#-qué-es-digihelp-ai)
- [Características](#-características)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Compilar a .exe](#-compilar-a-exe)
- [Uso](#-uso)
- [FAQ](#-faq)

---

## ¿Qué es DigiHelp AI?

DigiHelp AI es un chatbot de escritorio especializado en resolver **incidencias de soporte técnico IT** para empresas. Usa inteligencia artificial para guiar a los usuarios paso a paso en la resolución de problemas técnicos, con un lenguaje sencillo pensado para personas sin conocimientos informáticos.

Incluye un sistema de **login corporativo con MySQL**, gestión de tickets automática, tutoriales en vídeo y un panel de personalización completo.

---

## ✨ Características

- 🔐 **Login corporativo** — Autenticación de usuarios contra base de datos MySQL
- 💬 **Chat con IA** — Respuestas en tiempo real con streaming usando LLaMA 3.3 70B vía Groq
- 🖼️ **Análisis de imágenes** — Adjunta capturas de pantalla o fotos de dispositivos para que la IA las analice (LLaMA 4 Scout Vision)
- 📄 **Soporte de documentos** — Adjunta PDF, Word, Excel o TXT como contexto adicional
- 🎬 **Tutoriales en vídeo** — Reproductor integrado que lanza vídeos automáticamente al detectar palabras clave
- ☁️ **Sincronización en la nube** — El historial de conversaciones y tus preferencias se guardan en MySQL vinculados a tu usuario.
- 🎫 **Tickets automáticos** — Crea incidencias en la base de datos con urgencia detectada automáticamente
- ⚙️ **Panel de personalización** — Tema claro/oscuro, 6 colores de acento y tamaño de fuente ajustable (sincronizado con tu cuenta).
- 🔒 **Configuración segura** — Credenciales gestionadas mediante archivo `.env`

---

## 🛠️ Requisitos previos

- **Python 3.10 o superior** — [Descargar desde python.org](https://www.python.org/downloads/)
  > ⚠️ Al instalar, marca la casilla **"Add Python to PATH"**
- **MySQL 8.x** con las tablas `usuarios` e `incidencias` creadas
- **Cuenta en GroqCloud** — [Crear cuenta gratis en console.groq.com](https://console.groq.com)
- **Git** (opcional, para clonar el repositorio)

### Esquema de base de datos necesario

```sql
CREATE DATABASE digihelp;
USE digihelp;

CREATE TABLE `chats` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `chat_id` varchar(100) NOT NULL,
  `titulo` varchar(200) DEFAULT NULL,
  `fecha` varchar(50) DEFAULT NULL,
  `mensajes` longtext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `incidencias` (
  `id` int(11) NOT NULL,
  `usuario` varchar(100) NOT NULL,
  `problema` text NOT NULL,
  `urgencia` enum('baja','media','alta') DEFAULT 'media',
  `estado` enum('pendiente','en_proceso','resuelta') DEFAULT 'pendiente',
  `fecha` datetime DEFAULT current_timestamp(),
  `departamento` varchar(100) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `preferencias` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `prefs` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `nombre_completo` varchar(100) NOT NULL,
  `departamento` varchar(50) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `contrasenia` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `videos` (
  `id` int(11) NOT NULL,
  `palabra_clave` varchar(100) NOT NULL,
  `ruta_video` varchar(255) NOT NULL,
  `mensaje` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

ALTER TABLE `chats`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_usuario_chat` (`usuario_id`,`chat_id`);

ALTER TABLE `incidencias`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `preferencias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `usuario_id` (`usuario_id`);

ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

ALTER TABLE `videos`
  ADD PRIMARY KEY (`id`);

ALTER TABLE `chats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=39;

ALTER TABLE `incidencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

ALTER TABLE `preferencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

ALTER TABLE `videos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

ALTER TABLE `chats`
  ADD CONSTRAINT `chats_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

ALTER TABLE `preferencias`
  ADD CONSTRAINT `preferencias_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

```

---

## 📦 Instalación

### Paso 1 — Descargar el proyecto

**Opción A — Con Git:**
```bash
git clone https://github.com/ElGolondras/DIGI_HELPBOT.git
cd DIGI_HELPBOT
```

**Opción B — Sin Git:**
1. Haz clic en el botón verde **Code** en GitHub
2. Selecciona **Download ZIP**
3. Descomprime la carpeta y ábrela

### Paso 2 — Instalar las dependencias

```bash
python -m pip install customtkinter pillow opencv-python groq pymupdf python-docx openpyxl mysql-connector-python
```

### Paso 3 — Configurar el archivo `.env`

Crea un archivo llamado `.env` en la carpeta raíz del proyecto con este contenido:

```env
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXX
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=digihelp
```

> 🔑 Para obtener tu API Key de Groq: ve a [console.groq.com](https://console.groq.com) → **API Keys** → **Create API Key**

### Paso 4 — Ejecutar la aplicación

```bash
python Corazon-IA.py
```

---

## ⚙️ Configuración

### Avatar personalizado

Coloca tus imágenes en la carpeta raíz del proyecto:
- `avatar.png` — Avatar circular del bot (cualquier tamaño, se recorta automáticamente)
- `avatar.ico` — Icono de la ventana y barra de tareas (formato `.ico`)

### Tutoriales en vídeo

Los vídeos se configuran directamente en la tabla `videos` de MySQL:

```sql
INSERT INTO videos (palabra_clave, ruta_video, mensaje) VALUES
('impresora', 'videos/tutorial_impresora.mp4', '🖨️ Te muestro cómo solucionar problemas de impresora paso a paso.'),
('vpn', 'videos/tutorial_vpn.mp4', '🔐 Aquí tienes la guía para conectarte a la VPN de la empresa.');
```

Los vídeos deben estar en la carpeta `videos/` en formato `.mp4`.

> 💡 Si una entrada tiene `mensaje` vacío (`NULL`), la IA responde normalmente y además se abre el vídeo.

### Panel de personalización

Accede pulsando el botón **⚙️** en el header de la aplicación. Puedes cambiar:
- **Tema**: Claro / Oscuro
- **Color de acento**: Azul, Violeta, Verde, Rojo, Naranja o Rosa
- **Tamaño de fuente**: de 11 a 17 px

Las preferencias se guardan automáticamente en `preferencias.json` y se aplican en cada inicio.

---

## 📁 Estructura del proyecto

```
DIGI_HELPBOT/
│
├── Corazon-IA.py              # Archivo principal de la aplicación
├── .env                       # Credenciales
├── preferencias.json          # Preferencias de personalización (autogenerado)
│
├── Imagenes/                  
│   └── avatar.ico             # Icono de ventana (opcional)
│   └── avatar.png             # Avatar del bot (opcional)
│
├── videos/                    # Carpeta de vídeos de tutoriales
│   └── tutorial.mp4
│
└── conversaciones/            # Generada automáticamente al usar la app
    └── *.json
```

> ⚠️ Añade `.env` a tu `.gitignore` para no exponer credenciales.

---

## 📦 Compilar a .exe

### Opción A — Auto PY to EXE (recomendado, interfaz gráfica)

1. Instala la herramienta:
```bash
python -m pip install auto-py-to-exe
python -m auto_py_to_exe
```

2. Configura así:
   - **Script Location:** selecciona `Corazon-IA.py`
   - **Onefile:** ✅ One File
   - **Console Window:** ✅ Window Based (sin consola)
   - **Icon:** selecciona `avatar.ico` (opcional)
   - **Additional Files:** añade `avatar.png`, `avatar.ico` y la carpeta `videos/`
   - **Additional Files:** añade también el archivo `.env` con destino `.`

3. En la sección **Advanced** → campo `--collect-all`, añade:
```
groq
customtkinter
mysql

```

4. Pulsa **CONVERT .PY TO .EXE** 🚀

> ⚠️ El `.env` debe estar siempre en la **misma carpeta que el `.exe`** para que se carguen las credenciales correctamente.

### Opción B — Línea de comandos

```bash
python -m PyInstaller --onefile --windowed ^
    --collect-all groq ^
    --collect-all customtkinter ^
    --add-data "avatar.png;." ^
    --add-data "avatar.ico;." ^
    --add-data ".env;." ^
    --add-data "videos;videos" ^
    --icon "avatar.ico" ^
    --name "DigiHelp" ^
    Corazon-IA.py
```

> 💡 El `.exe` generado solo funcionará en **Windows**. Para Mac/Linux hay que compilarlo en ese sistema operativo.

---

## 📖 Uso

| Acción | Cómo hacerlo |
|--------|--------------|
| Iniciar sesión | Introduce usuario y contraseña corporativos |
| Enviar mensaje | Escribe en el campo inferior y pulsa **Enter** o **Enviar ➤** |
| Adjuntar imagen | Pulsa **📎** → **🖼️ Imagen** → selecciona el archivo |
| Adjuntar documento | Pulsa **📎** → **📄 Documento** → selecciona PDF/Word/Excel/TXT |
| Ver tutorial en vídeo | Escribe una palabra clave configurada en la tabla `videos` |
| Nuevo chat | Pulsa **＋ Nuevo chat** en la sidebar |
| Retomar chat anterior | Haz clic en cualquier conversación de la sidebar |
| Ocultar sidebar | Pulsa el botón **☰** en la esquina superior izquierda |
| Personalizar apariencia | Pulsa el botón **⚙️** en el header |
| Cerrar sesión | Pulsa **⏻ Cerrar sesión** en la parte inferior de la sidebar |

---

## ❓ FAQ

**¿Es gratuito?**
Sí. GroqCloud ofrece una capa gratuita generosa. Solo necesitarás pagar si superas los límites de uso (prácticamente imposible para uso empresarial normal).

**¿Los datos se envían a la nube?**
Los mensajes de texto e imágenes se envían a la API de Groq para procesarlos. El historial de tus conversaciones y la personalización de tu interfaz se guardan **de forma segura en la base de datos MySQL de tu empresa**, asociadas a tu usuario corporativo. Las credenciales de la API nunca salen de tu red local.

**¿Funciona sin internet?**
No. La IA requiere conexión para llamar a la API de Groq. Los vídeos de tutoriales sí se reproducen sin internet.

**El .exe no conecta a la base de datos, ¿qué hago?**
Asegúrate de que el archivo `.env` está en la **misma carpeta que el `.exe`**. Si el problema persiste, lanza el `.exe` desde consola para ver el error exacto:
```bash
DigiHelp.exe
```

**El .exe no abre, ¿qué hago?**
Asegúrate de haber incluido `--collect-all groq` y `--collect-all customtkinter` al compilar. Si sigue sin funcionar, ejecuta desde consola para ver el error.

**¿Cómo cambio el nombre "DigiHelp AI" por el de mi empresa?**
Busca en el código `DigiHelp AI` y `DigiHelp` y reemplázalos. También puedes modificar el `SYSTEM_PROMPT` para personalizar el comportamiento de la IA.

---

<div align="center">

Hecho con ❤️ · [Reportar un bug](https://github.com/ElGolondras/DIGI_HELPBOT/issues)

</div>
