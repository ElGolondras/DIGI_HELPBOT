# 🤖 DigiHelp AI — Chatbot de Soporte IT

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.x-1B2A4A?style=for-the-badge)
![Groq](https://img.shields.io/badge/Groq_API-LLaMA_3.3-F55036?style=for-the-badge)
![MySQL](https://img.shields.io/badge/MySQL-8.x-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Google Drive](https://img.shields.io/badge/Google_Drive-API_v3-34A853?style=for-the-badge&logo=googledrive&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)

**Asistente de soporte técnico IT con IA, login corporativo, análisis de imágenes y tutoriales en vídeo desde Google Drive.**

</div>

---

## 📋 Índice

- [¿Qué es DigiHelp AI?](#-qué-es-digihelp-ai)
- [Características](#-características)
- [Requisitos previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Google Drive — Tutoriales en vídeo](#-google-drive--tutoriales-en-vídeo)
- [Base de datos en la nube](#-base-de-datos-en-la-nube)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Compilar a .exe](#-compilar-a-exe)
- [Uso](#-uso)
- [FAQ](#-faq)

---

## ¿Qué es DigiHelp AI?

DigiHelp AI es un chatbot de escritorio especializado en resolver **incidencias de soporte técnico IT** para empresas. Usa inteligencia artificial para guiar a los usuarios paso a paso en la resolución de problemas técnicos, con un lenguaje sencillo pensado para personas sin conocimientos informáticos.

Incluye un sistema de **login corporativo con MySQL**, gestión de tickets automática, tutoriales en vídeo desde **Google Drive** y un panel de personalización completo. La base de datos está alojada en la nube (**Clever Cloud**), por lo que el bot funciona desde cualquier sitio con conexión a internet.

---

## ✨ Características

- 🔐 **Login corporativo** — Autenticación de usuarios contra base de datos MySQL
- 💬 **Chat con IA** — Respuestas en tiempo real con streaming usando LLaMA 3.3 70B vía Groq
- 🖼️ **Análisis de imágenes** — Adjunta capturas de pantalla o fotos de dispositivos para que la IA las analice (LLaMA 4 Scout Vision)
- 📄 **Soporte de documentos** — Adjunta PDF, Word, Excel o TXT como contexto adicional
- 🎬 **Tutoriales en vídeo desde Google Drive** — Los vídeos se almacenan en Google Drive y se descargan automáticamente al detectar palabras clave. No es necesario tener los vídeos en local
- ☁️ **Sincronización en la nube** — El historial de conversaciones y preferencias se guardan en MySQL (Clever Cloud) vinculados a tu usuario, accesible desde cualquier PC
- 🌍 **Acceso desde cualquier sitio** — La base de datos está en la nube. Solo necesitas el ejecutable e internet
- 🎫 **Tickets automáticos** — Crea incidencias en la base de datos con urgencia detectada automáticamente
- ⚙️ **Panel de personalización** — Tema claro/oscuro, 6 colores de acento y tamaño de fuente ajustable (sincronizado con tu cuenta)
- 🔒 **Configuración segura** — Credenciales gestionadas mediante archivo `.env`

---

## 🛠️ Requisitos previos

- **Python 3.10 o superior** — [Descargar desde python.org](https://www.python.org/downloads/)
  > ⚠️ Al instalar, marca la casilla **"Add Python to PATH"**
- **Cuenta en GroqCloud** — [Crear cuenta gratis en console.groq.com](https://console.groq.com)
- **Cuenta en Clever Cloud** — [clever-cloud.com](https://clever-cloud.com) (base de datos MySQL gratuita en la nube)
- **Cuenta de Google** con Google Drive y un proyecto en [Google Cloud Console](https://console.cloud.google.com) para la autenticación de vídeos
- **VLC Media Player** instalado en cada PC que use el bot — [videolan.org](https://www.videolan.org)
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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `incidencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `preferencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

ALTER TABLE `videos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

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
pip install customtkinter pillow groq pymupdf python-docx openpyxl mysql-connector-python python-vlc google-auth google-auth-httplib2 google-api-python-client requests
```

### Paso 3 — Configurar el archivo `.env`

Crea un archivo llamado `.env` en la carpeta raíz del proyecto:

```env
# API de Groq
GROQ_API_KEY=gsk_XXXXXXXXXXXXXXXXXXXXXXXX

# Base de datos MySQL (Clever Cloud)
DB_HOST=tu-host.services.clever-cloud.com
DB_PORT=3306
DB_USER=tu_usuario_clever
DB_PASSWORD=tu_password_clever
DB_NAME=tu_nombre_bd_clever

# Google Drive Service Account (ruta al JSON descargado de Google Cloud)
DRIVE_SERVICE_ACCOUNT_FILE=service_account.json
```

> 🔑 Para obtener tu API Key de Groq: ve a [console.groq.com](https://console.groq.com) → **API Keys** → **Create API Key**

### Paso 4 — Colocar el Service Account de Google

Descarga el archivo `service_account.json` desde Google Cloud Console (ver sección [Google Drive](#-google-drive--tutoriales-en-vídeo)) y colócalo en la carpeta raíz del proyecto junto al `.env`.

### Paso 5 — Ejecutar la aplicación

```bash
python Corazon-IA.py
```

---

## ⚙️ Configuración

### Avatar personalizado

Coloca tus imágenes en la carpeta raíz del proyecto:
- `avatar.png` — Avatar circular del bot (cualquier tamaño, se recorta automáticamente)
- `avatar.ico` — Icono de la ventana y barra de tareas (formato `.ico`)

### Panel de personalización

Accede pulsando el botón **⚙️** en el header de la aplicación. Puedes cambiar:
- **Tema**: Claro / Oscuro
- **Color de acento**: Azul, Violeta, Verde, Rojo, Naranja o Rosa
- **Tamaño de fuente**: de 11 a 17 px

Las preferencias se guardan en la base de datos vinculadas a tu usuario y se aplican en cada inicio de sesión.

---

## ☁️ Google Drive — Tutoriales en vídeo

Los vídeos de tutorial ya **no necesitan estar en el PC local**. Se almacenan en Google Drive y el bot los descarga automáticamente cuando detecta una palabra clave en el chat. Una vez cerrado el reproductor, el archivo temporal se elimina solo.

### Paso 1 — Crear el Service Account en Google Cloud

1. Ve a [console.cloud.google.com](https://console.cloud.google.com)
2. Crea un proyecto nuevo o usa uno existente
3. Activa la **Google Drive API** → Biblioteca → busca "Drive API" → Activar
4. Ve a **IAM y administración → Cuentas de servicio → Crear cuenta de servicio**
5. Dale un nombre (ej: `digihelp-bot`) y continúa
6. Entra en la cuenta creada → **Claves → Añadir clave → JSON**
7. Descarga el archivo `.json`, renómbralo a `service_account.json` y ponlo en la carpeta del proyecto

### Paso 2 — Compartir los vídeos con el Service Account

1. Sube tus vídeos a Google Drive normalmente
2. Click derecho en el vídeo → **Compartir**
3. Pega el email del Service Account (algo como `digihelp-bot@tu-proyecto.iam.gserviceaccount.com`)
4. Dale permisos de **Lector**

### Paso 3 — Registrar el vídeo en la base de datos

En el campo `ruta_video` de la tabla `videos` puedes guardar cualquiera de estos formatos:

```sql
-- Solo el ID de Drive (recomendado)
INSERT INTO videos (palabra_clave, ruta_video, mensaje) VALUES
('impresora', '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs', '🖨️ Aquí tienes el tutorial de impresora.');

-- O la URL completa de Drive
INSERT INTO videos (palabra_clave, ruta_video, mensaje) VALUES
('vpn', 'https://drive.google.com/file/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs/view', '🔐 Guía para conectarte a la VPN.');
```

> 💡 El ID de Drive se encuentra en la URL del archivo: `https://drive.google.com/file/d/**ESTE_ES_EL_ID**/view`

> 💡 Las rutas locales (`videos/tutorial.mp4`) también siguen funcionando para compatibilidad con instalaciones anteriores.

### Cómo funciona internamente

```
Usuario escribe "impresora"
    → Bot detecta la palabra clave en la tabla videos
    → Muestra "⏳ Descargando tutorial desde Drive…"
    → Descarga el vídeo a un archivo temporal
    → VLC lo reproduce en una ventana independiente
    → Al cerrar el reproductor, el archivo temporal se elimina
```

---

## 🌍 Base de datos en la nube

La base de datos está alojada en **Clever Cloud** (MySQL gratuito), lo que permite usar el bot desde cualquier PC con internet sin depender de un servidor local como XAMPP.

### Migrar desde XAMPP a Clever Cloud

1. En phpMyAdmin → selecciona `digihelp` → **Exportar** → formato SQL → Continuar
2. Crea una cuenta en [clever-cloud.com](https://clever-cloud.com)
3. **Add an add-on → MySQL → Plan DEV** (gratuito)
4. Anota los datos de conexión que te proporciona Clever Cloud
5. Usa **DBeaver** ([dbeaver.io](https://dbeaver.io)) para conectarte a Clever Cloud e importar el `.sql`
6. Actualiza el `.env` con los datos de Clever Cloud

> ✅ El plan gratuito DEV de Clever Cloud soporta hasta 256 MB, más que suficiente para uso normal.

---

## 📁 Estructura del proyecto

```
DIGI_HELPBOT/
│
├── Corazon-IA.py              # Archivo principal de la aplicación
├── .env                       # Credenciales (no subir a Git)
├── service_account.json       # Credenciales Google Drive (no subir a Git)
├── preferencias.json          # Preferencias locales de fallback (autogenerado)
│
├── avatar.png                 # Avatar del bot (opcional)
├── avatar.ico                 # Icono de ventana (opcional)
│
└── videos/                    # Carpeta de vídeos locales (opcional, legacy)
    └── tutorial.mp4
```

> ⚠️ Añade `.env` y `service_account.json` a tu `.gitignore` para no exponer credenciales.

---

## 📦 Compilar a .exe

### Opción A — Auto PY to EXE (recomendado, interfaz gráfica)

1. Instala la herramienta:
```bash
pip install auto-py-to-exe
python -m auto_py_to_exe
```

2. Configura así:
   - **Script Location:** selecciona `Corazon-IA.py`
   - **Onefile:** ✅ One File
   - **Console Window:** ✅ Window Based (sin consola)
   - **Icon:** selecciona `avatar.ico` (opcional)
   - **Additional Files:** añade `avatar.png`, `avatar.ico`, `.env` y `service_account.json`

3. En la sección **Advanced** → campo `--collect-all`, añade:
```
groq
customtkinter
mysql
google
```

4. Pulsa **CONVERT .PY TO .EXE** 🚀

### Opción B — Línea de comandos

```bash
python -m PyInstaller --onefile --windowed ^
    --collect-all groq ^
    --collect-all customtkinter ^
    --collect-all google ^
    --add-data "avatar.png;." ^
    --add-data "avatar.ico;." ^
    --add-data ".env;." ^
    --add-data "service_account.json;." ^
    --icon "avatar.ico" ^
    --name "DigiHelp" ^
    Corazon-IA.py
```

> ⚠️ El `.env` y el `service_account.json` deben estar siempre en la **misma carpeta que el `.exe`**.

> 💡 El `.exe` generado solo funcionará en **Windows**. Para Mac/Linux hay que compilarlo en ese sistema operativo.

> 💡 Cada PC que use el bot necesita tener **VLC Media Player** instalado.

---

## 📖 Uso

| Acción | Cómo hacerlo |
|--------|--------------|
| Iniciar sesión | Introduce usuario y contraseña corporativos |
| Enviar mensaje | Escribe en el campo inferior y pulsa **Enter** o **Enviar ➤** |
| Adjuntar imagen | Pulsa **📎** → **🖼️ Imagen** → selecciona el archivo |
| Adjuntar documento | Pulsa **📎** → **📄 Documento** → selecciona PDF/Word/Excel/TXT |
| Ver tutorial en vídeo | Escribe una palabra clave configurada en la tabla `videos` (el bot descarga el vídeo de Drive automáticamente) |
| Nuevo chat | Pulsa **＋ Nuevo chat** en la sidebar |
| Retomar chat anterior | Haz clic en cualquier conversación de la sidebar |
| Ocultar sidebar | Pulsa el botón **☰** en la esquina superior izquierda |
| Personalizar apariencia | Pulsa el botón **⚙️** en el header |
| Cerrar sesión | Pulsa **⏻ Cerrar sesión** en la parte inferior de la sidebar |

---

## ❓ FAQ

**¿Es gratuito?**
Sí. GroqCloud y Clever Cloud ofrecen capas gratuitas más que suficientes para uso empresarial normal. Google Drive también es gratuito hasta 15 GB.

**¿Necesito internet para usarlo?**
Sí. El bot requiere internet para conectarse a la API de Groq, a la base de datos en Clever Cloud y para descargar los vídeos de Google Drive.

**¿Los datos se envían a la nube?**
Los mensajes e imágenes se envían a la API de Groq para procesarlos. El historial de conversaciones y la personalización se guardan en Clever Cloud asociados a tu usuario corporativo. Las credenciales nunca se exponen en el código.

**¿El bot funciona desde cualquier PC?**
Sí. Solo necesitas el `.exe` (o el `.py`), el `.env` con las credenciales y el `service_account.json` en la misma carpeta, además de VLC instalado y conexión a internet.

**El .exe no conecta a la base de datos, ¿qué hago?**
Asegúrate de que `.env` y `service_account.json` están en la **misma carpeta que el `.exe`**. Si el problema persiste, lanza el `.exe` desde consola para ver el error:
```bash
DigiHelp.exe
```

**El vídeo de Drive no se reproduce, ¿qué hago?**
Comprueba que el vídeo está compartido con el email del Service Account y que ese email tiene permisos de **Lector**. Revisa también que el ID o URL guardado en la columna `ruta_video` es correcto.

**¿Cómo cambio el nombre "DigiHelp AI" por el de mi empresa?**
Busca en el código `DigiHelp AI` y `DigiHelp` y reemplázalos. También puedes modificar el `SYSTEM_PROMPT` para personalizar el comportamiento de la IA.

**¿Puedo seguir usando vídeos locales en vez de Drive?**
Sí. Si en `ruta_video` guardas una ruta local (`videos/tutorial.mp4`), el bot la usa directamente sin tocar Drive. Ambos modos son compatibles a la vez.

---

<div align="center">

Hecho con ❤️ · [Reportar un bug](https://github.com/ElGolondras/DIGI_HELPBOT/issues)

</div>