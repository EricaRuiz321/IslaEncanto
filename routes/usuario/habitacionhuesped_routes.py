from flask import Blueprint, render_template, request, redirect, url_for
from models.habitacionhuesped import HabitacionHuesped
from models.nuevahabitacion import NuevaHabitacion
from utils.extensions import db
from datetime import date

habitacionHuesped_bp = Blueprint('habitacionHuesped', __name__)


@habitacionHuesped_bp.route('/hospedaje_usuario')
def hospedaje_usuario():
    habitaciones = HabitacionHuesped.query.all()
    return render_template('usuario/hospedaje_usuario.html', habitaciones=habitaciones, current_date=date.today().strftime("%Y-%m-%d"))


@habitacionHuesped_bp.route('/reservar_habitacion', methods=['POST'])
def reservar_habitacion():
    habitacion_id = request.form.get("habitacion_id")
    nombre = request.form.get("nombre")
    precio = request.form.get("precio")
    cantidad_personas = request.form.get("cantidad_personas")
    check_in = request.form.get("check_in") or date.today()
    check_out = request.form.get("check_out")

    # Guardar la reserva en habitacionHuesped
    reserva = HabitacionHuesped(
        nombre=nombre,
        precio=precio,
        cantidad_personas=cantidad_personas,
        check_in=check_in,
        check_out=check_out
    )
    
    db.session.add(reserva)
    
    # Cambiar estado de la habitación a "Ocupada"
    habitacion = NuevaHabitacion.query.get(habitacion_id)
    if habitacion:
        habitacion.estado = "Ocupada"
        
    db.session.commit()

    return redirect(url_for('habitacionHuesped.hospedaje_usuario'))
