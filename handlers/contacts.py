"""
Handler para contactos de autoridades por sede
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class ContactsHandler:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
    
    async def get_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener contactos de autoridades por sede"""
        try:
            contacts_data = await self.sheets_manager.get_sheet_data('contactos')
            
            if not contacts_data:
                error_message = "❌ No se pudo obtener la información de contactos en este momento."
                if update.callback_query:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await update.message.reply_text(error_message)
                return
            
            # Verificar si se especificó una sede
            args = context.args
            if args:
                sede = ' '.join(args).lower()
                await self._get_contacts_by_sede(update, context, sede, contacts_data)
            else:
                await self._get_all_contacts(update, context, contacts_data)
                
        except Exception as e:
            logger.error(f"Error al obtener contactos: {e}")
            error_message = "❌ Ocurrió un error al obtener la información de contactos."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def _get_all_contacts(self, update: Update, context: ContextTypes.DEFAULT_TYPE, contacts_data: list):
        """Mostrar todas las sedes disponibles"""
        # Obtener sedes únicas
        sedes = list(set([contact.get('sede', '').lower() for contact in contacts_data if contact.get('sede')]))
        sedes.sort()
        
        message = "📞 **Contactos por Sede - Universidad Martin Lutero**\n\n"
        message += "Selecciona una sede para ver los contactos:\n\n"
        
        # Crear botones para cada sede
        keyboard = []
        for sede in sedes:
            sede_title = sede.title()
            keyboard.append([InlineKeyboardButton(
                f"🏢 {sede_title}", 
                callback_data=f"contacts_sede_{sede}"
            )])
        
        # Agregar botón para información general
        keyboard.append([InlineKeyboardButton("ℹ️ Información General", callback_data="contacts_general")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def _get_contacts_by_sede(self, update: Update, context: ContextTypes.DEFAULT_TYPE, sede: str, contacts_data: list):
        """Obtener contactos de una sede específica"""
        sede_contacts = [
            contact for contact in contacts_data 
            if contact.get('sede', '').lower() == sede
        ]
        
        if not sede_contacts:
            error_message = f"❌ No se encontraron contactos para la sede '{sede.title()}'."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
            return
        
        # Crear mensaje con contactos de la sede
        sede_title = sede.title()
        message = f"📞 **Contactos - Sede {sede_title}**\n\n"
        
        for contact in sede_contacts:
            nombre = contact.get('nombre', '')
            cargo = contact.get('cargo', '')
            telefono = contact.get('telefono', '')
            email = contact.get('email', '')
            horario = contact.get('horario', '')
            
            message += f"👤 **{nombre}**\n"
            if cargo:
                message += f"💼 {cargo}\n"
            if telefono:
                message += f"📱 {telefono}\n"
            if email:
                message += f"📧 {email}\n"
            if horario:
                message += f"🕒 {horario}\n"
            message += "\n"
        
        # Botones de navegación
        keyboard = [
            [InlineKeyboardButton("🔙 Todas las Sedes", callback_data="contacts")],
            [InlineKeyboardButton("📅 Calendario", callback_data="calendar")],
            [InlineKeyboardButton("💰 Pagos", callback_data="payments")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    
    async def handle_contacts_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, callback_data: str):
        """Manejar callbacks de contactos"""
        try:
            if callback_data == "contacts":
                contacts_data = await self.sheets_manager.get_sheet_data('contactos')
                await self._get_all_contacts(update, context, contacts_data)
            
            elif callback_data == "contacts_general":
                await self._get_general_info(update, context)
            
            elif callback_data.startswith("contacts_sede_"):
                sede = callback_data.replace("contacts_sede_", "")
                contacts_data = await self.sheets_manager.get_sheet_data('contactos')
                await self._get_contacts_by_sede(update, context, sede, contacts_data)
                
        except Exception as e:
            logger.error(f"Error en callback de contactos: {e}")
            await update.callback_query.edit_message_text(
                "❌ Ocurrió un error al obtener los contactos."
            )
    
    async def _get_general_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener información general de contacto"""
        message = """
ℹ️ **Información General - Universidad Martin Lutero**

📞 **Líneas de Atención:**
• Admisión: (505) XXXX-XXXX
• Finanzas: (505) XXXX-XXXX
• Soporte Técnico: (505) XXXX-XXXX

🌐 **Página Web:**
www.uml.edu.ni

📧 **Email General:**
info@uml.edu.ni

📱 **Redes Sociales:**
• Facebook: Universidad Martin Lutero
• Instagram: @uml_nicaragua
• Twitter: @UML_Nicaragua

🕒 **Horarios de Atención:**
Lunes a Viernes: 8:00 AM - 5:00 PM
Sábados: 8:00 AM - 12:00 PM

📍 **Sedes Principales:**
• Managua
• León
• Chinandega
• Jinotega
• Ocotal

Para contactos específicos por sede, selecciona la sede correspondiente.
        """
        
        # Botones de navegación
        keyboard = [
            [InlineKeyboardButton("🔙 Todas las Sedes", callback_data="contacts")],
            [InlineKeyboardButton("📅 Calendario", callback_data="calendar")],
            [InlineKeyboardButton("🎓 Carreras", callback_data="careers")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        ) 