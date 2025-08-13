"""
Handler para información de pagos y recordatorios
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class PaymentsHandler:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
    
    async def get_payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener información de pagos próximos"""
        try:
            payments_data = await self.sheets_manager.get_sheet_data('pagos')
            
            if not payments_data:
                error_message = "❌ No se pudo obtener la información de pagos en este momento."
                if update.callback_query:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await update.message.reply_text(error_message)
                return
            
            # Filtrar pagos futuros y ordenar por fecha
            current_date = datetime.now()
            upcoming_payments = []
            
            for payment in payments_data:
                try:
                    payment_date = datetime.strptime(payment.get('fecha', ''), '%Y-%m-%d')
                    if payment_date >= current_date:
                        upcoming_payments.append({
                            'fecha': payment_date,
                            'concepto': payment.get('concepto', ''),
                            'monto': payment.get('monto', ''),
                            'carrera': payment.get('carrera', 'Todas'),
                            'descripcion': payment.get('descripcion', ''),
                            'tipo': payment.get('tipo', 'General')
                        })
                except ValueError:
                    continue
            
            # Ordenar por fecha
            upcoming_payments.sort(key=lambda x: x['fecha'])
            
            if not upcoming_payments:
                no_payments_message = "💰 No hay pagos programados próximamente."
                if update.callback_query:
                    await update.callback_query.edit_message_text(no_payments_message)
                else:
                    await update.message.reply_text(no_payments_message)
                return
            
            # Crear mensaje de pagos
            message = "💰 **Próximos Pagos - Universidad Martin Lutero**\n\n"
            
            # Mostrar próximos 8 pagos
            for i, payment in enumerate(upcoming_payments[:8]):
                fecha_str = payment['fecha'].strftime('%d/%m/%Y')
                dias_restantes = (payment['fecha'] - current_date).days
                
                message += f"📅 **{fecha_str}** ({dias_restantes} días)\n"
                message += f"💳 {payment['concepto']}\n"
                if payment['monto']:
                    message += f"💰 ${payment['monto']}\n"
                if payment['carrera'] != 'Todas':
                    message += f"🎓 {payment['carrera']}\n"
                if payment['descripcion']:
                    message += f"📝 {payment['descripcion']}\n"
                message += "\n"
            
            if len(upcoming_payments) > 8:
                message += f"... y {len(upcoming_payments) - 8} pagos más\n\n"
            
            # Información adicional
            message += """
💡 **Recordatorios importantes:**
• Los pagos se pueden realizar en línea o en la oficina
• Mantén al día tus obligaciones para evitar sanciones
• Consulta con tu coordinador si tienes dudas

📞 **Para más información:**
Contacta a la oficina de finanzas de tu sede
            """
            
            # Botones de navegación
            keyboard = [
                [InlineKeyboardButton("📅 Calendario", callback_data="calendar")],
                [InlineKeyboardButton("📞 Contactos", callback_data="contacts")],
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
            logger.error(f"Error al obtener pagos: {e}")
            error_message = "❌ Ocurrió un error al obtener la información de pagos."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def get_payment_methods(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener métodos de pago disponibles"""
        try:
            # Información de métodos de pago
            message = """
💳 **Métodos de Pago - Universidad Martin Lutero**

**Opciones disponibles:**

🏦 **Pago en Línea:**
• Portal estudiantil
• Transferencia bancaria
• Tarjeta de crédito/débito

🏢 **Pago en Oficina:**
• Efectivo
• Cheque
• Tarjeta de crédito/débito

📱 **Pago Móvil:**
• Aplicaciones bancarias
• Transferencias instantáneas

**Información importante:**
• Guarda siempre tu comprobante de pago
• Los pagos se procesan en 24-48 horas
• Consulta el estado de tu cuenta en el portal

📞 **Soporte:**
Contacta a finanzas si tienes problemas con tu pago
            """
            
            # Botones de navegación
            keyboard = [
                [InlineKeyboardButton("💰 Ver Pagos", callback_data="payments")],
                [InlineKeyboardButton("📞 Contactos", callback_data="contacts")],
                [InlineKeyboardButton("📅 Calendario", callback_data="calendar")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener métodos de pago: {e}")
            await update.message.reply_text(
                "❌ Ocurrió un error al obtener los métodos de pago."
            )
    
    def get_urgent_payments(self) -> list:
        """Obtener pagos urgentes (próximos 7 días)"""
        try:
            payments_data = self.sheets_manager.get_sheet_data_sync('pagos')
            if not payments_data:
                return []
            
            current_date = datetime.now()
            urgent_payments = []
            
            for payment in payments_data:
                try:
                    payment_date = datetime.strptime(payment.get('fecha', ''), '%Y-%m-%d')
                    days_until = (payment_date - current_date).days
                    
                    if 0 <= days_until <= 7:
                        urgent_payments.append({
                            'fecha': payment_date,
                            'concepto': payment.get('concepto', ''),
                            'monto': payment.get('monto', ''),
                            'dias_restantes': days_until
                        })
                except ValueError:
                    continue
            
            return urgent_payments
            
        except Exception as e:
            logger.error(f"Error al obtener pagos urgentes: {e}")
            return [] 