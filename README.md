# README - Bot de Telegram para la Universidad Martin Lutero, Nicaragua

## Descripción
Este proyecto es un bot de Telegram desarrollado en Python para la Universidad Martin Lutero en Nicaragua. El bot proporciona información académica, recordatorios y asistencia a estudiantes, incluyendo:

- Recordatorios de fechas de pagos
- Calendario académico
- Eventos universitarios
- Información sobre carreras específicas
- Requisitos de admisión
- Datos de contacto de autoridades por sede
- Funcionalidad de preguntas y respuestas mediante integración con n8n

## Características principales
- Interacción amigable mediante comandos de Telegram
- Integración con Google Sheets como base de conocimiento
- Conexión con API de n8n para preguntas y respuestas
- Recordatorios automáticos de fechas importantes
- Fácil mantenimiento y actualización de información

## Requisitos previos
- Python 3.8 o superior
- Cuenta de Telegram y token de bot (obtener de @BotFather)
- Acceso a una hoja de cálculo de Google Sheets con la información requerida
- Flujo n8n configurado y accesible mediante API
- Cuenta de servicio de Google para la API de Sheets

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/umbot-telegram.git
cd umbot-telegram
```

2. Crear y activar un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

1. Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:
```ini
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
GOOGLE_SHEETS_ID=id_de_tu_hoja_de_calculo
GOOGLE_CREDENTIALS_FILE=credentials.json
N8N_API_URL=https://tu-instancia-n8n.com/webhook/preguntas
N8N_API_KEY=tu_api_key_de_n8n
```

2. Para las credenciales de Google Sheets:
   - Habilitar la API de Google Sheets en Google Cloud Console
   - Crear una cuenta de servicio y descargar el archivo JSON de credenciales
   - Colocar el archivo como `credentials.json` en la raíz del proyecto
   - Compartir tu hoja de cálculo con el email de la cuenta de servicio

## Estructura del proyecto
```
umbot-telegram/
├── bot.py                # Script principal del bot
├── handlers/             # Manejadores de comandos
│   ├── __init__.py
│   ├── academic.py       # Info académica y carreras
│   ├── calendar.py       # Calendario y eventos
│   ├── payments.py       # Recordatorios de pagos
│   └── contacts.py       # Contactos de autoridades
├── utils/
│   ├── __init__.py
│   ├── gsheets.py        # Conexión con Google Sheets
│   ├── scheduler.py      # Programación de recordatorios
│   └── helpers.py        # Funciones auxiliares
├── requirements.txt      # Dependencias
├── .env.example          # Ejemplo de configuración
└── README.md             # Este archivo
```

## Comandos disponibles
- `/start` - Mensaje de bienvenida y ayuda
- `/calendario` - Mostrar calendario académico
- `/pagos` - Próximas fechas de pago
- `/eventos` - Eventos universitarios próximos
- `/carreras` - Listado de carreras disponibles
- `/carrera [nombre]` - Información específica de una carrera
- `/admision` - Requisitos de admisión (interactivo por categorías)
- `/contactos [sede]` - Contactos de autoridades por sede




## Estructura de Google Sheets
El bot espera una hoja de cálculo con las siguientes pestañas:
1. `carreras` - Información detallada de cada carrera
2. `calendario` - Fechas académicas importantes
3. `pagos` - Cronograma de pagos
4. `eventos` - Eventos universitarios
5. `admision` - Requisitos de admisión (categorías y requisitos separados por comas)
6. `contactos` - Datos de contacto por sede

Para más detalles sobre la estructura de la hoja de admisión, consulta `GOOGLE_SHEETS_STRUCTURE.md`

## Despliegue
El bot puede ejecutarse localmente durante desarrollo:
```bash
python bot.py
```

Para producción, se recomienda:
1. Servidor con sistema operativo Linux
2. Usar PM2, Supervisor o systemd para mantener el proceso activo
3. Configurar un proxy inverso si es necesario

Ejemplo con PM2:
```bash
pm2 start bot.py --name "um-bot" --interpreter python3
pm2 save
pm2 startup
```

## Mantenimiento
Para actualizar la información:
1. Modificar los datos en Google Sheets
2. Algunos cambios requieren reiniciar el bot para recargar la caché

## Contribución
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia
Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## Contacto
Para soporte o preguntas:
- [Tu nombre o equipo]
- [Email de contacto]
- [Otros medios de contacto]