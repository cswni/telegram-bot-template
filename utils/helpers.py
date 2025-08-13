"""
Funciones auxiliares para el bot
"""

import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def format_date(date_str: str, input_format: str = '%Y-%m-%d', output_format: str = '%d/%m/%Y') -> str:
    """Formatear fecha de un formato a otro"""
    try:
        date_obj = datetime.strptime(date_str, input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        logger.warning(f"No se pudo formatear la fecha: {date_str}")
        return date_str

def parse_date_range(date_range: str) -> tuple:
    """Parsear rango de fechas (ej: '2024-01-01 to 2024-12-31')"""
    try:
        dates = date_range.split(' to ')
        if len(dates) == 2:
            start_date = datetime.strptime(dates[0].strip(), '%Y-%m-%d')
            end_date = datetime.strptime(dates[1].strip(), '%Y-%m-%d')
            return start_date, end_date
    except (ValueError, AttributeError):
        pass
    return None, None

def clean_text(text: str) -> str:
    """Limpiar texto de caracteres especiales y normalizar"""
    if not text:
        return ""
    
    # Remover caracteres especiales pero mantener acentos
    text = re.sub(r'[^\w\sáéíóúÁÉÍÓÚñÑ.,!?¿¡-]', '', text)
    
    # Normalizar espacios
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def extract_keywords(text: str) -> List[str]:
    """Extraer palabras clave de un texto"""
    if not text:
        return []
    
    # Limpiar texto
    clean_text_str = clean_text(text.lower())
    
    # Palabras comunes a ignorar
    stop_words = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'y', 'o', 'pero', 'si', 'no', 'que', 'cual', 'quien',
        'como', 'cuando', 'donde', 'por', 'para', 'con', 'sin',
        'sobre', 'entre', 'detras', 'delante', 'encima', 'debajo',
        'es', 'son', 'está', 'están', 'tiene', 'tienen', 'hay',
        'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas'
    }
    
    # Extraer palabras
    words = re.findall(r'\b\w+\b', clean_text_str)
    
    # Filtrar palabras cortas y stop words
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    return keywords

def match_keywords(text: str, keywords: List[str]) -> float:
    """Calcular similitud entre texto y palabras clave"""
    if not text or not keywords:
        return 0.0
    
    text_keywords = set(extract_keywords(text))
    target_keywords = set(keywords)
    
    if not target_keywords:
        return 0.0
    
    # Calcular similitud Jaccard
    intersection = len(text_keywords.intersection(target_keywords))
    union = len(text_keywords.union(target_keywords))
    
    return intersection / union if union > 0 else 0.0

def format_currency(amount: str) -> str:
    """Formatear cantidad monetaria"""
    try:
        # Remover caracteres no numéricos excepto punto y coma
        clean_amount = re.sub(r'[^\d.,]', '', str(amount))
        
        # Convertir a float
        if ',' in clean_amount and '.' in clean_amount:
            # Formato europeo: 1.234,56
            clean_amount = clean_amount.replace('.', '').replace(',', '.')
        elif ',' in clean_amount:
            # Formato con coma como separador decimal
            clean_amount = clean_amount.replace(',', '.')
        
        amount_float = float(clean_amount)
        
        # Formatear con separadores de miles
        return f"${amount_float:,.2f}"
        
    except (ValueError, TypeError):
        return str(amount)

def validate_email(email: str) -> bool:
    """Validar formato de email"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validar formato de teléfono"""
    if not phone:
        return False
    
    # Remover espacios, guiones y paréntesis
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Validar formato nicaragüense
    pattern = r'^(\+505|505)?[2-8]\d{7}$'
    return bool(re.match(pattern, clean_phone))

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncar texto a una longitud máxima"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def split_message(text: str, max_length: int = 4096) -> List[str]:
    """Dividir mensaje largo en partes más pequeñas"""
    if not text or len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    # Dividir por líneas
    lines = text.split('\n')
    
    for line in lines:
        # Si agregar esta línea excede el límite
        if len(current_part) + len(line) + 1 > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = line
            else:
                # La línea es muy larga, dividirla
                while len(line) > max_length:
                    parts.append(line[:max_length])
                    line = line[max_length:]
                current_part = line
        else:
            current_part += '\n' + line if current_part else line
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def create_inline_keyboard(buttons: List[List[Dict]], max_buttons_per_row: int = 2) -> List[List]:
    """Crear teclado inline con botones"""
    keyboard = []
    current_row = []
    
    for button in buttons:
        current_row.append(button)
        
        if len(current_row) >= max_buttons_per_row:
            keyboard.append(current_row)
            current_row = []
    
    if current_row:
        keyboard.append(current_row)
    
    return keyboard

def get_emoji_for_category(category: str) -> str:
    """Obtener emoji para una categoría"""
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
        'general': '📅',
        'admision': '📋',
        'contacto': '📞',
        'evento': '🎉',
        'recordatorio': '⏰',
        'urgente': '🚨',
        'info': 'ℹ️'
    }
    
    return emoji_map.get(category.lower(), '📌')

def format_duration(days: int) -> str:
    """Formatear duración en días a texto legible"""
    if days == 0:
        return "hoy"
    elif days == 1:
        return "mañana"
    elif days < 7:
        return f"en {days} días"
    elif days < 30:
        weeks = days // 7
        return f"en {weeks} semana{'s' if weeks > 1 else ''}"
    else:
        months = days // 30
        return f"en {months} mes{'es' if months > 1 else ''}"

def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    # Remover caracteres no permitidos
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Limitar longitud
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename.strip()

def is_weekend(date: datetime) -> bool:
    """Verificar si una fecha es fin de semana"""
    return date.weekday() >= 5

def get_business_days(start_date: datetime, end_date: datetime) -> int:
    """Calcular días hábiles entre dos fechas"""
    business_days = 0
    current_date = start_date
    
    while current_date <= end_date:
        if not is_weekend(current_date):
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days 