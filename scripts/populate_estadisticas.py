#!/usr/bin/env python3
"""
Script para poblar datos de estadísticas de los últimos 7 días
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from config import Config
from utils.extensions import db
from models.estadisticasgenerales import EstadisticasGenerales
from datetime import date, timedelta
import random

# Crear app Flask simple
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    print("Poblando estadísticas de los últimos 7 días...")
    
    # Crear nuevas estadísticas con datos de prueba
    for i in range(6, -1, -1):  # De hace 6 días hasta hoy
        dia = date.today() - timedelta(days=i)
        
        # Buscar o crear registro existente
        estadistica = EstadisticasGenerales.query.filter_by(fecha=dia).first()
        
        # Generar datos aleatorios pero realistas
        base_huespedes = 10 + i * 2  # Crecimiento gradual
        base_usuarios = 5 + i
        
        total_huespedes = base_huespedes + random.randint(-3, 5)
        usuarios_registrados = base_usuarios + random.randint(-2, 3)
        check_out_hoy = random.randint(0, 4)
        
        if estadistica:
            # Actualizar registro existente
            estadistica.total_huespedes = total_huespedes
            estadistica.usuarios_registrados = usuarios_registrados
            estadistica.check_out_hoy = check_out_hoy
            print(f"Actualizado: {dia} - Huéspedes: {total_huespedes}, Usuarios: {usuarios_registrados}")
        else:
            # Crear nuevo registro
            estadistica = EstadisticasGenerales(
                fecha=dia,
                total_huespedes=total_huespedes,
                usuarios_registrados=usuarios_registrados,
                check_out_hoy=check_out_hoy
            )
            db.session.add(estadistica)
            print(f"Añadido: {dia} - Huéspedes: {total_huespedes}, Usuarios: {usuarios_registrados}")
    
    db.session.commit()
    print("✅ Estadísticas pobladas correctamente!")
    
    # Verificar que se crearon correctamente
    print("\nVerificando datos creados:")
    for i in range(6, -1, -1):
        dia = date.today() - timedelta(days=i)
        registro = EstadisticasGenerales.query.filter_by(fecha=dia).first()
        if registro:
            print(f"{dia}: H={registro.total_huespedes}, U={registro.usuarios_registrados}")
        else:
            print(f"{dia}: No encontrado")