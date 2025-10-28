#!/usr/bin/env python3
"""
Script para corregir habitaciones con precio nulo
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

def fix_habitacion_precios():
    """Corregir habitaciones con precio nulo"""
    app = create_app()
    
    with app.app_context():
        # Buscar habitaciones con precio nulo usando SQL directo
        result = db.session.execute(text("""
            SELECT id, nombre, precio, cupo_personas 
            FROM nuevaHabitacion 
            WHERE precio IS NULL OR precio = 0
        """))
        
        habitaciones_sin_precio = result.fetchall()
        
        print(f"Encontradas {len(habitaciones_sin_precio)} habitaciones sin precio o con precio 0")
        
        for habitacion in habitaciones_sin_precio:
            print(f"Corrigiendo habitación: {habitacion.nombre} (ID: {habitacion.id})")
            print(f"  Precio actual: {habitacion.precio}")
            
            # Asignar precio por defecto basado en el cupo de personas
            if habitacion.cupo_personas <= 2:
                precio_defecto = 150000  # Habitación sencilla/doble
            elif habitacion.cupo_personas <= 4:
                precio_defecto = 200000  # Habitación familiar
            else:
                precio_defecto = 250000  # Suite o habitación grande
                
            print(f"  Nuevo precio: {precio_defecto}")
            
            # Actualizar usando SQL directo
            db.session.execute(text("""
                UPDATE nuevaHabitacion 
                SET precio = :precio 
                WHERE id = :id
            """), {"precio": precio_defecto, "id": habitacion.id})
        
        if habitaciones_sin_precio:
            db.session.commit()
            print(f"\n✅ Se corrigieron {len(habitaciones_sin_precio)} habitaciones")
        else:
            print("✅ Todas las habitaciones ya tienen precio asignado")

if __name__ == "__main__":
    fix_habitacion_precios()