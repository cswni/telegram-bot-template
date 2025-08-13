"""
Utilidad para manejo de Google Sheets
"""

import os
import logging
import asyncio
from typing import List, Dict, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    def __init__(self):
        self.sheets_id = os.getenv('GOOGLE_SHEETS_ID')
        self.credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        self.service = None
        self._cache = {}
        self._cache_timestamps = {}
        self._cache_duration = 300  # 5 minutos
        
        if not self.sheets_id:
            logger.warning("GOOGLE_SHEETS_ID no está configurado")
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Inicializar el servicio de Google Sheets"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.error(f"Archivo de credenciales no encontrado: {self.credentials_file}")
                return
            
            # Configurar credenciales
            scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
            credentials = Credentials.from_service_account_file(
                self.credentials_file, 
                scopes=scopes
            )
            
            # Crear servicio
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Servicio de Google Sheets inicializado correctamente")
            
        except Exception as e:
            logger.error(f"Error al inicializar Google Sheets: {e}")
            self.service = None
    
    async def get_sheet_data(self, sheet_name: str) -> List[Dict]:
        """Obtener datos de una hoja específica de forma asíncrona"""
        try:
            # Verificar caché
            if self._is_cache_valid(sheet_name):
                return self._cache.get(sheet_name, [])
            
            # Ejecutar en thread separado para no bloquear
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, 
                self._fetch_sheet_data, 
                sheet_name
            )
            
            # Actualizar caché
            self._update_cache(sheet_name, data)
            return data
            
        except Exception as e:
            logger.error(f"Error al obtener datos de {sheet_name}: {e}")
            return []
    
    def get_sheet_data_sync(self, sheet_name: str) -> List[Dict]:
        """Obtener datos de una hoja específica de forma síncrona"""
        try:
            # Verificar caché
            if self._is_cache_valid(sheet_name):
                return self._cache.get(sheet_name, [])
            
            # Obtener datos
            data = self._fetch_sheet_data(sheet_name)
            
            # Actualizar caché
            self._update_cache(sheet_name, data)
            return data
            
        except Exception as e:
            logger.error(f"Error al obtener datos de {sheet_name}: {e}")
            return []
    
    def _fetch_sheet_data(self, sheet_name: str) -> List[Dict]:
        """Obtener datos de Google Sheets"""
        if not self.service or not self.sheets_id:
            logger.error("Servicio de Google Sheets no disponible")
            return []
        
        try:
            # Obtener datos de la hoja
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheets_id,
                range=f'{sheet_name}!A:Z'  # Obtener todas las columnas
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                logger.warning(f"No se encontraron datos en la hoja {sheet_name}")
                return []
            
            # Convertir a lista de diccionarios
            headers = values[0]
            data = []
            
            for row in values[1:]:
                # Asegurar que la fila tenga el mismo número de columnas que los headers
                while len(row) < len(headers):
                    row.append('')
                
                # Crear diccionario
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ''
                
                data.append(row_dict)
            
            logger.info(f"Obtenidos {len(data)} registros de {sheet_name}")
            return data
            
        except HttpError as e:
            logger.error(f"Error HTTP al obtener datos de {sheet_name}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error inesperado al obtener datos de {sheet_name}: {e}")
            return []
    
    def _is_cache_valid(self, sheet_name: str) -> bool:
        """Verificar si el caché es válido"""
        if sheet_name not in self._cache_timestamps:
            return False
        
        import time
        current_time = time.time()
        cache_time = self._cache_timestamps[sheet_name]
        
        return (current_time - cache_time) < self._cache_duration
    
    def _update_cache(self, sheet_name: str, data: List[Dict]):
        """Actualizar caché"""
        import time
        self._cache[sheet_name] = data
        self._cache_timestamps[sheet_name] = time.time()
    
    def clear_cache(self, sheet_name: Optional[str] = None):
        """Limpiar caché"""
        if sheet_name:
            self._cache.pop(sheet_name, None)
            self._cache_timestamps.pop(sheet_name, None)
            logger.info(f"Caché limpiado para {sheet_name}")
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
            logger.info("Caché completamente limpiado")
    
    def get_available_sheets(self) -> List[str]:
        """Obtener lista de hojas disponibles"""
        if not self.service or not self.sheets_id:
            return []
        
        try:
            result = self.service.spreadsheets().get(
                spreadsheetId=self.sheets_id
            ).execute()
            
            sheets = result.get('sheets', [])
            sheet_names = [sheet['properties']['title'] for sheet in sheets]
            
            return sheet_names
            
        except Exception as e:
            logger.error(f"Error al obtener hojas disponibles: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Probar conexión con Google Sheets"""
        try:
            if not self.service or not self.sheets_id:
                return False
            
            # Intentar obtener metadatos del spreadsheet
            result = self.service.spreadsheets().get(
                spreadsheetId=self.sheets_id
            ).execute()
            
            title = result.get('properties', {}).get('title', '')
            logger.info(f"Conexión exitosa con spreadsheet: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error al probar conexión: {e}")
            return False 