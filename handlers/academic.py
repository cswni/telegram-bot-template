"""
Handler para información académica: carreras y admisión
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class AcademicHandler:
    def __init__(self, sheets_manager):
        self.sheets_manager = sheets_manager
    
    async def get_careers(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener listado de carreras disponibles"""
        try:
            careers_data = await self.sheets_manager.get_sheet_data('carreras')
            
            if not careers_data:
                error_message = "❌ No se pudo obtener la información de carreras en este momento."
                if update.callback_query:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await update.message.reply_text(error_message)
                return
            
            # Crear mensaje con las carreras
            message = "🎓 **Carreras Disponibles en la Universidad Martin Lutero:**\n\n"
            
            # Crear botones para cada carrera
            keyboard = []
            for career in careers_data:
                career_name = career.get('nombre', 'Sin nombre')
                career_id = career.get('id', '')
                message += f"• {career_name}\n"
                
                # Agregar botón para obtener más información
                keyboard.append([InlineKeyboardButton(
                    f"📚 {career_name}", 
                    callback_data=f"career_detail_{career_id}"
                )])
            
            # Agregar botón para requisitos de admisión
            keyboard.append([InlineKeyboardButton("📋 Requisitos de Admisión", callback_data="admission")])
            
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
            logger.error(f"Error al obtener carreras: {e}")
            error_message = "❌ Ocurrió un error al obtener la información de carreras."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def get_career_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE, career_id: str):
        """Obtener información detallada de una carrera específica"""
        try:
            careers_data = await self.sheets_manager.get_sheet_data('carreras')
            
            career = None
            for c in careers_data:
                if c.get('id') == career_id:
                    career = c
                    break
            
            if not career:
                await update.callback_query.edit_message_text(
                    "❌ No se encontró información para esta carrera."
                )
                return
            
            # Crear mensaje detallado
            message = f"""
🎓 **{career.get('nombre', 'Carrera')}**

📝 **Descripción:**
{career.get('descripcion', 'Sin descripción disponible')}

⏱️ **Duración:** {career.get('duracion', 'No especificada')}

📚 **Plan de Estudios:**
{career.get('plan_estudios', 'No disponible')}

💼 **Campo Laboral:**
{career.get('campo_laboral', 'No especificado')}

💰 **Costo por Semestre:** {career.get('costo', 'Consultar')}

📞 **Más información:** {career.get('contacto', 'Contactar admisión')}
            """
            
            # Botones de navegación
            keyboard = [
                [InlineKeyboardButton("🔙 Volver a Carreras", callback_data="careers")],
                [InlineKeyboardButton("📋 Requisitos de Admisión", callback_data="admission")],
                [InlineKeyboardButton("📞 Contactar", callback_data="contacts")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener detalle de carrera: {e}")
            await update.callback_query.edit_message_text(
                "❌ Ocurrió un error al obtener la información de la carrera."
            )
    
    async def get_admission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Obtener requisitos de admisión"""
        try:
            admission_data = await self.sheets_manager.get_sheet_data('admision')
            
            if not admission_data:
                error_message = "❌ No se pudo obtener la información de admisión en este momento."
                if update.callback_query:
                    await update.callback_query.edit_message_text(error_message)
                else:
                    await update.message.reply_text(error_message)
                return
            
            # Crear mensaje con requisitos
            message = "📋 **Requisitos de Admisión - Universidad Martin Lutero**\n\n"
            
            # Crear botones para cada categoría
            keyboard = []
            
            for req in admission_data:
                categoria = req.get('categoria', 'General')
                requisitos = req.get('requisitos', '')
                
                # Separar requisitos por comas y crear lista
                if requisitos:
                    requisitos_lista = [r.strip() for r in requisitos.split(',') if r.strip()]
                    
                    # Mostrar categoría con emoji
                    emoji_map = {
                        'documentos': '📄',
                        'academicos': '🎓',
                        'personales': '👤',
                        'económicos': '💰',
                        'medicos': '🏥',
                        'generales': '📋',
                        'general': '📋'
                    }
                    
                    emoji = emoji_map.get(categoria.lower(), '📋')
                    message += f"{emoji} **{categoria.upper()}**\n"
                    
                    # Mostrar primeros 3 requisitos como preview
                    for i, req_item in enumerate(requisitos_lista[:3]):
                        message += f"   • {req_item}\n"
                    
                    # Si hay más de 3 requisitos, mostrar indicador
                    if len(requisitos_lista) > 3:
                        message += f"   • ... y {len(requisitos_lista) - 3} más\n"
                    
                    message += "\n"
                    
                    # Agregar botón para ver todos los requisitos de esta categoría
                    keyboard.append([InlineKeyboardButton(
                        f"{emoji} Ver {categoria}", 
                        callback_data=f"admission_detail_{categoria.lower().replace(' ', '_')}"
                    )])
            
            # Agregar información adicional
            message += """
📞 **Para más información:**
• Contacta a la oficina de admisión
• Visita nuestra página web
• Llama al número de contacto de tu sede

🎯 **¡Tu futuro comienza aquí!**
            """
            
            # Botones de navegación
            keyboard.append([InlineKeyboardButton("🎓 Ver Carreras", callback_data="careers")])
            keyboard.append([InlineKeyboardButton("📞 Contactos", callback_data="contacts")])
            keyboard.append([InlineKeyboardButton("📅 Calendario", callback_data="calendar")])
            
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
            logger.error(f"Error al obtener requisitos de admisión: {e}")
            error_message = "❌ Ocurrió un error al obtener los requisitos de admisión."
            if update.callback_query:
                await update.callback_query.edit_message_text(error_message)
            else:
                await update.message.reply_text(error_message)
    
    async def get_admission_detail(self, update: Update, context: ContextTypes.DEFAULT_TYPE, categoria: str):
        """Obtener requisitos detallados de una categoría específica"""
        try:
            admission_data = await self.sheets_manager.get_sheet_data('admision')
            
            # Buscar la categoría específica
            categoria_data = None
            for req in admission_data:
                if req.get('categoria', '').lower().replace(' ', '_') == categoria:
                    categoria_data = req
                    break
            
            if not categoria_data:
                await update.callback_query.edit_message_text(
                    "❌ No se encontró información para esta categoría."
                )
                return
            
            categoria_nombre = categoria_data.get('categoria', 'General')
            requisitos = categoria_data.get('requisitos', '')
            
            # Separar requisitos por comas
            requisitos_lista = [r.strip() for r in requisitos.split(',') if r.strip()]
            
            # Crear mensaje detallado
            emoji_map = {
                'documentos': '📄',
                'academicos': '🎓',
                'personales': '👤',
                'económicos': '💰',
                'medicos': '🏥',
                'generales': '📋',
                'general': '📋'
            }
            
            emoji = emoji_map.get(categoria_nombre.lower(), '📋')
            
            message = f"{emoji} **{categoria_nombre.upper()}**\n\n"
            message += "📋 **Requisitos completos:**\n\n"
            
            # Mostrar todos los requisitos numerados
            for i, req_item in enumerate(requisitos_lista, 1):
                message += f"**{i}.** {req_item}\n"
            
            message += f"\n📊 **Total de requisitos:** {len(requisitos_lista)}\n\n"
            
            # Información adicional según la categoría
            if 'documentos' in categoria_nombre.lower():
                message += "💡 **Nota:** Todos los documentos deben estar actualizados y en buen estado.\n"
            elif 'academicos' in categoria_nombre.lower():
                message += "💡 **Nota:** Los requisitos académicos son obligatorios para el proceso de admisión.\n"
            elif 'económicos' in categoria_nombre.lower():
                message += "💡 **Nota:** Consulta con la oficina de admisión sobre opciones de pago y becas.\n"
            elif 'medicos' in categoria_nombre.lower():
                message += "💡 **Nota:** Los exámenes médicos deben ser realizados en centros autorizados.\n"
            
            # Botones de navegación
            keyboard = [
                [InlineKeyboardButton("🔙 Volver a Requisitos", callback_data="admission")],
                [InlineKeyboardButton("🎓 Ver Carreras", callback_data="careers")],
                [InlineKeyboardButton("📞 Contactos", callback_data="contacts")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error al obtener detalle de admisión: {e}")
            await update.callback_query.edit_message_text(
                "❌ Ocurrió un error al obtener los detalles de admisión."
            ) 