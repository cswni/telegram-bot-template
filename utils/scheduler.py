"""
Utilidad para programación de recordatorios automáticos
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from handlers.payments import PaymentsHandler

logger = logging.getLogger(__name__)

class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_user_ids = self._parse_admin_ids()
        self.bot = None
        self.payments_handler = None
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
    def _parse_admin_ids(self) -> List[int]:
        """Parsear IDs de administradores desde variable de entorno"""
        admin_ids_str = os.getenv('ADMIN_USER_IDS', '')
        if not admin_ids_str:
            return []
        
        try:
            return [int(uid.strip()) for uid in admin_ids_str.split(',') if uid.strip()]
        except ValueError:
            logger.error("Error al parsear ADMIN_USER_IDS")
            return []
    
    def set_payments_handler(self, payments_handler: PaymentsHandler):
        """Establecer el handler de pagos para recordatorios"""
        self.payments_handler = payments_handler
    
    def start(self):
        """Iniciar el scheduler"""
        try:
            # Configurar jobs
            self._setup_jobs()
            
            # Iniciar scheduler
            self.scheduler.start()
            logger.info("Scheduler iniciado correctamente")
            
        except Exception as e:
            logger.error(f"Error al iniciar scheduler: {e}")
    
    def stop(self):
        """Detener el scheduler"""
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler detenido")
        except Exception as e:
            logger.error(f"Error al detener scheduler: {e}")
    
    def _setup_jobs(self):
        """Configurar jobs programados"""
        
        # Recordatorio diario de pagos (9:00 AM)
        self.scheduler.add_job(
            self._daily_payment_reminder,
            CronTrigger(hour=9, minute=5),
            id='daily_payment_reminder',
            name='Recordatorio diario de pagos'
        )
        
        # Recordatorio semanal de eventos (Lunes 8:00 AM)
        self.scheduler.add_job(
            self._weekly_events_reminder,
            CronTrigger(day_of_week='mon', hour=9, minute=6),
            id='weekly_events_reminder',
            name='Recordatorio semanal de eventos'
        )
        
        # Limpieza de caché (Domingo 2:00 AM)
        self.scheduler.add_job(
            self._clear_cache_job,
            CronTrigger(day_of_week='sun', hour=2, minute=0),
            id='clear_cache_job',
            name='Limpieza de caché semanal'
        )
        
        # Verificación de salud del bot (cada 6 horas)
        self.scheduler.add_job(
            self._health_check,
            CronTrigger(hour='*/6'),
            id='health_check',
            name='Verificación de salud del bot'
        )
    
    async def _daily_payment_reminder(self):
        """Recordatorio diario de pagos próximos"""
        try:
            if not self.payments_handler or not self.bot:
                return
            
            # Obtener pagos urgentes (próximos 7 días)
            urgent_payments = self.payments_handler.get_urgent_payments()
            
            if not urgent_payments:
                return
            
            # Crear mensaje de recordatorio
            message = "💰 **Recordatorio de Pagos - Universidad Martin Lutero**\n\n"
            message += "Tienes pagos próximos a vencer:\n\n"
            
            for payment in urgent_payments[:5]:  # Máximo 5 pagos
                fecha_str = payment['fecha'].strftime('%d/%m/%Y')
                dias = payment['dias_restantes']
                
                message += f"📅 **{fecha_str}** ({dias} días)\n"
                message += f"💳 {payment['concepto']}\n"
                if payment['monto']:
                    message += f"💰 ${payment['monto']}\n"
                message += "\n"
            
            if len(urgent_payments) > 5:
                message += f"... y {len(urgent_payments) - 5} pagos más\n\n"
            
            message += "⚠️ **Recuerda realizar tus pagos a tiempo para evitar sanciones.**\n\n"
            message += "Usa /pagos para ver todos los pagos programados."
            
            # Enviar a administradores
            for admin_id in self.admin_user_ids:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error al enviar recordatorio a admin {admin_id}: {e}")
            
            logger.info(f"Recordatorio de pagos enviado a {len(self.admin_user_ids)} administradores")
            
        except Exception as e:
            logger.error(f"Error en recordatorio diario de pagos: {e}")
    
    async def _weekly_events_reminder(self):
        """Recordatorio semanal de eventos"""
        try:
            if not self.bot:
                return
            
            # Crear mensaje de eventos semanales
            message = "📅 **Eventos de la Semana - Universidad Martin Lutero**\n\n"
            message += "Esta semana tendremos los siguientes eventos:\n\n"
            message += "🎓 **Eventos Académicos:**\n"
            message += "• Revisa el calendario académico\n"
            message += "• Consulta con tu coordinador\n\n"
            message += "📚 **Actividades Estudiantiles:**\n"
            message += "• Participa en las actividades programadas\n"
            message += "• Mantente informado de los eventos\n\n"
            message += "Usa /eventos para ver todos los eventos próximos."
            
            # Enviar a administradores
            for admin_id in self.admin_user_ids:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error al enviar recordatorio de eventos a admin {admin_id}: {e}")
            
            logger.info(f"Recordatorio de eventos enviado a {len(self.admin_user_ids)} administradores")
            
        except Exception as e:
            logger.error(f"Error en recordatorio semanal de eventos: {e}")
    
    async def _clear_cache_job(self):
        """Job para limpiar caché semanalmente"""
        try:
            # Esta función se puede expandir para limpiar caché de Google Sheets
            logger.info("Job de limpieza de caché ejecutado")
            
        except Exception as e:
            logger.error(f"Error en job de limpieza de caché: {e}")
    
    async def _health_check(self):
        """Verificación de salud del bot"""
        try:
            if not self.bot:
                return
            
            # Verificar que el bot esté funcionando
            me = await self.bot.get_me()
            logger.info(f"Health check: Bot {me.first_name} está funcionando correctamente")
            
        except Exception as e:
            logger.error(f"Error en health check: {e}")
    
    async def send_urgent_notification(self, message: str, user_ids: List[int] = None):
        """Enviar notificación urgente a usuarios específicos"""
        try:
            if not self.bot:
                return
            
            target_users = user_ids if user_ids else self.admin_user_ids
            
            for user_id in target_users:
                try:
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Error al enviar notificación urgente a {user_id}: {e}")
            
            logger.info(f"Notificación urgente enviada a {len(target_users)} usuarios")
            
        except Exception as e:
            logger.error(f"Error al enviar notificación urgente: {e}")
    
    def get_job_status(self) -> Dict:
        """Obtener estado de los jobs programados"""
        try:
            jobs = self.scheduler.get_jobs()
            job_status = {}
            
            for job in jobs:
                job_status[job.id] = {
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'active': job.next_run_time is not None
                }
            
            return job_status
            
        except Exception as e:
            logger.error(f"Error al obtener estado de jobs: {e}")
            return {} 