#!/usr/bin/env python3
"""
Script para corregir registros de InventarioResumen con valores nulos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.extensions import db
from config import Config
from flask import Flask
from sqlalchemy import text

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def fix_inventario_resumen():
    """Corregir registros de InventarioResumen con valores nulos"""
    app = create_app()
    
    with app.app_context():
        # Buscar registros con campos nulos
        result = db.session.execute(text("""
            SELECT id, fecha_inventario, porcentaje_completado, total_habitaciones, 
                   total_objetos_revisados, objetos_completos, objetos_faltantes, objetos_pendientes
            FROM inventario_resumen 
            WHERE porcentaje_completado IS NULL 
               OR total_habitaciones IS NULL
               OR total_objetos_revisados IS NULL
               OR objetos_completos IS NULL
               OR objetos_faltantes IS NULL
               OR objetos_pendientes IS NULL
        """))
        
        registros_nulos = result.fetchall()
        
        print(f"Encontrados {len(registros_nulos)} registros con valores nulos")
        
        for registro in registros_nulos:
            print(f"Corrigiendo registro ID: {registro.id} - Fecha: {registro.fecha_inventario}")
            
            # Actualizar usando SQL directo
            db.session.execute(text("""
                UPDATE inventario_resumen 
                SET porcentaje_completado = COALESCE(porcentaje_completado, 0.0),
                    total_habitaciones = COALESCE(total_habitaciones, 0),
                    total_objetos_revisados = COALESCE(total_objetos_revisados, 0),
                    objetos_completos = COALESCE(objetos_completos, 0),
                    objetos_faltantes = COALESCE(objetos_faltantes, 0),
                    objetos_pendientes = COALESCE(objetos_pendientes, 0)
                WHERE id = :id
            """), {"id": registro.id})
        
        if registros_nulos:
            db.session.commit()
            print(f"\n✅ Se corrigieron {len(registros_nulos)} registros")
        else:
            print("✅ Todos los registros ya tienen valores válidos")

if __name__ == "__main__":
    fix_inventario_resumen()