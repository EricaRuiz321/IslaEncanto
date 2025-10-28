#!/usr/bin/env python3
"""
Script para añadir objetos de prueba al inventario
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.extensions import db
from models.objetoinventario import ObjetoInventario
from models.inventariodiario import InventarioDiario  # Importar para las relaciones
from models.inventarioresumen import InventarioResumen  # Importar para las relaciones
from models.nuevahabitacion import NuevaHabitacion  # Importar para las relaciones
from config import Config
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def add_sample_objects():
    """Añadir objetos de prueba si no existen"""
    app = create_app()
    
    with app.app_context():
        # Lista de objetos de prueba
        objetos_prueba = [
            {"nombre": "Secador de pelo", "categoria": "electrodomesticos", "descripcion": "Secador de pelo para huéspedes"},
            {"nombre": "Mini bar", "categoria": "amenidades", "descripcion": "Pequeño refrigerador con bebidas"},
            {"nombre": "Plancha", "categoria": "electrodomesticos", "descripcion": "Plancha para ropa"},
            {"nombre": "Toallas", "categoria": "textiles", "descripcion": "Juego de toallas"},
            {"nombre": "Televisor", "categoria": "electrodomesticos", "descripcion": "Smart TV"},
            {"nombre": "Aire acondicionado", "categoria": "electrodomesticos", "descripcion": "Sistema de climatización"},
            {"nombre": "Caja fuerte", "categoria": "seguridad", "descripcion": "Caja fuerte para valuables"},
            {"nombre": "Jabón", "categoria": "amenidades", "descripcion": "Jabón de tocador"},
        ]
        
        objetos_creados = 0
        
        for obj_data in objetos_prueba:
            # Verificar si ya existe
            existe = ObjetoInventario.query.filter_by(nombre=obj_data["nombre"]).first()
            
            if not existe:
                objeto = ObjetoInventario(
                    nombre=obj_data["nombre"],
                    categoria=obj_data["categoria"],
                    descripcion=obj_data["descripcion"],
                    activo=True
                )
                db.session.add(objeto)
                objetos_creados += 1
                print(f"✅ Creado: {obj_data['nombre']}")
            else:
                if not existe.activo:
                    existe.activo = True
                    db.session.add(existe)
                    print(f"🔄 Reactivado: {obj_data['nombre']}")
                else:
                    print(f"ℹ️  Ya existe: {obj_data['nombre']}")
        
        if objetos_creados > 0:
            db.session.commit()
            print(f"\n✅ Se crearon {objetos_creados} objetos nuevos")
        
        # Mostrar total de objetos activos
        total_activos = ObjetoInventario.query.filter_by(activo=True).count()
        print(f"📊 Total de objetos activos: {total_activos}")
        
        print("\n🎉 Los objetos ya están disponibles en el formulario de nueva habitación!")

if __name__ == "__main__":
    add_sample_objects()