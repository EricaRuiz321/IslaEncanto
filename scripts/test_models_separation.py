#!/usr/bin/env python3
"""
Script para verificar que los modelos separados funcionen correctamente
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.extensions import db
from config import Config
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def test_imports():
    """Probar que todas las importaciones funcionen"""
    app = create_app()
    
    with app.app_context():
        try:
            # Probar importaciones individuales
            from models.objetoinventario import ObjetoInventario
            from models.inventariodiario import InventarioDiario
            from models.inventarioresumen import InventarioResumen
            
            print("✅ Importaciones individuales funcionando")
            
            print("✅ Modelos separados funcionando correctamente")
            
            # Probar consultas
            objetos_count = ObjetoInventario.query.count()
            print(f"✅ Objetos en base de datos: {objetos_count}")
            
            # Probar relaciones
            if objetos_count > 0:
                primer_objeto = ObjetoInventario.query.first()
                print(f"✅ Primer objeto: {primer_objeto.nombre}")
                print(f"✅ Inventarios relacionados: {len(primer_objeto.inventarios)}")
            
            print("\n🎉 Todos los tests pasaron correctamente!")
            print("📁 Estructura de modelos separados funcionando")
            
        except Exception as e:
            print(f"❌ Error en los tests: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_imports()