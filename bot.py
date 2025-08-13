#!/usr/bin/env python3
"""
Bot de Telegram para la Universidad Martin Lutero, Nicaragua
Script principal del bot
"""

import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from handlers.academic import AcademicHandler
from handlers.calendar import CalendarHandler
from handlers.payments import PaymentsHandler
from handlers.contacts import ContactsHandler
from utils.scheduler import Scheduler
from utils.gsheets import GoogleSheetsManager

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class UMBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN no está configurado en .env")
        
        self.application = Application.builder().token(self.token).build()
        self.sheets_manager = GoogleSheetsManager()
        self.scheduler = Scheduler()
        
        # Inicializar handlers
        self.academic_handler = AcademicHandler(self.sheets_manager)
        self.calendar_handler = CalendarHandler(self.sheets_manager)
        self.payments_handler = PaymentsHandler(self.sheets_manager)
        self.contacts_handler = ContactsHandler(self.sheets_manager)
        
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurar todos los handlers del bot"""
        
        # Comandos principales
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        
        # Handlers específicos
        self.application.add_handler(CommandHandler("calendario", self.calendar_handler.get_calendar))
        self.application.add_handler(CommandHandler("pagos", self.payments_handler.get_payments))
        self.application.add_handler(CommandHandler("eventos", self.calendar_handler.get_events))
        self.application.add_handler(CommandHandler("carreras", self.academic_handler.get_careers))
        self.application.add_handler(CommandHandler("admision", self.academic_handler.get_admission))
        self.application.add_handler(CommandHandler("contactos", self.contacts_handler.get_contacts))
        
        # Callback queries para botones inline
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Mensaje de bienvenida"""
        user = update.effective_user
        welcome_message = f"""
🤖 ¡Hola {user.first_name}! 

Bienvenido al Bot de la Universidad Martin Lutero, Nicaragua.

Soy tu asistente virtual y puedo ayudarte con:

📅 Calendario académico y eventos
💰 Información sobre pagos
🎓 Carreras y requisitos de admisión
📞 Contactos de autoridades

Usa /menu para ver todas las opciones disponibles o /help para más información.

¡Estoy aquí para ayudarte! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📅 Calendario", callback_data="calendar")],
            [InlineKeyboardButton("💰 Pagos", callback_data="payments")],
            [InlineKeyboardButton("🎓 Carreras", callback_data="careers")],
            [InlineKeyboardButton("📞 Contactos", callback_data="contacts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Información de ayuda"""
        help_text = """
🤖 **Comandos disponibles:**

**Comandos principales:**
/start - Mensaje de bienvenida
/help - Esta ayuda
/menu - Menú principal

**Información académica:**
/calendario - Calendario académico
/pagos - Próximas fechas de pago
/eventos - Eventos universitarios
/carreras - Listado de carreras
/admision - Requisitos de admisión

**Contactos y soporte:**
/contactos [sede] - Contactos por sede

**Ejemplos:**
/contactos Managua
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /menu - Menú principal con botones"""
        keyboard = [
            [InlineKeyboardButton("📅 Calendario Académico", callback_data="calendar")],
            [InlineKeyboardButton("💰 Información de Pagos", callback_data="payments")],
            [InlineKeyboardButton("🎓 Carreras Disponibles", callback_data="careers")],
            [InlineKeyboardButton("📋 Requisitos de Admisión", callback_data="admission")],
            [InlineKeyboardButton("📞 Contactos por Sede", callback_data="contacts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 **Menú Principal**\nSelecciona una opción:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Manejar callbacks de botones inline"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "calendar":
            await self.calendar_handler.get_calendar(update, context)
        elif query.data == "payments":
            await self.payments_handler.get_payments(update, context)
        elif query.data == "careers":
            await self.academic_handler.get_careers(update, context)
        elif query.data == "admission":
            await self.academic_handler.get_admission(update, context)
        elif query.data.startswith("admission_detail_"):
            categoria = query.data.replace("admission_detail_", "")
            await self.academic_handler.get_admission_detail(update, context, categoria)
        elif query.data == "contacts":
            await self.contacts_handler.get_contacts(update, context)
        elif query.data == "events":
            await self.calendar_handler.get_events(update, context)
        elif query.data.startswith("career_detail_"):
            career_id = query.data.replace("career_detail_", "")
            await self.academic_handler.get_career_detail(update, context, career_id)
        elif query.data.startswith("contacts_sede_"):
            sede = query.data.replace("contacts_sede_", "")
            await self.contacts_handler.handle_contacts_callback(update, context, f"contacts_sede_{sede}")
        elif query.data == "contacts_general":
            await self.contacts_handler.handle_contacts_callback(update, context, "contacts_general")
    
    def run(self):
        """Ejecutar el bot"""
        logger.info("Iniciando bot de la Universidad Martin Lutero...")
        
        # Iniciar el scheduler para recordatorios
        self.scheduler.start()
        
        # Ejecutar el bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Función principal"""
    try:
        bot = UMBot()
        bot.run()
    except Exception as e:
        logger.error(f"Error al iniciar el bot: {e}")
        raise

if __name__ == '__main__':
    main() 