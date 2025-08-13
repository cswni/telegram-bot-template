#!/usr/bin/env python3
"""
Script de prueba para verificar la conectividad con Google Sheets
"""

import os
import sys
from dotenv import load_dotenv
from utils.gsheets import GoogleSheetsManager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_sheets():
    """Probar la conectividad con Google Sheets"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar variables requeridas
    sheets_id = os.getenv('GOOGLE_SHEETS_ID')
    credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    
    if not sheets_id:
        print("❌ Error: GOOGLE_SHEETS_ID no está configurado en el archivo .env")
        return False
    
    if not os.path.exists(credentials_file):
        print(f"❌ Error: No se encontró el archivo {credentials_file}")
        print("   Asegúrate de haber descargado el archivo credentials.json desde Google Cloud Console")
        return False
    
    print("🔍 Iniciando prueba de conectividad con Google Sheets...")
    print(f"📊 ID de la hoja: {sheets_id}")
    print(f"🔑 Archivo de credenciales: {credentials_file}")
    print()
    
    try:
        # Crear instancia del manager (usa variables de entorno)
        sheets_manager = GoogleSheetsManager()
        
        # Probar conexión
        print("🔄 Probando conexión...")
        if sheets_manager.test_connection():
            print("✅ Conexión exitosa con Google Sheets")
        else:
            print("❌ Error al conectar con Google Sheets")
            return False
        
        # Obtener hojas disponibles
        print("📋 Obteniendo hojas disponibles...")
        available_sheets = sheets_manager.get_available_sheets()
        print(f"✅ Hojas encontradas: {', '.join(available_sheets)}")
        
        # Probar obtener datos de cada hoja
        expected_sheets = ['carreras', 'calendario', 'pagos', 'eventos', 'admision', 'contactos']
        
        for sheet_name in expected_sheets:
            print(f"\n📊 Probando hoja '{sheet_name}'...")
            try:
                data = sheets_manager.get_sheet_data_sync(sheet_name)
                if data:
                    print(f"✅ {sheet_name}: {len(data)} registros encontrados")
                    if len(data) > 0:
                        print(f"   Columnas: {list(data[0].keys())}")
                else:
                    print(f"⚠️  {sheet_name}: No hay datos")
            except Exception as e:
                print(f"❌ {sheet_name}: Error - {e}")
        
        print("\n🎉 ¡Prueba completada!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBA DE CONECTIVIDAD - GOOGLE SHEETS")
    print("=" * 50)
    
    success = test_google_sheets()
    
    if success:
        print("\n✅ Todas las pruebas pasaron correctamente")
        print("   Tu configuración de Google Sheets está funcionando")
    else:
        print("\n❌ Algunas pruebas fallaron")
        print("   Revisa tu configuración y vuelve a intentar")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main()) 