"""
Handler para calendario académico y eventos
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class CalendarHandler:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
    
    async def get_calendar(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener calendario académico"""
        try:
            calendar_data = await self.sheets_manager.get_sheet_data('calendario')
            
            if not calendar_data:
                error_message = "❌ No se pudo obtener el calendario académico en este momento."
                if update.callback_query:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await update.message.reply_text(error_message)
                return
            
            # Filtrar eventos futuros y ordenar por fecha
            current_date = datetime.now()
            future_events = []
            
            for event in calendar_data:
                try:
                    event_date = datetime.strptime(event.get('fecha', ''), '%Y-%m-%d')
                    if event_date >= current_date:
                        future_events.append({
                            'fecha': event_date,
                            'evento': event.get('evento', ''),
                            'descripcion': event.get('descripcion', ''),
                            'tipo': event.get('tipo', 'General')
                        })
                except ValueError:
                    continue
            
            # Ordenar por fecha
            future_events.sort(key=lambda x: x['fecha'])
            
            if not future_events:
                no_events_message = "📅 No hay eventos programados en el calendario académico."
                if update.callback_query:
                    await update.callback_query.edit_message_text(no_events_message)
                else:
                    await update.message.reply_text(no_events_message)
                return
            
            # Crear mensaje del calendario
            message = "📅 **Calendario Académico - Universidad Martin Lutero**\n\n"
            
            # Mostrar próximos 10 eventos
            for i, event in enumerate(future_events[:10]):
                fecha_str = event['fecha'].strftime('%d/%m/%Y')
                tipo_emoji = self._get_event_emoji(event['tipo'])
                
                message += f"{tipo_emoji} **{fecha_str}** - {event['evento']}\n"
                if event['descripcion']:
                    message += f"   _{event['descripcion']}_\n"
                message += "\n"
            
            if len(future_events) > 10:
                message += f"... y {len(future_events) - 10} eventos más\n\n"
            
            # Botones de navegación
            keyboard = [
                [InlineKeyboardButton("📅 Ver Eventos", callback_data="events")],
                [InlineKeyboardButton("💰 Pagos", callback_data="payments")],
                [InlineKeyboardButton("🎓 Carreras", callback_data="careers")]
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
            
        except Exception as e:
            logger.error(f"Error al obtener calendario: {e}")
            error_message = "❌ Ocurrió un error al obtener el calendario académico."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def get_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener eventos universitarios"""
        try:
            events_data = await self.sheets_manager.get_sheet_data('eventos')
            
            if not events_data:
                error_message = "❌ No se pudo obtener la información de eventos en este momento."
                if update.callback_query:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await update.message.reply_text(error_message)
                return
            
            # Filtrar eventos próximos (próximos 30 días)
            current_date = datetime.now()
            upcoming_events = []
            
            for event in events_data:
                try:
                    event_date = datetime.strptime(event.get('fecha', ''), '%Y-%m-%d')
                    if event_date >= current_date and event_date <= current_date + timedelta(days=30):
                        upcoming_events.append({
                            'fecha': event_date,
                            'titulo': event.get('titulo', ''),
                            'descripcion': event.get('descripcion', ''),
                            'lugar': event.get('lugar', ''),
                            'tipo': event.get('tipo', 'General')
                        })
                except ValueError:
                    continue
            
            # Ordenar por fecha
            upcoming_events.sort(key=lambda x: x['fecha'])
            
            if not upcoming_events:
                no_events_message = "📅 No hay eventos próximos programados."
                if update.callback_query:
                    await update.callback_query.edit_message_text(no_events_message)
                else:
                    await update.message.reply_text(no_events_message)
                return
            
            # Crear mensaje de eventos
            message = "🎉 **Eventos Próximos - Universidad Martin Lutero**\n\n"
            
            for event in upcoming_events:
                fecha_str = event['fecha'].strftime('%d/%m/%Y')
                tipo_emoji = self._get_event_emoji(event['tipo'])
                
                message += f"{tipo_emoji} **{event['titulo']}**\n"
                message += f"📅 {fecha_str}\n"
                if event['lugar']:
                    message += f"📍 {event['lugar']}\n"
                if event['descripcion']:
                    message += f"📝 {event['descripcion']}\n"
                message += "\n"
            
            # Botones de navegación
            keyboard = [
                [InlineKeyboardButton("📅 Calendario Completo", callback_data="calendar")],
                [InlineKeyboardButton("💰 Pagos", callback_data="payments")],
                [InlineKeyboardButton("📞 Contactos", callback_data="contacts")]
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
            
        except Exception as e:
            logger.error(f"Error al obtener eventos: {e}")
            error_message = "❌ Ocurrió un error al obtener los eventos."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    def _get_event_emoji(self, event_type: str) -> str:
        """Obtener emoji según el tipo de evento"""
        emoji_map = {
            'academico': '📚',
            'pago': '💰',
            'graduacion': '🎓',
            'cultural': '🎭',
            'deportivo': '⚽',
            'conferencia': '🎤',
            'taller': '🔧',
            'examen': '📝',
            'vacaciones': '🏖️',
            'general': '📅'
        }
        return emoji_map.get(event_type.lower(), '📅') 